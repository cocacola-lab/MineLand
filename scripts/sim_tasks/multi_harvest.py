import sys
sys.path.append('../..')

import mineland
import numpy as np
import mineland
from PIL import Image

def pause():
    print("Press any key to continue")
    line = input()
    print("Pressed.")
    print("Continuing...")
    return agents_resume_action

def get_next_action_from_stdin():
    actions = []
    for i in range(len(agents_name)):
        print(f" ===== Enter next action code for {agents_name[i]} (use \"END\" to stop entering): =====")
        action_code = ""
        while True:
            line = input()
            if line.startswith("END"):
                break
            action_code += line + '\n'
        action_code += "\n"
        if action_code.startswith('END'):
            actions.append({ "type": mineland.Action.RESUME, "code": "" })
        else:
            actions.append({ "type": mineland.Action.NEW, "code": action_code })
    print(" ===== Action Begin ===== ")
    print(actions)
    print(" ===== Action End ===== ")
    return actions

def print_obs(obs):
    for i in range(len(obs)):
        print(f'Bot#{obs[i]["name"]}: {obs[i]}')

def print_code_info(code_info):
    for i in range(len(code_info)):
        if code_info[i] is not None:
            print(f'Bot#{code_info[i]["name"]}: {code_info[i]}')

def save_image(obs):
    for i in range(len(obs)):
        print("img.shape: ", obs[i]['rgb'].shape)
        img = np.transpose(obs[i]['rgb'], (1, 2, 0))
        pil_img = Image.fromarray(img)
        pil_img.save(f'output_image_{agents_name[i]}.jpg')

# ===== Make =====
mindland = mineland.make(
    # task_id="multi_harvest_1_dirt",
    task_id="harvest_1_cobblestone",
    agents_count=1,

    is_printing_server_info=True,
    is_printing_mineflayer_info=True,
)

obs = mindland.reset()

agents_count = len(obs)
agents_name = [obs[i]['name'] for i in range(agents_count)]
agents_resume_action = [{ "type": mineland.Action.RESUME, "code": "" } for _ in range(agents_count)]

dig_below_block = "await bot.dig(bot.blockAt(bot.entity.position.offset(0, -1, 0)))"

for i in range(5000):
    # if i > 0 :
    #     print(code_info[0])
    if i > 0 and i % 20 == 0 and code_info[0]["is_ready"]:
        act = [{ "type": mineland.Action.NEW, "code": dig_below_block } for _ in range(agents_count)]
    else:
        act = agents_resume_action

    if i > 0 and i % 20 == 0:
        print_obs(obs)
        print("task_info: ", task_info)

    obs, code_info, event, done, task_info = mindland.step(action=act)

    assert task_info is not None, "task_info should not be None"

    if done:
        print(" ===== Task Done! ===== ")
        print("task_info: ", task_info)
        break

    if i > 0 and i % 4 == 0:
        print_code_info(code_info)

    # TODO: 任务tick 和 服务器log tick 不一致的问题（可能是任务tick为时间tick，而不是服务器log tick）
