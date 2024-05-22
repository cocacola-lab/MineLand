import sys
sys.path.append('../..')

import mineland


def pause():
    print("Press any key to continue")
    line = input()
    print("Pressed.")
    print("Continuing...")
    return get_resume_action()

def get_resume_action():
    return [
        { "type": mineland.Action.RESUME, "code": "" },
        { "type": mineland.Action.RESUME, "code": "" }
    ]

def print_obs(obs):
    for i in range(len(obs)):
        print(f'Bot#{obs[i]["name"]}: {obs[i]}')

def print_code_info(code_info):
    for i in range(len(code_info)):
        if code_info[i] is not None:
            print(f'Bot#{code_info[i]["name"]}: {code_info[i]}')

# ===== Make =====
mineland = mineland.make(
    task_id="stage_performance_2_agent_argue",

    is_printing_server_info=True,
    is_printing_mineflayer_info=True,
)

obs = mineland.reset()

agents_count = 2
agents_name = ['Bob', 'Alice']

for i in range(5000):

    if i > 0 and i % 20 == 0:
        print("current_tick: ", obs[0].tick)
        print("task_info: ", task_info)


    act = get_resume_action()

    obs, code_info, event, done, task_info = mineland.step(action=act)

    assert task_info is not None, "task_info should not be None"

    # if done:
    #     print(" ===== Task Done! ===== ")
    #     print("task_info: ", task_info)
    #     break

    # TODO: 任务tick 和 服务器log tick 不一致的问题（可能是任务tick为时间tick，而不是服务器log tick）
