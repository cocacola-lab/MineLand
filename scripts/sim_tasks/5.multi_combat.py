#
# You can run this script directly to test the task.
#

script = '''
const zombie = bot.nearestEntity((entity) => entity.name === 'zombie')

if (!zombie) {
    console.log('No zombie found.');
    return;
}

console.log('Zombie found. Starting to attack.');

// 攻击僵尸
while(true) {
    bot.attack(zombie);
    await bot.waitForTicks(20);
}
'''

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
    task_id="combat_8_pig_with_1_diamond_sword_and_1_shield",
    agents_count=3,
    agents_config=[{"name": f"MineflayerBot{i}"} for i in range(3)],

    is_printing_server_info=True,
    is_printing_mineflayer_info=True,
)

obs = mindland.reset()

agents_count = len(obs)
agents_name = [obs[i]['name'] for i in range(agents_count)]
agents_resume_action = [{ "type": mineland.Action.RESUME, "code": "" } for _ in range(agents_count)]

for i in range(5000):

    print('life_stats:', obs[0]['life_stats'])
    print('equipment:', obs[0]['equipment']['name'])
    if i == 0:
        act = [{ "type": mineland.Action.NEW, "code": script } for _ in range(agents_count)]
    else:
        act = agents_resume_action
    
    print("action:", act[0])

    obs, code_info, event, done, task_info = mindland.step(action=act)

    print('event:', event)

    assert task_info is not None, "task_info should not be None"

    if done:
        print(" ===== Task Done! ===== ")
        print("task_info: ", task_info)
        break

    # TODO: 任务tick 和 服务器log tick 不一致的问题（可能是任务tick为时间tick，而不是服务器log tick）
