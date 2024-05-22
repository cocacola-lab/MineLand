
#
# It's needed to install the following extra packages: stable_baselines3, gymnasium
# BE CAREFUL! The API is NOT stable and may change in the future!!!
#

from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
import gymnasium as gym
import numpy as np
import time
import mineland

task_id = "playground"

# open a file to log score
log_file = open(f"score_log_{time.time()}.txt", "w")

AGENT_COUNT = 1 # >=2 agents is not supported in this file
AGENT_CONFIG = [ {'name': f'mineflayer{i}'} for i in range(AGENT_COUNT) ]

class WrapperEnv(gym.Env):
    def __init__(self):
        super(WrapperEnv, self).__init__()
        self.obs_length = 6
        self.action_space = gym.spaces.Discrete(4) # [noop/forward/back/attack]
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(self.obs_length,), dtype=np.float32)

        self.mland = mineland.make(
            task_id='combat_1_zombie',
            agents_count = AGENT_COUNT,
            agents_config = AGENT_CONFIG,
            headless = True,
            enable_low_level_action = True,
        )

        self.score = 0

    def __merge_obs(x, y):
        x_floats = [float(i) for i in x]
        y_values = [float(value) for value in y.values()]
        combined = x_floats + y_values
        return np.array(combined, dtype=np.float32)
    
    def reset(self, seed=0):
        self.mland.close()
        self.mland = mineland.make(
            task_id='combat_1_zombie',
            agents_count = AGENT_COUNT,
            agents_config = AGENT_CONFIG,
            headless = True,
            enable_low_level_action = True,
        )
        _ = self.mland.reset()
        self.score = 0
        return np.zeros(self.obs_length, dtype=np.float32), {}
    
    def step(self, action):
        print(action)
        new_actions = mineland.LowLevelAction.no_op(AGENT_COUNT)
        if action < 3:
            new_actions[0][0] = int(action) # move
        else:
            new_actions[0][5] = 3      # attack

        obs, _, event, done, _ = self.mland.step(action=new_actions)

        reward = 0
        for e in event[0]:
            if e['type'] == 'entityHurt' and e['entity_type'] != 'self':
                reward += 10
            elif e['type'] == 'entityHurt' and e['entity_type'] == 'self':
                reward -= 5
            elif e['type'] == 'entityDead' and e['entity_name'] == 'zombie':
                reward += 100
            elif e['type'] == 'death':
                reward -= 100
            print(e)
        self.score += reward
        
        if done:
            print(f"=== Episode done, score: {self.score} ===")
            log_file.write(f"{self.score}\n")
            log_file.flush()
            return None, reward, done, done, {}
        
        if len(obs[0]['target_entities']) < 1:
            print(f"=== Episode interrupt, score: {self.score} ===")
            log_file.write(f"{self.score}\n")
            log_file.flush()
            return None, reward, True, True, {}
        
        return WrapperEnv.__merge_obs(obs[0]['location_stats']['pos'], obs[0]['target_entities'][0]['position']), reward, done, done, {}
    
    def close(self):
        self.mland.close()


env = WrapperEnv()
model = DQN(
    "MlpPolicy",
    env=env,
    learning_rate=1e-3,
    buffer_size=10000,
    exploration_initial_eps=1.0,
    exploration_final_eps=0.1,
    exploration_fraction=0.5,
    verbose=1
)
time.sleep(1)

model.learn(total_timesteps=20000)
model.save("./model/RL_Agent_CKPT.pkl")