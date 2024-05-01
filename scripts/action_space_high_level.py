import mineland

AGENTS_COUNT = 1
AGENTS_CONFIG = [{"name": f"MineflayerBot{i}"} for i in range(AGENTS_COUNT)]

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
        if action_code == "":
            print(" ===== No action code entered, RESUME the bot. ===== ")
            actions.append(mineland.Action(type=mineland.Action.RESUME, code=""))
        else:
            action_code += "\n"
            print(" ===== action code entered, INTERRUPT the bot. ===== ")
            actions.append(mineland.Action(type=mineland.Action.NEW, code=action_code))
    return actions

def get_resume_action():
    return [mineland.Action(type=mineland.Action.RESUME, code="") for _ in range(AGENTS_COUNT)]

def print_obs(obs):
    print('===== Observations =====')
    for i in range(len(obs)):
        print(f'Bot#{AGENTS_CONFIG[i]["name"]}: {obs[i]}')

def print_code_info(code_info):
    print('===== Code Info =====')
    for i in range(len(code_info)):
        if code_info[i] is not None:
            print(f'Bot#{AGENTS_CONFIG[i]["name"]}: {code_info[i]}')

def print_event(event):
    print('===== Events =====')
    for i in range(len(event)):
        if event[i] is not None:
            print(f'Bot#{AGENTS_CONFIG[i]["name"]}: {event[i]}')

# ===== Make =====
mland = mineland.make(
    task_id="playground", # no any task

    agents_count=AGENTS_COUNT,
    agents_config=AGENTS_CONFIG,

    ticks_per_step=20, # 1 second (because 20 ticks per second in minecraft)
)

obs = mland.reset()
for i in range(5000):

    if i > 0 and i % 4 == 0:
        act = get_next_action_from_stdin()
    else:
        act = get_resume_action()

    obs, code_info, event, done, task_info = mland.step(action=act)

    if i > 0 and i % 4 == 0:
        # print_obs(obs)
        # print_event(event)
        print_code_info(code_info)