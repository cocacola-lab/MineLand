import sys
sys.path.append('..')

import mineland

AGENTS_COUNT = 1
AGENTS_CONFIG = [
    {"name": "MineflayerBot0"},
    # {"name": "MineflayerBot1"},
]

def get_next_action_from_stdin():
    actions = []
    for i in range(AGENTS_COUNT):
        print(f" ===== Enter next action code for {AGENTS_CONFIG[i]['name']} (use \"END\" to stop entering): =====")
        action_code = ""
        while True:
            line = input()
            if line.startswith("END"):
                break
            action_code += line + '\n'
        action_code += "\n"
        actions.append({ "type": mineland.Action.NEW, "code": action_code })
    print(" ===== Action Begin ===== ")
    print(actions)
    print(" ===== Action End ===== ")
    return actions
    

def get_resume_action():
    return [
        { "type": mineland.Action.RESUME, "code": "" },
        # { "type": mineland.Action.RESUME, "code": "" },
    ]

def print_obs(obs):
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

# ===== Make =====
mineland = mineland.make(
    task_id="playground",

    is_printing_server_info=True,
    is_printing_mineflayer_info=True,
    agents_count = AGENTS_COUNT,
    agents_config = AGENTS_CONFIG,
    ticks_per_step = 5,
)

obs = mineland.reset()
for i in range(5000):

    # 因为python变量的作用域不包括循环体，所以act不需要在函数外部声明
    if i % 8 == 0:
        act = get_next_action_from_stdin()
    else:
        act = get_resume_action()

    obs, code_info, event, done, task_info = mineland.step(action=act)

    if i > 0 and i % 8 == 0:
        # print_obs(obs)
        print_code_info(code_info)



