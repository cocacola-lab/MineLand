import sys
sys.path.append('../..')

import mineland

def pause():
    print("Press any key to continue")
    line = input()
    print("Pressed.")
    print("Continuing...")
    return agents_resume_action

def print_obs(obs):
    for i in range(len(obs)):
        print(f'Bot#{obs[i]["name"]}: {obs[i]}')

def print_code_info(code_info):
    for i in range(len(code_info)):
        if code_info[i] is not None:
            print(f'Bot#{code_info[i]["name"]}: {code_info[i]}')

# ===== Make =====
mindland = mineland.make(
    task_id="survival_0.01_days",
    mode='competitive',
    agents_count=2,
    agents_config=[{"name": f"MineflayerBot{i}"} for i in range(2)],

    is_printing_server_info=True,
    is_printing_mineflayer_info=True,
)

obs = mindland.reset()

agents_count = len(obs)
agents_name = [obs[i]['name'] for i in range(agents_count)]
agents_resume_action = [{ "type": mineland.Action.RESUME, "code": "" } for _ in range(agents_count)]
agents_chat_action = [{ "type": mineland.Action.NEW, "code": "bot.chat('I am here')" }, { "type": mineland.Action.RESUME, "code": "" }]
for i in range(5000):

    if i > 0 and i % 20 == 0:
        print("current_tick: ", obs[0].tick)
        print("task_info: ", task_info)

    # if i == 40:
    #     mindland.server_manager.execute("kill MineflayerBot0")
    # if i == 80:
    #     mindland.server_manager.execute("kill MineflayerBot1")

    act = agents_resume_action
    if i > 0 and i % 10 == 0:
        act = agents_chat_action

    obs, code_info, event, done, task_info = mindland.step(action=act)

    assert task_info is not None, "task_info should not be None"

    if done:
        print(" ===== Task Done! ===== ")
        print("task_info: ", task_info)
        break

    # TODO: 任务tick 和 服务器log tick 不一致的问题（可能是任务tick为时间tick，而不是服务器log tick）
