from mineland.sim.data.task_info import TaskInfo

from .base_task import BaseTask
from .utils import *

class SurvivalTask(BaseTask):
    def __init__(
        self,
        *,
        survival_target_day: float,
        initial_inventory: dict,
        guidance: str,
        goal: str,
        mode: str = 'cooperative',
        **kwargs,
    ):
        self.agents_count = kwargs['agents_count']
        self.agents_config = kwargs['agents_config']
        self.survival_target_day = survival_target_day
        self.initial_inventory = initial_inventory
        self.guidance = guidance
        self.goal = goal
        self.mode = mode
        print(f'Agent(s) need to survive for {self.survival_target_day} days ({self.survival_target_day * 24000} ticks)')
        super().__init__(**kwargs)

    def reset(self):
        obs = self.env.reset()
        self.server_manager.execute('difficulty normal')
        if self.mode == 'cooperative' :
            self.start_tick = obs[0].age
        else :
            self.start_tick = [obs[0].age] * self.agents_count
        for tool, number in self.initial_inventory.items() :
            self.server_manager.execute(f"give @a minecraft:{tool} {number}")
        self.server_manager.execute(f"give @a minecraft:iron_sword 1")
        return obs
    
    def step(self, action):
        obs, code_info, events, done, task_info = self.env.step(action)
        
        if self.mode == 'cooperative':
            for event_per_bot in events:
                for event in event_per_bot:
                    if event['type'] == 'death':
                        self.start_tick = obs[0].age
                        print('Agent(s) died. Reset start_tick to', self.start_tick)
        else:
            for i in range(self.agents_count):
                event_per_bot = events[i]
                for event in event_per_bot:
                    if event['type'] == 'death':
                        self.start_tick[i] = obs[0].age
                        print(f'Agent {self.agents_config[i]["name"]} died. Reset his start_tick to', self.start_tick[i])
        # print('events: ', events)
        # print('start_tick: ', self.start_tick)

        task_info = TaskInfo(
            task_id=self.task_id,
            is_success=False,
            is_failed=False,
            # goal=f'Agent(s) need to survive for {self.survival_target_day} days ({self.survival_target_day * 24000} ticks)' + '\n' +
            #      f'Agent(s) have survived for {float((obs[0].age - self.start_tick) / 24000)} days ({obs[0].age - self.start_tick} ticks).',
            goal = 'None',
            guidance="None",
            mode=self.mode
        )
        if self.__is_success(self.start_tick, obs[0].age):
            task_info.is_success = True
            done = True
        else:
            done = False
        if done:
            self.print_success_information(self.start_tick, obs[0].age)
        return obs, code_info, events, done, task_info
    
    def print_success_information(self, start_tick, current_tick: int) :
        if self.mode == 'cooperative' :
            print("TASK ACCOMPLISHED!")
        if self.mode == 'competitive' :
            print("TASK ACCOMPLISHED!")
            winner = []
            for i in range(self.agents_count) :
                if current_tick - start_tick[i] >= self.survival_target_day * 24000:
                    winner.append(self.agents_config[i]["name"])
            s = 'Agent(s) '
            for i in range(len(winner)) :
                winner_name = winner[i]
                if i + 1 < len(winner):
                    s += f'{winner_name}, '
                else :
                    s += f'{winner_name} '
            s += 'win!'
            print(s)


    def __is_success(self, start_tick, current_tick: int):
        if self.mode == 'cooperative' and current_tick - start_tick >= self.survival_target_day * 24000:
            return True
        if self.mode == 'competitive' :
            for i in range(self.agents_count):
                if current_tick - start_tick[i] >= self.survival_target_day * 24000:
                    return True
        else:
            return False
        
