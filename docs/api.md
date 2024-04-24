# MineLand API Documentation

> The structure of this document is based on [MineDojo Docs](https://docs.minedojo.org/), whose clarity and widespread acceptance.

## 1. First Agent in MineLand

### Quick Start

After following the [Installation Docs](./installation.md), you can **import MineLand**.

```python
import mineland
```

**Secondly, an Environment can now be created.**

```python
mland = mineland.make(
	task_id="survival_0.01_days",
    agents_count=2,
)
```

In the code above, `task_id` refers to the task content executed by the environment. The available options for `task_id` can be found in [Tasks Module](https://github.com/cocacola-lab/MineLand/tree/main/mineland/tasks/description_files). If you do not wish to enable any benchmarks, you can initialize a simulator without benchmark by directly using the `mineland.MineLand` class, or by setting `task_id` to `playground`.

`agents_count` represents the number of agents initially present in the environment. If you wish to configure the initial settings (like names) of the agents, you can use `agents_config`. for more details, see [agents_config](#agents_config).

MineLand supports connecting to any vanilla 1.19 Minecraft server, meaning that you can use MineLand not only as a machine learning tool but also as a fully functional, interruption-capable, Python-side Minecraft bot library. This has already been applied in some projects. You can pass the parameters `server_host` and `server_port` to specify the target server; for more details, see [server_host](#server_host). If these parameters are not provided, a Minecraft server is automatically invoked locally.

**Then, let bots connect to the server.**

```python
obs = mland.reset()
```

After `mland.reset()` has been executed, all bots will connect to the server.

If you haven't enable the PAUSE mode or you connect to a remote server, the time will begin to pass...

**Next, we can implement a main loop.**

```python
for i in range(5000):
    act = mineland.Action.no_op(len(obs))
    obs, code_info, event, done, task_info = mland.step(action=act)
    if done: break
```

In the main loop, we need to complete at least 3 parts of the code: getting actions, passing in actions and receiving observations, and checking termination conditions.

First part, getting actions. MineLand's default high-level actions differ from the action spaces of other gym-style libraries. A high-level action consists of a piece of JavaScript code. In this example, we will fetch a RESUME Action (which performs no action). You can also use `mineland.Action.chat_op(num_of_agents)` to get the bot to print messages in the chat area.

Please note, to implement the "interruption" feature, high-level actions are divided into two modes: `RESUME` and `NEW`. The code is executed **only** under NEW, and any previous code is interrupted. You can check in the observation space whether the previous code has finished executing. For more details, see [code_info](#code_info)

Second part, getting observations. Pass the action into the `step` function and obtain five pieces of information: `obs`, `code_info`, `event`, `done`, and `task_info`. Here, `obs`, `code_info`, and `event` are all lists, each equal in length to the number of agents. For instance, `obs[0]` can be used to view all observation information for the first agent; you might try printing `obs[0]`, `code_info[0]`, and `event[0]` directly. Meanwhile, `done` and `task_info` are not lists, and relate to benchmark information.

Third part, termination conditions. This can be implemented using a simple `if done: break` statement.

**Finally**, close the environment by executing the follows.

```python
mland.close();
```

### Observation and Action Spaces

Observation Space is defined in [observation.py](https://github.com/cocacola-lab/MineLand/blob/main/mineland/sim/data/observation.py) and [observation_utils.js](https://github.com/cocacola-lab/MineLand/blob/main/mineland/sim/mineflayer/observation_utils.js).

Action Space (High-level) is all functions you can invoke in javascript and mineflayer (including pathfinder, etc). You can refer to [high_level_action](https://github.com/cocacola-lab/MineLand/tree/main/mineland/assets/high_level_action) and [Mineflayer API Docs](https://github.com/PrismarineJS/mineflayer/blob/master/docs/api.md).

## 2. Environment Parameters

### agents_config

### server_host

### server_port

## 3. Observation Space

### obs

### code_info

### event

### done

### task_info

## 4. Action Space (High-level)

## 5. Action Space  (Low-level)
