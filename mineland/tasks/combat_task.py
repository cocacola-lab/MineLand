from typing import Optional

from mineland.sim.data.task_info import TaskInfo

from .base_task import BaseTask
from .utils import *

class CombatTask(BaseTask):
    '''Agent(s) need
    '''

    def __init__(
        self,
        *,
        target: str,
        num_of_target: int,
        goal:str, 
        initial_inventory: dict = {},
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.target = target
        self.num_of_target = num_of_target
        self.initial_inventory = initial_inventory
        self.goal = goal
        self.has_defeated = 0
        self.is_alive = [True for _ in range(self.agents_count)]
        
        print(f'{self.agents_count} Agent(s) need to defeat {self.num_of_target} x {self.target} ')

    def reset(self):
        obs = self.env.reset()

        self.server_manager.execute('difficulty normal')

        # Give tools to agents
        # if self.tool is not None:
        #     self.server_manager.execute(f"give @a minecraft:{self.tool} {self.num_of_tool}")
        for tool, number in self.initial_inventory.items() :
            self.server_manager.execute(f"give @a minecraft:{tool} {number}")

        # Get position of agents
        pos = [obs[0]['location_stats']['pos'][0], obs[0]['location_stats']['pos'][1], obs[0]['location_stats']['pos'][2]]
        def pos_to_string(pos):
            return f"{pos[0]} {pos[1]} {pos[2]}"

        # Set compass of agents
        self.server_manager.execute(f"tp {obs[0]['name']} {pos_to_string(pos)} 0 0")
        for i in range(1, self.agents_count):
            pos_i = pos.copy()
            pos_i[0] += i
            self.server_manager.execute(f"tp {obs[i]['name']} {pos_to_string(pos_i)} 0 0")

        # Summon target mobs
        pos[2] += 5
        for i in range(self.num_of_target):
            pos_i = pos.copy()
            pos_i[0] += i
            self.server_manager.execute(f"summon {self.target} {pos_to_string(pos_i)} " + "{CustomName:\"\\\"" + f"{self.target} {i}/{self.num_of_target}" + "\\\"\"}")
        
        return obs
    
    def step(self, action):
        obs, code_info, events, done, task_info = self.env.step(action)

        # Event based judgement
        for i in range(len(obs)):
            for event in events[i]:
                if event['type'] == 'death':
                    self.is_alive[i] = False
                    print(f'Agent#{obs[i]["name"]} died.')
                elif i == 0 and event['type'] == 'entityDead' and event['entity_name'] == self.target:
                    self.has_defeated += 1
                    print(f'Agent(s) defeated a(n) {self.target}.')

        task_info = TaskInfo(
            task_id=self.task_id,
            is_success=False,
            is_failed=False,
            goal=f'{self.goal}.\n'
                #  + f'{self.agents_count} Agent(s) need to defeat {self.num_of_target} x {self.target} ' + '\n'
                 + f'Agent(s) have defeated {self.has_defeated}, {self.num_of_target - self.has_defeated} more to go.',
            guidance="TODO",

            target=obs[0].target_entities,
        )

        if self.__is_success():
            task_info.is_success = True
            done = True
        elif self.__is_failed():
            task_info.is_failed = True
            done = True
        else:
            done = False

        return obs, code_info, events, done, task_info
    
    def __is_success(self):
        return self.has_defeated >= self.num_of_target
    
    def __is_failed(self):
        return all(not alive for alive in self.is_alive)
        
