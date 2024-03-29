from mineland.sim.data.task_info import TaskInfo

from .base_task import BaseTask
from .utils import *

class PlaythroughTask(BaseTask):
    def __init__(
        self,
        mode: str = 'default',
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.target = 'ender_dragon'
        self.num_of_target = 1
        self.has_defeated = 0
        self.mode = mode
        print(f'{self.agents_count} Agent(s) need to defeat the ENDER DRAGON and beat the game!!!') 

    def reset(self):
        obs = self.env.reset()
        return obs
    
    def step(self, action):
        obs, code_info, events, done, task_info = self.env.step(action)

        # Event based judgement
        for i in range(len(obs)):
            for event in events[i]:
                if i == 0 and event['type'] == 'entityDead' and event['entity_name'] == self.target:
                    self.has_defeated += 1
                    print(f'Agent(s) defeated a(n) {self.target}!!!')

        task_info = TaskInfo(
            task_id=self.task_id,
            is_success=False,
            is_failed=False,
            goal=f'{self.agents_count} Agent(s) need to defeat the ENDER DRAGON and beat the game!!!',
            guidance="TODO",
            mode=self.mode
        )

        if self.__is_success():
            task_info.is_success = True
            print(f'Agent(s) have beaten the ENDER DRAGON! Amazing!')
            done = True
        else:
            done = False

        return obs, code_info, events, done, task_info
    
    def __is_success(self):
        return self.has_defeated >= self.num_of_target
