import sys
sys.path.append('..')

import mineland

AGENTS_COUNT = 2
AGENTS_CONFIG = [
    {"name": "MineflayerBot0"},
    {"name": "MineflayerBot1"},
]

def pause():
    print("Press any key to continue")
    line = input()
    print("Pressed.")
    print("Continuing...")
    return get_resume_action()

def get_resume_action():
    return [
        { "type": mineland.Action.RESUME, "code": "" },
        { "type": mineland.Action.RESUME, "code": "" },
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
mindland = mineland.make(
    task_id="playground",

    # is_printing_server_info=True,
    is_printing_mineflayer_info=True,
    agents_count = AGENTS_COUNT,
    agents_config = AGENTS_CONFIG,
    ticks_per_step = 5,
)

obs = mindland.reset()
for i in range(5000):

    if i > 0 and i % 20 == 0:
        print_obs(obs)

    if i > 0 and i % 20 == 0:
        act = pause()
    else:
        act = get_resume_action()

    obs, code_info, event, done, task_info = mindland.step(action=act)

    for i in range(AGENTS_COUNT):
        if code_info[i] is not None:
            print(f'Bot#{AGENTS_CONFIG[i]["name"]}: {code_info[i]}')
        if event[i] is not None:
            print(f'Bot#{AGENTS_CONFIG[i]["name"]}: {event[i]}')