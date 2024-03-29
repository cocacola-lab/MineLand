from mineland.sim.data.task_info import TaskInfo

from .base_task import BaseTask
from .utils import *

class CreativeTask(BaseTask):
    def __init__(
        self,
        guidance: str,
        goal: str,
        initial_inventory: dict = {},
        mode: str = 'cooperative',
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.guidance = guidance,
        self.goal = goal,
        self.initial_inventory = initial_inventory
        self.mode = mode
        print(f'agent(s) need to do : {goal} \n ') 
        if guidance :
            print(f"guidance is : {guidance}")

    def reset(self):
        obs = self.env.reset()
        for tool, number in self.initial_inventory.items() :
            self.server_manager.execute(f"give @a minecraft:{tool} {number}")
        return obs
    def step(self, action):
        obs, code_info, events, done, task_info = self.env.step(action)

        task_info = TaskInfo(
            task_id=self.task_id,
            is_success=False,
            is_failed=False,
            goal=self.goal,
            guidance=self.guidance,
            mode=self.mode,
        )

        return obs, code_info, events, False, task_info
