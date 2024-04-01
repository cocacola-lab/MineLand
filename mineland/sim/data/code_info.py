from typing import Dict

class CodeInfo:
    '''This class is used to represent a code Info that occurred in mineflayer bot.

    Example:
        >>> obs, codeInfo, event = mindland.step(action=act)
        >>> print(codeInfo[0][code_error]['error_type']) 
        'TypeError'
        >>> print(codeInfo[0][code_error]['error_message'])
        Cannot read property 'property' of undefined

    '''
    
    def __init__(
            self,
            name: str,
            is_running: bool,
            is_ready: bool,
            code_error: Dict[str, str],
            last_code: str,
            code_tick: int,
    ):
        '''Construct a CodeInfo object.

        Args:
            name (str): The name of the bot.
            is_running (bool): Whether the bot is running a code.
            is_ready (bool): Whether the bot is ready to run a code.
            code_error (dict): The error information of the bot.
                error_type (str): The type of the error.
                error_message (str): The detailed message of the error.
                error_stack (str): The traceback of the error.

        Returns:
            None
        '''

        local_vars = locals()
        for name, value in local_vars.items():
            if name != "self":
                setattr(self, name, value)
    
    def __str__(self) -> str:
        result = "CodeInfo (\n"
        for name, value in self.__dict__.items():
            if name == "code_error":
                if value == {}: 
                    result += f"    {name}: None\n"
                    continue
                result += f"    {name}:" + " {\n"
                for err_key, err_value in value.items():
                    if err_key == "error_stack":
                        result += f"        {err_key}: "
                        for index, line in enumerate(err_value.split("\n")):
                            if index == 0:
                                result += f"{line}\n"
                            else:
                                result += f"                {line}\n"
                    else:
                        result += f"        {err_key}: {err_value}\n"
                result += "    }\n"
            else:
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
