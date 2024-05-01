import mineland

AGENTS_COUNT = 2
AGENTS_CONFIG = [{"name": f"MineflayerBot{i}"} for i in range(AGENTS_COUNT)]

def get_resume_action():
    return [mineland.Action(type=mineland.Action.RESUME, code="") for _ in range(AGENTS_COUNT)]

def print_obs(obs):
    print(red_text('===== Observations ====='))
    for i in range(len(obs)):
        print(red_text(f'Bot#{AGENTS_CONFIG[i]["name"]}'), f': {obs[i]}')

def print_code_info(code_info):
    print(red_text('===== Code Info ====='))
    for i in range(len(code_info)):
        if code_info[i] is not None:
            print(red_text(f'Bot#{AGENTS_CONFIG[i]["name"]}'), f': {code_info[i]}')

def print_event(event):
    print(red_text('===== Events ====='))
    for i in range(len(event)):
        if event[i] is not None:
            print(red_text(f'Bot#{AGENTS_CONFIG[i]["name"]}'), f': {event[i]}')

# ===== Make =====
mland = mineland.make(
    task_id="harvest_1_oak_log", # no any task

    agents_count=AGENTS_COUNT,
    agents_config=AGENTS_CONFIG,

    ticks_per_step=20, # 1 second (because 20 ticks per second in minecraft)
)

def red_text(text):
    return f"\033[31m{text}\033[0m"

obs = mland.reset()
for i in range(5000):

    act = get_resume_action()

    obs, code_info, event, done, task_info = mland.step(action=act)

    if i > 0 and i % 10 == 0: # output per 10 seconds
        print_obs(obs)
        print_event(event)
        print_code_info(code_info)

        print(red_text('done:'), done)
        print(red_text('task_info:'), task_info)
        print(red_text(' ===== ===== ===== ===== Divide Line ===== ===== ===== ====='))
