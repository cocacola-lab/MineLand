import sys
sys.path.append('../../')

import os

import mineland
from mineland.utils import cyan_text
from mineland.alex import Alex

AGENTS_COUNT = 1
AGENTS_CONFIG = [
    {"name": "MineflayerBot0"},
]

task_id = "harvest_1_white_wool_with_1_iron_sword"

save_path = f"./storage/{task_id}"
if not os.path.exists(save_path):
    os.makedirs(save_path)
    #在task_id文件夹下建立log.txt
with open(f"{save_path}/log.txt", "a+") as f:
        f.write("\n\n\n========================== Iteration ==========================\n")

def wrapper(obs, code_info, event, done, task_info):
    return obs, code_info, done, task_info

def save_env(iteration, obs, code_info, done, task_info, action):
    observation = ""
    observation += f"\n\nstep: {iteration}\n"
    observation += f"obs: \n{str(obs)}\n"
    observation += f"code_info: \n{str(code_info)}\n"
    observation += f"done: {str(done)}\n"
    observation += f"task_info: \n{str(task_info)}\n"
    if isinstance(action, str):
        action = action.replace("\\n", "\n")
    else:
        action = str(action)
    observation += f"action: \n{action}\n"
    with open(f"{save_path}/log.txt", "a+") as f:
        f.write(observation)

def main():
    mineLand = mineland.make(
        task_id=task_id,
        is_printing_server_info=True,
        is_printing_mineflayer_info=True,
        agents_count = AGENTS_COUNT,
        agents_config = AGENTS_CONFIG,
        enable_auto_pause = False,
        ticks_per_step = 20,
    )

    alex = Alex(save_path=save_path, personality='None')

    iteration = 0

    obs = mineLand.reset()
    act = [{ "type": mineland.Action.RESUME, "code": ''}]

    a = input(f"\n\n[Alex] {cyan_text('teleport the bot to the task location')}\n\n")

    for i in range (10000):

        # print("try to step")
        obs, code_info, event, done, task_info = mineLand.step(action=act)
        obs, code_info, done, task_info = wrapper(obs, code_info, event, done, task_info)
        # print("step finished")

        if i == 0:
            act = [{ "type": mineland.Action.RESUME, "code": ''}]

        else:
            print(f"[Alex] {cyan_text(f'=================== step{i} =================== ')}")
            act = []
            action = alex.run(obs[0], code_info[0], done, task_info, verbose=True)
            if action is not None:
                act.append(action)
            else:
                iteration += 1
                save_env(iteration, obs[0], code_info[0], done, task_info, action)
                break
        
        if act != [{ "type": mineland.Action.RESUME, "code": ''}]:
            iteration += 1
            save_env(iteration, obs[0], code_info[0], done, task_info, action["code"])
            a = input("continue?\n")

    with open(f"{save_path}/log.txt", "a+") as f:
        f.write("\n\n\n========================== End ==========================\n\n\n")
    mineLand.close()


if __name__ == '__main__':
    main()
