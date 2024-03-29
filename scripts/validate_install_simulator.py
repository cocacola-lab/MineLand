import mineland

# Make the environment
mland = mineland.make(
    task_id="survival_0.01_days",
    agents_count = 2,
)

# Reset the environment
obs = mland.reset()
num_of_agents = len(obs)

for i in range(5000):
    act = mineland.Action.chat_op(num_of_agents) if i % 10 == 0 else mineland.Action.no_op(num_of_agents)

    obs, code_info, event, done, task_info = mland.step(action=act)

    if done: break

mland.close()

print("Validation passed! The simulator is installed correctly.")