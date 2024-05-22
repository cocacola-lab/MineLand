import sys
import shutil
sys.path.append('../')

import os

import mineland
from mineland.utils import cyan_text
from mineland.alex import Alex

AGENTS_COUNT = 1
AGENTS_CONFIG = [
    {"name": "Bot"}
]

task_id = "techtree_1_diamond_pickaxe"

save_path = f"./storage/{task_id}"
if not os.path.exists(save_path):
    os.makedirs(save_path)
    #在task_id文件夹下建立log.txt
with open(f"{save_path}/log.txt", "a+") as f:
        f.write("\n\n\n========================== Iteration ==========================\n")

def wrapper(obs, code_info, event, done, task_info):
    return obs, code_info, done, task_info

def print_obs(obs):
    print(obs)
    print(f"obs length: {len(obs)}")
    for i in range(len(obs)):
        print(f'Bot#{AGENTS_CONFIG[i]["name"]}: {obs[i]}')

def print_code_info(code_info):
    for i in range(len(code_info)):
        if code_info[i] is not None:
            print(f'Bot#{AGENTS_CONFIG[i]["name"]}: {code_info[i]}')

def print_event(event):
    for i in range(len(event)):
        if event[i] is not None:
            print(f'Bot#{AGENTS_CONFIG[i]["name"]}: {event[i]}')

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
    # path = './storage/survival_1_days'
    # dst_folder = path
    # if os.path.exists(dst_folder):
    #     shutil.rmtree(dst_folder)
    
    mineLand = mineland.make(
        task_id=task_id,
        is_printing_server_info=True,
        is_printing_mineflayer_info=True,
        agents_count = AGENTS_COUNT,
        agents_config = AGENTS_CONFIG,
        ticks_per_step = 20,
        enable_auto_pause = True,
    )

    alex = Alex(save_path=save_path, personality="")

    obs = mineLand.reset()
    act = [{ "type": mineland.Action.RESUME, "code": ''}]

    a = input(f"\n\n[Alex] {cyan_text('teleport the bot to the task location')}\n\n")
    iteration = 0
    for i in range (5000):
        print("iteration : " + str(iteration))

        obs, code_info, event, done, task_info = mineLand.step(action=act)
        obs, code_info, done, task_info = wrapper(obs, code_info, event, done, task_info)

        if i == 2 :
            act = [{ "type": mineland.Action.RESUME, "code": ''}]
        else:
            print(f"[Alex] {cyan_text(f'=================== step{i} =================== ')}")
            act = []
            for j in range(AGENTS_COUNT):
                obs[j].inventory = obs[j].inventory_all
                
                action = alex.run(obs[j], code_info[j], done, task_info, verbose=True)
                if action is not None:
                    act.append(action)
                save_env(iteration, obs[j], code_info[j], done, task_info, action)
            if act != [{ "type": mineland.Action.RESUME, "code": ''}]:
                save_env(iteration, obs[0], code_info[0], done, task_info, action["code"])
                iteration += 1
                # a = input("continue?\n")
            if task_info.is_success == True :
                print("Task successful!")
                break

        


    with open(f"{save_path}/log.txt", "a+") as f:
        f.write("\n\n\n========================== End ==========================\n\n\n")
    mineLand.close()

    pass

def test_generate_skill_info():
    skill_manager = SkillManager()
    code_info = {"last_code": "async function harvestOakLog(bot) {\n  bot.chat('Locating the nearest oak tree.');\n  const oakTreePosition = new Vec3(-32.3, 64, -22.81); // The position is assumed based on bot's current location\n  await bot.pathfinder.goto(new GoalNear(oakTreePosition.x, oakTreePosition.y, oakTreePosition.z, 1));\n  bot.chat('Approaching the oak tree.');\n  const block = bot.blockAt(oakTreePosition);\n  if (block && block.name === 'oak_log') {\n    await bot.dig(block);\n    bot.chat('Harvested 1 oak log.');\n  } else {\n    bot.chat('No oak log found at this position.');\n  }\n}\nawait harvestOakLog(bot);\n"}
    skill_info = skill_manager.generate_skill_info(code_info)
    
    skill_description = f"    // { skill_info['description']}"


    description = f"async function {skill_info['name']}(bot) {{\n{skill_description}\n}}"
    print(description)

if __name__ == '__main__':
    main()
    # test_generate_skill_info()
