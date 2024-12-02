#
# simple stage performance task example
# Important: This script is not a complete script,
#            it is just a snippet to show how to create a stage performance task,
#            and get enough information.
#

import mineland
from mineland.alex import Alex

mland = mineland.make(
    task_id="stage_performance_2_agent_date",
    agents_count = 2,
    headless = True,
)

obs = mland.reset()

agents_count = len(obs)
agents_name = [obs[i]['name'] for i in range(agents_count)]

# MARK: Create any agent like Alex here
agents = []
# ...

# You may need this information
print("Script: ", mland.get_script())
print("Personalities: ", mland.get_personalities())

for i in range(5000):
    if i > 0 and i % 20 == 0:
        print("task_info: ", task_info)
    
    if i == 0:
        act = mineland.Action.no_op(agents_count)
    else:
        # === Use agent action instead of no_op here ===
        # === Remember to tell mland.get_script() and mland.get_personalities() to agents ===
        # print("Script: ", mland.get_script())
        # print("Personalities: ", mland.get_personalities())
        act = mineland.Action.no_op(agents_count)

    obs, code_info, event, done, task_info = mland.step(action=act)
