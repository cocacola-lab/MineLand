from typing import Any, Dict, List

class TaskInfo:
    '''The information of the task.
    '''
    
    def __init__(
            self,
            *,
            task_id: str,
            is_success: bool,
            is_failed: bool,
            goal: str,
            guidance: str,
            score: float = 0,
            local_score: float = 0,
            global_score: float = 0,
            mode: str = 'cooperative',
            target: List[Dict[str, Any]] = None,
    ):
        local_vars = locals()
        for name, value in local_vars.items():
            if name != "self":
                setattr(self, name, value)
    
    def __str__(self) -> str:
        result = "TaskInfo (\n"
        for name, value in self.__dict__.items():
            result += f"    {name}: {value}\n"
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