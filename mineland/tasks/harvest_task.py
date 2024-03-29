from typing import Optional

from mineland.sim.data.task_info import TaskInfo

from .base_task import BaseTask
from .utils import *

class HarvestTask(BaseTask):
    def __init__(
        self,
        *,
        target_item: str,
        num_of_target_item: int,
        initial_inventory: dict = {},
        mode: str = 'cooperative',
        goal: str,
        guidance: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.agents_count = kwargs['agents_count']
        self.agents_config = kwargs['agents_config']
        self.target_item = target_item
        self.num_of_target_item = num_of_target_item
        self.has_gotten_last = [0] * self.agents_count
        self.initial_inventory = initial_inventory
        self.goal = goal
        self.guidance = guidance
        self.mode = mode
        print(f'{self.agents_count} Agent(s) need to harvest {self.num_of_target_item} x {self.target_item}')

    def reset(self):
        obs = self.env.reset()

        # Give tools to agents
        # if self.tool is not None:
        #     self.server_manager.execute(f"give @a minecraft:{self.tool} {self.num_of_tool}")
        for tool, number in self.initial_inventory.items() :
            self.server_manager.execute(f"give @a minecraft:{tool} {number}")
        return obs
    
    def step(self, action):
        obs, code_info, events, done, task_info = self.env.step(action)

        # cooperative mode
        if self.mode == 'cooperative':
            has_gotten = 0
            # for obs_s in obs: # obs_s means obs_single
            for i in range(self.agents_count):
                obs_s = obs[i]
                for j in range(len(obs_s.inventory['name'])):
                    if obs_s.inventory['name'][j] == self.target_item:
                        has_gotten += obs_s.inventory['quantity'][j]
            if has_gotten > self.has_gotten_last[0]:
                self.has_gotten_last = has_gotten
                print('Agent(s) got', has_gotten, 'x', '"' + self.target_item + '"')

        # competive mode 
        if self.mode == 'competitive':
            has_gotten = [0] * self.agents_count
            # for obs_s in obs: # obs_s means obs_single
            for i in range(self.agents_count):
                obs_s = obs[i]
                for j in range(len(obs_s.inventory['name'])):
                    if obs_s.inventory['name'][j] == self.target_item:
                        has_gotten[i] += obs_s.inventory['quantity'][j]
            for i in range(self.agents_count):
                if has_gotten[i] > self.has_gotten_last[i]:
                    self.has_gotten_last[i] = has_gotten[i]
                    print(f'Agent {self.agents_config[i]["name"]} got', obs_s.inventory['quantity'][i], 'x', '"' + self.target_item + '"')

        task_info = TaskInfo(
            task_id=self.task_id,
            is_success=False,
            is_failed=False,
            # goal=f'{self.agents_count} Agent(s) need to harvest {self.num_of_target_item} x {self.target_item} ' + '\n'
            #      + f'Agent(s) have harvested {has_harvested}, {self.num_of_target_item - has_harvested} more to go.',
            goal=self.goal,
            guidance=self.guidance,
            mode = self.mode,
        )

        
        if self.__is_success(has_gotten):
            task_info.is_success = True
            done = True
        else:
            done = False
        if done :
            self.print_success_information(has_gotten)
        
        return obs, code_info, events, done, task_info
    
    def print_success_information(self, has_gotten) :
        if self.mode == 'cooperative' :
            print("TASK ACCOMPLISHED!")
        if self.mode == 'competitive' :
            print("TASK ACCOMPLISHED!")
            winner = []
            for i in range(self.agents_count) :
                if has_gotten[i] >= self.num_of_target_item:
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

    def __is_success(self, has_gotten):
        if self.mode == 'cooperative' :
            return has_gotten >= self.num_of_target_item
        for i in range(self.agents_count) :
            if has_gotten[i] >= self.num_of_target_item:
                return True
        return False
