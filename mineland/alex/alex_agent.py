import time

from .self_check.self_check_agent import *
from .critic.critic_agent import *
from .brain.memory_library import *
from .brain.associative_memory import *
from .action.action_agent import *
from .. import Action

class Alex:
    def __init__(self,
                llm_model_name = "gpt-4-turbo",
                vlm_model_name = "gpt-4-turbo",
                max_tokens = 512,
                temperature = 0,
                save_path = "./storage",
                load_path = "./load",
                FAILED_TIMES_LIMIT = 3,
                bot_name = "Alex",
                personality = "None",
                vision = True,):
        
        self.personality = personality
        self.llm_model_name = llm_model_name
        self.vlm_model_name = vlm_model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.save_path = save_path + "/" + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        self.load_path = load_path
        self.vision = vision
        self.bot_name = bot_name
        self.FAILED_TIMES_LIMIT = FAILED_TIMES_LIMIT

        print(f"save_path: {self.save_path}")

        self.self_check_agent = SelfCheckAgent(FAILED_TIMES_LIMIT=self.FAILED_TIMES_LIMIT,
                                               save_path=self.save_path,)
        self.critic_agent = CriticAgent(FAILED_TIMES_LIMIT=self.FAILED_TIMES_LIMIT,
                                        mode="auto",
                                        model_name=self.vlm_model_name,
                                        max_tokens=self.max_tokens,
                                        temperature=self.temperature,
                                        save_path=self.save_path,
                                        vision=self.vision,)
        self.memory_library = MemoryLibrary(model_name=self.vlm_model_name,
                                            max_tokens=self.max_tokens,
                                            save_path=self.save_path,
                                            load_path=self.load_path,
                                            personality=self.personality,
                                            bot_name=self.bot_name,
                                            vision=self.vision,)
        self.associative_memory = AssociativeMemory(model_name=self.vlm_model_name,
                                                    max_tokens=self.max_tokens,
                                                    temperature=self.temperature,
                                                    save_path=self.save_path,
                                                    personality=self.personality,
                                                    vision=self.vision,)
        self.action_agent = ActionAgent(model_name=self.vlm_model_name,
                                        max_tokens=self.max_tokens * 3,
                                        temperature=self.temperature,
                                        save_path=self.save_path,)

    def self_check(self, obs, code_info = None, done = None, task_info = None):
        return self.self_check_agent.self_check(obs, code_info, done, task_info, associative_memory=self.associative_memory)

    def critic(self, obs, verbose = False):
        short_term_plan = self.memory_library.retrieve_latest_short_term_plan()
        return self.critic_agent.critic(short_term_plan, obs, verbose=verbose)

    def perceive(self, obs, plan_is_success, critic_info = None, code_info = None, vision = False, verbose = False):
        self.memory_library.perceive(obs, plan_is_success, critic_info, code_info, vision=vision, verbose=verbose)

    def retrieve(self, obs, verbose = False):
        retrieved = self.memory_library.retrieve(obs, verbose)
        return retrieved

    def plan(self, obs, task_info, retrieved, verbose = False):
        short_term_plan = self.associative_memory.plan(obs, task_info, retrieved, verbose=verbose)
        self.memory_library.add_short_term_plan(short_term_plan, verbose=verbose)
        return short_term_plan

    def execute(self, obs, description, code_info = None, critic_info = None, verbose = False):
        if description == "Code Unfinished":
            # return { "type": Action.RESUME, "code": ''}
            return Action(type=Action.RESUME, code='')
        short_term_plan = self.memory_library.retrieve_latest_short_term_plan()
        if description == "Code Failed" or description == "Code Error":
            return self.action_agent.retry(obs, short_term_plan, code_info, verbose=verbose)
        if description == "redo":
            return self.action_agent.redo(obs, short_term_plan, critic_info, verbose=verbose)
        return self.action_agent.execute(obs, short_term_plan, verbose=verbose)

    def run(self, obs, code_info = None, done = None, task_info = None, verbose = False):

        # 1. self check
        if verbose:
            print("==========self check==========")

        next_step, description = self.self_check(obs, code_info, done, task_info)

        ## if task is done
        if next_step is None:
            print(description)
            return None

        if verbose:
            print("next step after self check: " + next_step)
            print("description: " + description)
            print("==============================\n")
            if next_step != "action":
                with open(f"{self.save_path}/log.txt", "a+") as f:
                    f.write("==========self check==========\n")
                    f.write("next step after self check: " + next_step + "\n")
                    f.write("description: " + description + "\n")
                    f.write("==============================\n")
        
        # 2. critic
        plan_is_success = False
        critic_info = None
        if next_step == "critic":
            if verbose:
                print("==========critic==========")
                with open(f"{self.save_path}/log.txt", "a+") as f:
                    f.write("==========critic==========\n")

            next_step, plan_is_success, critic_info = self.critic(obs, verbose=verbose)

            if next_step == "action":
                description = "redo"

            if verbose:
                print("next step after critic: " + next_step)
                print("critic info: " + critic_info)
                print("==========================\n")
                with open(f"{self.save_path}/log.txt", "a+") as f:
                    f.write("next step after critic: " + next_step + "\n")
                    f.write("critic info: " + critic_info + "\n")
                    f.write("==========================\n")

        # 3. brain
                    
        if next_step == "action":
            self.perceive(obs, plan_is_success, critic_info=None, code_info=None, vision = False, verbose=False)

        if next_step == "brain":
            
            if verbose:
                print("==========brain==========")
                with open(f"{self.save_path}/log.txt", "a+") as f:
                    f.write("==========brain==========\n")
            
            if description == "Code Failed":
                critic_info = "action failed, maybe the plan is too difficult. please change to a easy plan."

            self.perceive(obs, plan_is_success, critic_info, code_info, vision = True, verbose=verbose)
            self.memory_library.generate_long_term_plan(obs, task_info)
            # print(long_term_plan)
            # long_term_plan = {'difficult': False, 'long_term_plan': 'Since no ultimate goal has been defined, a long-term plan is not necessary. To start setting your own goals, you might consider basic survival tasks such as building shelter, gathering resources like wood and stone, crafting tools, exploring to find a village, or starting a farm. These activities can serve as a foundation for whatever objectives you decide to pursue in your Minecraft adventure.'}
            # self.memory_library.add_long_term_plan(long_term_plan)
            retrieved = self.retrieve(obs, verbose=verbose)
            self.plan(obs, task_info, retrieved, verbose=verbose)

            next_step = "action"
            description = "execute the plan"

            if verbose:
                print("next step after brain: " + next_step)
                print("description: " + description)
                print("========================\n")
                with open(f"{self.save_path}/log.txt", "a+") as f:
                    f.write("next step after brain: " + next_step + "\n")
                    f.write("description: " + description + "\n")
                    f.write("========================\n")

        # 4. action
        if next_step == "action":
            if verbose:
                print("==========action==========")
                if description != "Code Unfinished":
                    with open(f"{self.save_path}/log.txt", "a+") as f:
                        f.write("==========action==========\n")

            act = self.execute(obs, 
                               description, 
                               code_info=code_info, 
                               critic_info=critic_info, 
                               verbose=verbose)


            if verbose:
                print("==========================\n")
                if description != "Code Unfinished":
                    with open(f"{self.save_path}/log.txt", "a+") as f:
                        f.write("==========================\n\n\n")
            
            return act