'''
associative memory
'''

from .memory_library import MemoryNode
from ..prompt_template import load_prompt
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import SystemMessagePromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

class ShorttermPlan(BaseModel):
    short_term_plan: str = Field(description="short_term_plan")
    reasoning: str = Field(description="reasoning")
    critic_info: str = Field(description="critic_info")

class SpecialEventInfo(BaseModel):
    handling: str = Field(description="handling")
    reasoning: str = Field(description="reasoning")

class AssociativeMemory:
    def __init__(self,
                #  model_name = 'gpt-4-vision-preview',
                 model_name = 'gpt-4-1106-preview',
                 max_tokens = 1024,
                 temperature = 0,
                 save_path = "./save",
                 personality = "None"):
        self.personality = personality
        self.environment = set()
        self.events = set()
        self.chat = set()
        self.skills = set()
        self.long_term_plan = None
        self.last_short_term_plan = None
        self.short_term_plan = None
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.save_path = save_path

        
        model = ChatOpenAI(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        parser = JsonOutputParser(pydantic_object=ShorttermPlan)
        self.chain = model | parser

        model = ChatOpenAI(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        parser = JsonOutputParser(pydantic_object=SpecialEventInfo)
        self.special_event_chain = model | parser

    def render_system_message(self):
        prompt = load_prompt("generate_short_term_plan")
        return SystemMessage(content=prompt)

    def render_human_message(self, obs, task_info, recent_chat):
        content = []
        text = ""
        text += f"Personality: {self.personality} \n"
        if task_info is None:
            task_info = "None"
        text += f"Task information: {task_info}\n"
        text += f"long-term plan: {self.long_term_plan}\n"
        text += f"last {len(self.last_short_term_plan)} short-term plan:\n"
        for plan in self.last_short_term_plan:
            text += f"{plan}\n"


        current_event = ""
        current_chat = ""
        events = obs["event"]
        for event in events:
            event_type = event["type"]
            event_message = event["message"]
            if event_type == "chat":
                current_chat += f"{event_message}\n"
            else:
                current_event += f"{event_message}\n"
        if current_event == "":
            current_event = "None"
        text += f"Current Event: {current_event}\n"
        if current_chat == "":
            current_chat = "None"
        text += f"Current Chat: {current_chat}\n"


        relevant_events = ""
        for event in self.events:
            event : MemoryNode
            relevant_events += event.description + "\n"
        if relevant_events == "":
            relevant_events = "None"
        text += f"Relevant Event: {relevant_events}\n"


        recent_chat_text = ""
        if recent_chat is not None:
            for chat in recent_chat:
                recent_chat_text += f"{chat}\n"
        if recent_chat_text == "":
            recent_chat_text = "None"
        text += f"Recent Chat: {recent_chat_text}\n"


        relevant_chat = ""
        for chat in self.chat:
            chat : MemoryNode
            relevant_chat += chat.description + "\n"
        if relevant_chat == "":
            relevant_chat = "None"
        text += f"Relevant Chat: {relevant_chat}\n"

        text += f"Observation: {obs}\n"
    
        # relevant_skills = ""
        # for skill in self.skills:
        #     skill : MemoryNode
        #     relevant_skills += skill.description + "\n"
        # if relevant_skills == "":
        #     relevant_skills = "None"
        # text += f"Relevant Skill: {relevant_skills}\n"


        relevant_environment = ""
        for environment in self.environment:
            environment : MemoryNode
            relevant_environment += environment.description + "\n"
        if relevant_environment == "":
            relevant_environment = "None"
        text += f"Relevant Environment: {relevant_environment}\n"


        content.append({"type": "text", "text": text})

        if self.model_name == 'gpt-4-vision-preview':
            try:
                image_base64 = obs["rgb_base64"]
                if image_base64 != "":
                    content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "auto",
                                },
                            })
            except:
                print("No image in observation")
                pass
        
        human_message = HumanMessage(content=content)
        return human_message


    def plan(self, obs, task_info, retrieved, verbose = False):
        
        # 1. Store the retrieved information
        self.last_short_term_plan = retrieved["short_term_plan"]
        self.long_term_plan = retrieved["long_term_plan"]
        
        for event_desc, rel_ctx in retrieved.items():
            if event_desc not in ["long_term_plan", "short_term_plan", "recent_chat"]:
                for ctx_type, ctx in rel_ctx.items():
                    if ctx_type == "environment":
                        self.environment.update(ctx)
                    if ctx_type == "event":
                        self.events.update(ctx)
                    if ctx_type == "chat":
                        self.chat.update(ctx)
                    # if ctx_type == "skill":
                    #     self.skills.update(ctx)

        # 2. Short term plan
        system_message = self.render_system_message()
        human_message = self.render_human_message(obs, task_info, retrieved["recent_chat"])

        # print("human_message: ", human_message)

        messages = [system_message, human_message]

        self.short_term_plan = self.chain.invoke(messages)

        if verbose:
            # human_message.pretty_print()
            print(f"\033[31m****Short-term planner****\n{self.short_term_plan}\033[0m")
            with open(f"{self.save_path}/log.txt", "a+") as f:
                f.write(f"****Short-term planner****\n{self.short_term_plan}\n")

        return self.short_term_plan
    
    def reflect(self):
        pass

    def render_special_event_human_message(self, obs, task_info, code_info):
        content = []
        text = ""
        text += f"Personality: {self.personality} \n"
        if task_info is None:
            task_info = "None"
        text += f"Task information: {task_info}\n"
        text += f"long-term plan: {self.long_term_plan}\n"

        if self.last_short_term_plan is None:
            text += f"last short-term plan: None\n"
        else:
            text += f"last {len(self.last_short_term_plan)} short-term plan:\n"
            for plan in self.last_short_term_plan:
                text += f"{plan}\n"


        current_event = ""
        current_chat = ""
        events = obs["event"]
        for event in events:
            event_type = event["type"]
            event_message = event["message"]
            print(event_type, event_message)
            if event_type == "chat":
                current_chat += f"{event_message}\n"
            else:
                current_event += f"{event_message}\n"
        if current_event == "":
            current_event = "None"
        text += f"Current Event: {current_event}\n"
        if current_chat == "":
            current_chat = "None"
        text += f"Current Chat: {current_chat}\n"

        relevant_events = ""
        for event in self.events:
            event : MemoryNode
            relevant_events += event.description + "\n"
        if relevant_events == "":
            relevant_events = "None"
        text += f"Relevant Event: {relevant_events}\n"

        relevant_chat = ""
        for chat in self.chat:
            chat : MemoryNode
            relevant_chat += chat.description + "\n"
        if relevant_chat == "":
            relevant_chat = "None"
        text += f"Relevant Chat: {relevant_chat}\n"

        text += f"Observation: {obs}\n"

        if code_info is not None:
            text += f"Code Info: {code_info}\n"


        content.append({"type": "text", "text": text})

        if self.model_name == 'gpt-4-vision-preview':
            try:
                image_base64 = obs["rgb_base64"]
                if image_base64 != "":
                    content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "auto",
                                },
                            })
            except:
                print("No image in observation")
                pass
        
        human_message = HumanMessage(content=content)
        return human_message



    def special_event_check(self, obs, task_info, code_info):
        system_message_prompt = load_prompt("special_event_check")
        system_message = SystemMessage(content=system_message_prompt)
        human_message = self.render_special_event_human_message(obs, task_info, code_info)

        messages = [system_message, human_message]

        special_event_info = self.special_event_chain.invoke(messages)

        return special_event_info
        
        
