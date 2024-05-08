
import random

class LowLevelAction:
    def __init__(self):
        self.data = [0 for _ in range(8)]
        self.min = [0 for _ in range(8)]
        self.max = [2, 2, 3, 24, 24, 7, 243, 35] # -1 means wip
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        assert 0 <= key < 8, f"Key {key} is out of range, must be in [0, 7]"
        assert self.min[key] <= value <= self.max[key], f"Value {value} is out of range for key {key}, min: {self.min[key]}, max: {self.max[key]}"
        self.data[key] = value
    
    def __str__(self):
        return f'LowLevelAction({self.data})'
    
    def to_json(self):
        return str(self.data)
    
    @staticmethod
    def no_op(num_of_agents: int):
        return [LowLevelAction() for _ in range(num_of_agents)]

    @staticmethod
    def random_op(num_of_agents: int):
        actions = LowLevelAction.no_op(num_of_agents)
        for action in actions:
            for i in range(8):
                if action.max[i] == -1:
                    continue
                action[i] = random.randint(action.min[i], action.max[i])
        return actions