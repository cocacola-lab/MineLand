# This script is a simple example of how to connect to any server.
# It will connect to a server running on localhost:25565 and add an agent every 30 steps.
# The script will run for 305 steps and then close the environment.

import mineland

# Make the environment
mland = mineland.MineLand(
    server_host='localhost', # You can change this to your server IP
    server_port=25565,       # You can change this to your server port
    agents_count = 2,
)

# Reset the environment
obs = mland.reset()
num_of_agents = len(obs)

disconnect_cnt = 0

for i in range(305):
    if i > 0 and i <= 150 and i % 30 == 0:
        num_of_agents += 1
        mland.add_an_agent()
    
    if i > 150 and i % 30 == 0:
        mland.disconnect_an_agent(f'MineflayerBot{disconnect_cnt}')
        disconnect_cnt += 1

    act = mineland.Action.chat_op(num_of_agents) if (i + 15) % 30 == 0 else mineland.Action.no_op(num_of_agents)

    obs, code_info, event, done, task_info = mland.step(action=act)

    if i > 0 and i % 30 == 0:
        j = 0
        for ob in obs:
            if ob is None:
                print(f'Agent {j} is disconnected')
            else:
                print(f'Agent {j} is connected, obs:', ob['name'], ob['rgb'].shape, ob['tick'])
            j += 1

    if done: break

mland.close()