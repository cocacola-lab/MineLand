class Action:
    # ===== Action Type =====
    RESUME = 0
    NEW = 1

    # ===== Action Function =====
    def __init__(self, type: int, code: str):
        self.type = type
        self.code = code
    
    def __str__(self):
        return f"Action(type={self.type}, code={self.code})"

    def to_json(self):
        return {
            "type": self.type,
            "code": self.code,
        }
    
    @staticmethod
    def no_op(num_of_agents: int):
        return [Action(Action.RESUME, "") for _ in range(num_of_agents)]

    @staticmethod
    def chat_op(num_of_agents: int):
        return [Action(Action.NEW, f"bot.chat('I am Bot#{i}')") for i in range(num_of_agents)]