# This script is a simple example of how to connect to any server.
# It will connect to a server running on localhost:25565 and add an agent every 30 steps.
# The script will run for 305 steps and then close the environment.

import mineland

# Make the environment
mland = mineland.MineLand(
    server_host="localhost", # You can change this to your server IP
    server_port=25565,       # You can change this to your server port
    agents_count = 2,
)

# Reset the environment
obs = mland.reset()
num_of_agents = len(obs)

for i in range(305):
    if i % 30 == 0:
        num_of_agents += 1
        mland.add_an_agent()

    act = mineland.Action.chat_op(num_of_agents) if i % 10 == 0 else mineland.Action.no_op(num_of_agents)

    obs, code_info, event, done, task_info = mland.step(action=act)

    if i % 30 == 0:
        for ob in obs:
            print('obs:', ob)

    if done: break

mland.close()