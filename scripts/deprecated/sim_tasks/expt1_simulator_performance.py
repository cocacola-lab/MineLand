import sys
sys.path.append('../..')

from datetime import datetime

import mineland

def pause():
    print("Press any key to continue")
    line = input()
    print("Pressed.")
    print("Continuing...")
    return agents_resume_action

# ===== Make =====
AGENTS_COUNT = 32
mindland = mineland.make(
    task_id="survival_1_days",
    headless=True,

    agents_count=AGENTS_COUNT,
    agents_config=[{"name": f"MineflayerBot{i}"} for i in range(AGENTS_COUNT)],

    is_printing_server_info=True,
    is_printing_mineflayer_info=True,
)

obs = mindland.reset()

agents_count = len(obs)
agents_name = [obs[i]['name'] for i in range(agents_count)]
agents_resume_action = [{ "type": mineland.Action.RESUME, "code": "" } for _ in range(agents_count)]

for i in range(5000):
    act = agents_resume_action
    obs, code_info, event, done, task_info = mindland.step(action=act)
    print(datetime.now().strftime("%H:%M:%S"), "step", i, "done", " tick:", obs[0]['tick'])
