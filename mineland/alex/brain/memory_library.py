'''
Main memory library for the brain.
'''

from ..prompt_template import load_prompt
from .long_term_planner import LongtermPlanner
from .viewer import Viewer
from .skill_manager import SkillManager
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.vectorstores.chroma import Chroma

class MemoryNode:
    def __init__(self, 
                 node_id,
                 node_count, 
                 node_type, 
                 created, 
                 description):
        self.node_id = node_id
        self.node_count = node_count
        self.node_type = node_type

        self.created = created
        self.last_accessed = self.created

        self.description = description

class MemoryLibrary:
    def __init__(self, 
                 chat_retrieve_limit = 5,
                 event_retrieve_limit = 2,
                 environment_retrieve_limit = 2,
                 skill_retrieve_limit = 5,
                 recent_chat_retrieve_limit = 7,
                 short_term_plan_retrieve_limit = 5,
                 model_name = 'gpt-4-turbo',
                 max_tokens = 256,
                 temperature = 0,
                 save_path:str = "memory_library",
                 load_path:str = "memory_library",
                 personality = "None",
                 bot_name = "Alex",
                 vision = True,
                 ):
        
        # =================== memory library ===================
        self.personality = personality
        self.save_path = save_path
        self.load_path = load_path
        self.id_to_node = dict()
        self.personality = None
        self.bot_name = bot_name
        self.vision = vision
        self.environment = []
        self.events = []
        self.chat = []
        self.skills = []
        self.long_term_plan = None
        self.short_term_plan = []

        # =================== conponents ===================
        self.long_term_planner = LongtermPlanner(model_name=model_name, 
                                                 max_tokens=max_tokens,
                                                 temperature=temperature,
                                                 personality=personality,
                                                 vision=vision)
        self.viewer = Viewer(model_name=model_name, 
                             max_tokens=max_tokens,
                             temperature=temperature)
        self.skill_manager = SkillManager(model_name=model_name,
                                          max_tokens=max_tokens,
                                          temperature=temperature)
        
        # =================== vectordb retrieve limit ===================
        self.chat_retrieve_limit = chat_retrieve_limit
        self.event_retrieve_limit = event_retrieve_limit
        self.environment_retrieve_limit = environment_retrieve_limit
        self.skill_retrieve_limit = skill_retrieve_limit
        self.recent_chat_retrieve_limit = recent_chat_retrieve_limit
        self.short_term_plan_retrieve_limit = short_term_plan_retrieve_limit

        # =================== vectordb ===================
        self.skill_vectordb = Chroma(
            collection_name="skill_vectordb",
            embedding_function=OpenAIEmbeddings(),
            persist_directory=f"{save_path}/memory/skill/vectordb",
        )

        self.chat_vectordb = Chroma(
            collection_name="chat_vectordb",
            embedding_function=OpenAIEmbeddings(),
            persist_directory=f"{save_path}/memory/chat/vectordb",
        )

        self.events_vectordb = Chroma(
            collection_name="events_vectordb",
            embedding_function=OpenAIEmbeddings(),
            persist_directory=f"{save_path}/memory/events/vectordb",
        )

        self.environment_vectordb = Chroma(
            collection_name="environment_vectordb",
            embedding_function=OpenAIEmbeddings(),
            persist_directory=f"{save_path}/memory/environment/vectordb",
        )

        
        # print(f"chat vectordb counts: {self.chat_vectordb._collection.count()}")
        # print(f"skill vectordb counts: {self.skill_vectordb._collection.count()}")
        # print(f"events vectordb counts: {self.events_vectordb._collection.count()}")
        # print(f"environment vectordb counts: {self.environment_vectordb._collection.count()}")

    def perceive(self, obs, plan_is_success, critic_info, code_info, vision = False, verbose = False):
        '''
        Perceive the environment and store the information in the memory library.
        '''

        # ============= perceive Time Info =============
        tick = obs["tick"]
        time = obs["time"]
        day = obs["day"]

        # ============= perceive Events =============
        events = obs["event"]

        for event in events:
            event_type = event["type"]
            if event_type == "chat":
                event_message = event["message"]
                self.add_chat(tick, day, time, event_message)
            else:
                self.add_event(tick, day, time, event)
        
        # ============= perceive Environment =============

        if vision:
            self.add_env(tick, day, time, obs, vision=vision)


        # ============= perceive Critic Info =============
        if len(self.short_term_plan) > 0 and critic_info is not None:
            self.short_term_plan[0]["critic_info"] = critic_info


        # ============= perceive Skills =============
        if plan_is_success is True:
            self.add_skill(tick, day, time, code_info)

        if verbose:
            print(f"tick: {tick}\ntime: {time}\nday: {day}")
            print(f"id_to_node: {len(self.id_to_node)}")

            print(f"chat vectordb counts: {self.chat_vectordb._collection.count()}")
            print(f"skill vectordb counts: {self.skill_vectordb._collection.count()}")
            print(f"events vectordb counts: {self.events_vectordb._collection.count()}")
            print(f"environment vectordb counts: {self.environment_vectordb._collection.count()}")

            with open(f"{self.save_path}/log.txt", "a+") as f:
                f.write(f"chat vectordb counts: {self.chat_vectordb._collection.count()}\n")
                f.write(f"skill vectordb counts: {self.skill_vectordb._collection.count()}\n")
                f.write(f"events vectordb counts: {self.events_vectordb._collection.count()}\n")
                f.write(f"environment vectordb counts: {self.environment_vectordb._collection.count()}\n")

        
        # print(self.chat_vectordb._collection.get())
        pass

    
    def retrieve(self, obs, verbose = False):
        '''
        Retrieve information from the memory library.
        '''
        events = obs["event"]
        retrieved = {
            "long_term_plan": "",
            "short_term_plan": "",
        }
        
        retrieved["long_term_plan"] = self.retrieve_long_term_plan()
        retrieved["short_term_plan"] = self.short_term_plan[0:self.short_term_plan_retrieve_limit]

        # retrieve event related information
        for event in events:
            query = event["message"]
            if query.startswith(f"<{self.bot_name}>"):
                continue
            
            if verbose:
                print("query: " + query)

            if query not in retrieved.keys():
                retrieved[query] = dict()
                retrieved[query]["chat"] = set()
                retrieved[query]["environment"] = set()
                retrieved[query]["event"] = set()
                # retrieved[query]["skill"] = set()
            
            # retrieve chat
            chats = self.retrieve_chats(query, verbose=verbose)
            retrieved[query]["chat"].update(chats)

            # retrieve environment
            environments = self.retrieve_environments(query, verbose=verbose)
            retrieved[query]["environment"].update(environments)

            # retrieve event
            events = self.retrieve_events(query, verbose=verbose)
            retrieved[query]["event"].update(events)

            # retrieve skill
            # skills = self.retrieve_skills(query, verbose=verbose)
            # retrieved[query]["skill"].update(skills) 
        
        # retrieve recent chat history
        retrieved["recent_chat"] = self.chat[0:self.recent_chat_retrieve_limit]

        if verbose:
            print("----------------retrieved info ----------------------")
            print(f"long_term_plan: {retrieved['long_term_plan']}")
            print(f"last {len(retrieved['short_term_plan'])} short_term_plan:")
            for plan in retrieved["short_term_plan"]:
                print(plan)
            chat_logs = ", ".join([chat.description for chat in retrieved["recent_chat"]])
            print(f"recent_chat: {chat_logs}")
            for event_desc, rel_ctx in retrieved.items():
                if event_desc not in ["long_term_plan", "short_term_plan", "recent_chat"]:
                    print(f"retrieved: {event_desc}")
                    for ctx_type, ctx in rel_ctx.items():
                        print(f"ctx_type: {ctx_type}")
                        for node in ctx:
                            node : MemoryNode
                            print(f"node_id: {node.node_id}, node_count: {node.node_count}, node_type: {node.node_type}, description: {node.description}")
            print("-----------------------------------------------------\n")

            with open(f"{self.save_path}/log.txt", "a+") as f:
                f.write(f"----------------retrieved info ----------------------\n")
                f.write(f"long_term_plan: {retrieved['long_term_plan']}\n")
                f.write(f"last {len(retrieved['short_term_plan'])} short_term_plan:\n")
                for plan in retrieved["short_term_plan"]:
                    f.write(f"{plan}\n")
                chat_logs = ", ".join([chat.description for chat in retrieved["recent_chat"]])
                f.write(f"recent_chat: {chat_logs}\n")
                for event_desc, rel_ctx in retrieved.items():
                    if event_desc not in ["long_term_plan", "short_term_plan", "recent_chat"]:
                        f.write(f"retrieved: {event_desc}\n")
                        for ctx_type, ctx in rel_ctx.items():
                            f.write(f"ctx_type: {ctx_type}\n")
                            for node in ctx:
                                node : MemoryNode
                                f.write(f"node_id: {node.node_id}, node_count: {node.node_count}, node_type: {node.node_type}, description: {node.description}\n")
                f.write(f"-----------------------------------------------------\n")

        return retrieved

    def generate_long_term_plan(self, obs, task_info):
        if self.long_term_plan is None:
            self.long_term_plan = self.long_term_planner.plan(obs, task_info)
        return self.long_term_plan
    
    def add_env(self, tick, day, time, obs, vision:bool):

        node_count = len(self.id_to_node.keys()) + 1
        node_id = f"node_{str(node_count)}"
        node_type = "environment"
        created = tick
        pos = obs["location_stats"]["pos"]
        description = f"Day {day}, Time {time}: I am at {pos}"
        
        if vision:
            view_summary = self.viewer.summary(obs)
            view_summary = view_summary["image_summary"]
            description += f"I can see: {view_summary}"


        environment_node = MemoryNode(node_id, node_count, node_type, created, description)
        self.environment[0:0] = [environment_node]
        self.id_to_node[node_id] = environment_node

        self.environment_vectordb.add_texts(
            texts=[description],
            ids=[node_id],
            metadatas=[{"node_id": node_id}],
        )

        self.environment_vectordb.persist()
        

    def add_event(self, tick, day, time, event):
        node_count = len(self.id_to_node.keys()) + 1
        node_id = f"node_{str(node_count)}"
        node_type = "event"
        created = tick
        event_info = f"Day : {day}, Time :{time}, event type: {event['type']}, event message: {event['message']}"
        description = event_info
        event_node = MemoryNode(node_id, node_count, node_type, created, description)
        self.events[0:0] = [event_node]
        self.id_to_node[node_id] = event_node

        self.events_vectordb.add_texts(
            texts=[event_info],
            ids=[node_id],
            metadatas=[{"node_id": node_id}],
        )

        self.events_vectordb.persist()

    def add_chat(self, tick, day, time, chat):
        node_count = len(self.id_to_node.keys()) + 1
        node_id = f"node_{str(node_count)}"
        node_type = "chat"
        created = tick
        chat_info = f"Day {day}, Time {time}: {chat}"
        description = chat_info
        chat_node = MemoryNode(node_id, node_count, node_type, created, description)
        self.chat[0:0] = [chat_node]
        self.id_to_node[node_id] = chat_node

        self.chat_vectordb.add_texts(
            texts=[description],
            ids=[node_id],
            metadatas=[{"node_id": node_id}],
        )
        
        # print(f"chat vectordb counts: {self.chat_vectordb._collection.count()}")

        self.chat_vectordb.persist()

    def add_skill(self, tick, day, time, code_info):
        node_count = len(self.id_to_node.keys()) + 1
        node_id = f"node_{str(node_count)}"
        node_type = "skill"
        created = tick

        skill_info = self.skill_manager.generate_skill_info(code_info)
        skill_description = f"    // { skill_info['description']}"


        description = f"async function {skill_info['name']}(bot) {{\n{skill_description}\n}}"

        skill_node = MemoryNode(node_id, node_count, node_type, created, description)

        self.skills[0:0] = [skill_node]
        self.id_to_node[node_id] = skill_node

        self.skill_vectordb.add_texts(
            texts=[description],
            ids=[node_id],
            metadatas=[{"node_id": node_id}],
        )

        self.skill_vectordb.persist()
        pass

    def add_long_term_plan(self, long_term_plan):
        self.long_term_plan = long_term_plan
        pass

    def add_short_term_plan(self, short_term_plan, verbose = False):
        for plan in self.short_term_plan:
            if plan["short_term_plan"] == short_term_plan["short_term_plan"]:
                plan["critic_info"] = "do it later"
        self.short_term_plan[0:0] = [short_term_plan]

        if verbose:
            print("==========short-term plans==========")
            for i, plan in enumerate(self.short_term_plan):
                print(f"{i}: {plan}")
            print("====================================")
            with open(f"{self.save_path}/log.txt", "a+") as f:
                f.write("==========short-term plans==========\n")
                for i, plan in enumerate(self.short_term_plan):
                    f.write(f"{i}: {plan}\n")
                f.write("====================================\n")
        pass

    def retrieve_events(self, query, verbose = False):
        k = min(self.event_retrieve_limit, len(self.events))
        if k == 0:
            return []
        if verbose:
            print(f"\033[33mMemory Library retrieving for {k} events\033[0m")
        docs_and_scores = self.events_vectordb.similarity_search_with_score(query, k=k)
        if verbose:
            print(
                f"\033[33mMemory Library retrieved events: "
                f"{', '.join([doc.metadata['node_id'] for doc, _ in docs_and_scores])}\033[0m"
            )
        events = []
        for doc, _ in docs_and_scores:
            node = self.id_to_node[doc.metadata["node_id"]]
            events.append(node)

        return events

    def retrieve_chats(self, query, verbose = False):
        k = min(self.chat_retrieve_limit, len(self.chat))
        if k == 0:
            return []
        if verbose:
            print(f"\033[33mMemory Library retrieving for {k} chats\033[0m")
        docs_and_scores = self.chat_vectordb.similarity_search_with_score(query, k=k)
        if verbose:
            print(
                f"\033[33mMemory Library retrieved chats: "
                f"{', '.join([doc.metadata['node_id'] for doc, _ in docs_and_scores])}\033[0m"
            )
        chats = []
        for doc, _ in docs_and_scores:
            # print(doc.metadata["node_id"])
            node = self.id_to_node[doc.metadata["node_id"]]
            chats.append(node)

        return chats

    def retrieve_skills(self, query, verbose = False):
        k = min(self.skill_retrieve_limit, len(self.skills))
        if k == 0:
            return []
        if verbose:
            print(f"\033[33mMemory Library retrieving for {k} skills\033[0m")
        docs_and_scores = self.skill_vectordb.similarity_search_with_score(query, k=k)
        if verbose:
            print(
                f"\033[33mMemory Library retrieved skills: "
                f"{', '.join([doc.metadata['node_id'] for doc, _ in docs_and_scores])}\033[0m"
            )
        skills = []
        for doc, _ in docs_and_scores:
            node = self.id_to_node[doc.metadata["node_id"]]
            skills.append(node)
        return skills
    
    def retrieve_environments(self, query, verbose = False):
        k = min(self.environment_retrieve_limit, len(self.environment))
        if k == 0:
            return []
        if verbose:
            print(f"\033[33mMemory Library retrieving for {k} environment\033[0m")
        docs_and_scores = self.environment_vectordb.similarity_search_with_score(query, k=k)
        if verbose:
            print(
                f"\033[33mMemory Library retrieved environment: "
                f"{', '.join([doc.metadata['node_id'] for doc, _ in docs_and_scores])}\033[0m"
            )
        environment = []
        for doc, _ in docs_and_scores:
            node = self.id_to_node[doc.metadata["node_id"]]
            environment.append(node)

        return environment

    def retrieve_long_term_plan(self, verbose = False):
        if verbose:
            print(f"\033[33mMemory Library retrieving for long term plan\033[0m")
        if self.long_term_plan:
            return self.long_term_plan["long_term_plan"]
        else:
            return None

    def retrieve_latest_short_term_plan(self, verbose = False):
        if verbose:
            print(f"\033[33mMemory Library retrieving for short term plan\033[0m")
        if len(self.short_term_plan) == 0:
            return None
        return self.short_term_plan[0]

    def retrieve_latest_unfinished_short_term_plan(self, verbose = False):
        if verbose:
            print(f"\033[33mMemory Library retrieving for latest unfinished short term plan\033[0m")
        if len(self.short_term_plan) == 0:
            return None
        for plan in self.short_term_plan:
            if plan["critic_info"] == "unfinished" or plan["critic_info"] == "failed":
                return plan
        return self.short_term_plan[0]

        