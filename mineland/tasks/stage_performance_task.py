from mineland.sim.data.task_info import TaskInfo

from .base_task import BaseTask
from .utils import *
import numpy as np



class StagePerformanceTask(BaseTask):
    def __init__(
        self,
        agent_names,
        system_instructions,
        critical_point,
        initial_inventory,
        personalities,
        script,
        
        **kwargs,
    ):
        self.agent_names = agent_names
        self.critical_point = critical_point
        self.initial_inventory = initial_inventory
        self.personalities = personalities
        self.script = script
        self.system_instructions = system_instructions
        self.guidance = "follow the script"
        self.goal = "In order to get a high score, what you do should be as scripted as possible  "
        self.finished = [False for i in range(len(critical_point))]
        self.max_chat_score = [0 for i in range(len(critical_point))]
        self.seq = ""
        self.baseline = ""
        for point in critical_point:
            self.baseline += point[0] + ' ' + point[1] + ' ' + point[2] + ', '
        kwargs["agents_config"] = [{"name": name} for name in agent_names]
        kwargs["agents_count"] = len(agent_names)

        print("Task Id: ", kwargs["task_id"])
        print("Agents config (after modification): ", kwargs["agents_config"])
        print("Agents names: ", agent_names)
        print("Guidnace: ", self.guidance)
        print("Script: ", self.script)
        super().__init__(**kwargs)
    
    def reset(self):
        obs = self.env.reset()
        self.last_obs = obs
        for instruction in self.system_instructions:
            self.server_manager.execute(instruction)
        for name, inventory in self.initial_inventory.items(): 
            for item, number in inventory.items(): 
                self.server_manager.execute(f"give {name} {item} {number}")
        print("Finish reset!")
        return obs
    
    def get_personalities(self) :
        return self.personalities
    
    def get_script(self) :
        return self.script

    def get_score(self) :
        lcs = self.calc_lcs(self.seq, self.baseline)
        if len(self.baseline) == 0 : 
            local_score = 0
        else:
            local_score = lcs/len(self.baseline)
        if len(self.seq) == 0 : 
            global_score = 0
        else:
            global_score = lcs/len(self.seq)

        return local_score, global_score
    
    def update_seq(self, obs, events) :
        last_obs = self.last_obs
        # for obs_s in obs :
        #     print(obs_s)
        for event in events[0]:
            if event['type'] == 'chat' :
                self.seq += f'{event["username"]} chat {event["only_message"]}, '
        for event in events[0]:
            if event['type'] == 'entityDead':
                self.seq += f'combat {self.target}, '       
        for i in range(len(self.agent_names)) :
            last_inventory = last_obs[i].inventory['name']
            inventory = obs[i].inventory['name']
            #get something
            get_list = [x for x in inventory if x != None and x not in last_inventory]
            for x in get_list:
                self.seq += f'{self.agent_names[i]} get {x}, '

    def calc_lcs(self, s1, s2) :
        n = len(s1)
        m = len(s2)
        dp = [[0 for i in range(m + 1)] for j in range(n + 1)]
        for i in range(n) :
            for j in range(m) :
                if s1[i] == s2[j] :
                    dp[i][j] = max(dp[i][j], dp[i - 1][j - 1] + 1)
                else :
                    dp[i][j] = max(dp[i][j - 1], dp[i - 1][j])
        return dp[n - 1][m - 1]
    
    def step(self, action):
        obs, code_info, events, done, task_info = self.env.step(action)
        self.update_seq(obs, events)
        local_score, global_score = self.get_score()
        task_info = TaskInfo(
            task_id=self.task_id,
            is_success=False,
            is_failed=False,
            goal=self.goal,
            local_score=local_score,
            global_score=global_score,
            guidance=self.guidance,
        )
        self.last_obs = obs
        return obs, code_info, events, False, task_info
