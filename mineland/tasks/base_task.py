import gymnasium as gym

from ..sim import MineLand
from .utils import *

class BaseTask(gym.Wrapper):
    def __init__(
        self,
        *,
        task_id: str,
        **kwargs
    ):
        self.task_id = task_id
        env = MineLand(**kwargs)
        super().__init__(env)

    def reset(self):
        obs = self.env.reset()
        return obs

    def step(self, action):
        obs, code_info, event, done, task_info = self.env.step(action)
        return obs, code_info, event, done, task_info

    def render(self, mode='human'):
        return self.env.render(mode)

    def close(self):
        return self.env.close()

    def seed(self, seed=None):
        assert False, "Does not support seed."

    def __getattr__(self, name):
        return getattr(self.env, name)
