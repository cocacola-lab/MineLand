from enum import Enum
from typing import Dict

class EventType(Enum):
    CHAT = 0
    HURT = 1
    DEATH = 2

class Event:
    '''
    This class is used to represent events that occured in mineflayer bot.
    '''
    def __init__(
        self,
        type: str,
        message: str,
        tick: int,
    ):
        '''
        Construct a Event object.
        Args:
            type (str): The type of the event.
            message (str): The detailed message of the event.
        '''
        local_vars = locals()
        for name, value in local_vars.items():
            if name != "self":
                setattr(self, name, value)
    
    def __str__(self) -> str:
        result = "Event ("
        for name, value in self.__dict__.items():
            result += f" ({name}:{value}) "
        result += ")"
        return result
    
    def __getitem__(self, key):
        return getattr(self, key, None)

    @classmethod
    def from_json(cls, json):
        if json == {}:
            return None
        return cls(**json)
    
    @classmethod
    def from_json_list(cls, json_list):
        return [cls.from_json(json) for json in json_list]

    @classmethod
    def from_json_matrix(cls, json_matrix):
        return [cls.from_json_list(list) for list in json_matrix]
