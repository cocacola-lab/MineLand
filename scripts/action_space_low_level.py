import mineland

AGENTS_COUNT = 2
AGENTS_CONFIG = [{"name": f"MineflayerBot{i}"} for i in range(AGENTS_COUNT)]

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

    enable_low_level_action=True,

    ticks_per_step=20, # 1 second (because 20 ticks per second in minecraft)
)

obs = mland.reset()
for i in range(5000):

    # act = mineland.LowLevelAction.no_op(AGENTS_COUNT)
    act = mineland.LowLevelAction.random_op(AGENTS_COUNT)

    act[0][1] = 1
    act[1][3] = 24

    obs, code_info, event, done, task_info = mland.step(action=act)

    if i > 0 and i % 4 == 0:
        # print_obs(obs)
        # print_event(event)
        print_code_info(code_info)