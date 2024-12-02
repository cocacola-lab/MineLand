from typing import List, Dict, Union
from omegaconf import OmegaConf
import importlib

from .utils import *

from .base_task import BaseTask
from .survival_task import SurvivalTask
from .harvest_task import HarvestTask
from .techtree_task import TechtreeTask
from .combat_task import CombatTask
from .playthrough_task import PlaythroughTask
from .creative_task import CreativeTask
from .construction_task import ConstructionTask
from .stage_performance_task import StagePerformanceTask

# ===== Main Make =====

def make(**kwargs):
    '''Make a task environment.

    Args:
        task_id (str): The id of the task.

    Example:
        >>> env = mineland.make("playground", agents_count=1, agents_config=[{"name": "MineflayerBot0"}])
        >>> env = mineland.make("survival_single_agent", survival_target_day=1)
        >>> env = mineland.make("survival_multi_agent", survival_target_day=1, agents_count=2)
    '''

    if 'agents_count' not in kwargs:
        raise ValueError("agents_count must be provided in the arguments.")

    if 'server_host' in kwargs or 'server_port' in kwargs:
        raise ValueError("server_host and server_port should not be provided in the Task Mode!\nBecause Benchmark only works in the local environment.")

    if 'task_id' not in kwargs:
        raise ValueError("task_id must be provided in the arguments.")
    
    def add_mode_argument():
        if 'mode' not in kwargs or (kwargs['mode'] != 'cooperative' and kwargs['mode'] != 'competitive'):
            kwargs['mode'] = 'cooperative'
            print("task mode has been modified as cooperative")

    if 'agents_config' not in kwargs and not kwargs['task_id'].startswith("stage_performance"):
        kwargs['agents_config'] = [{'name': f'MineflayerBot{i}'} for i in range(kwargs['agents_count'])]

    if kwargs['task_id'].startswith("playground"):
        env = _make_playground(**kwargs)
    elif kwargs['task_id'].startswith("survival") :
        add_mode_argument()
        env = _make_survival(**kwargs)
    elif kwargs['task_id'].startswith("harvest"):
        add_mode_argument()
        env = _make_harvest(**kwargs)
    elif kwargs['task_id'].startswith("techtree"):
        add_mode_argument()
        env = _make_techtree(**kwargs)
    elif kwargs['task_id'].startswith("combat"):
        env = _make_combat(**kwargs)
    elif kwargs['task_id'].startswith("playthrough"):
        add_mode_argument()
        env = _make_playthrough(**kwargs)
    elif kwargs['task_id'].startswith("creative"):
        add_mode_argument()
        env = _make_creative(**kwargs)
    elif kwargs['task_id'].startswith("construction"):
        env = _make_construction(**kwargs)
    elif kwargs['task_id'].startswith("stage_performance"):
        env = _make_stage_performance(**kwargs)
    else:
        env = _make_creative(**kwargs)
    return env

# ===== Load Datas =====

def _resource_file_path(fname) -> str:
    with importlib.resources.path("mineland.tasks.description_files", fname) as p:
        return str(p)

# load survival tasks
SURVIVAL_TASKS = OmegaConf.load(
    _resource_file_path("survival_tasks.yaml")
)
# check no duplicates
assert len(set(SURVIVAL_TASKS.keys())) == len(SURVIVAL_TASKS)

# load harvest tasks
HARVEST_TASKS = OmegaConf.load(
    _resource_file_path("harvest_tasks.yaml")
)
# check no duplicates
assert len(set(HARVEST_TASKS.keys())) == len(HARVEST_TASKS)

# load tech tree tasks
TECHTREE_TASKS = OmegaConf.load(
    _resource_file_path("techtree_tasks.yaml")
)
# check no duplicates
assert len(set(TECHTREE_TASKS.keys())) == len(TECHTREE_TASKS)

# load tech tree tasks
COMBAT_TASKS = OmegaConf.load(
    _resource_file_path("combat_tasks.yaml")
)
# check no duplicates

assert len(set(COMBAT_TASKS.keys())) == len(COMBAT_TASKS)

# load tech tree tasks
CREATIVE_TASKS = OmegaConf.load(
    _resource_file_path("creative_tasks.yaml")
)
# check no duplicates
assert len(set(CREATIVE_TASKS.keys())) == len(CREATIVE_TASKS)

# load construction tasks
CONSTRUCTION_TASKS = OmegaConf.load(
    _resource_file_path("construction_tasks.yaml")
)
# check no duplicates
assert len(set(CONSTRUCTION_TASKS.keys())) == len(CONSTRUCTION_TASKS)

# load stage performance tree tasks
STAGE_PERFORMANCE_TASKS = OmegaConf.load(
    _resource_file_path("stage_performance_tasks.yaml")
)
# check no duplicates
assert len(set(STAGE_PERFORMANCE_TASKS.keys())) == len(STAGE_PERFORMANCE_TASKS)

# print("HARVEST_TASKS: ", HARVEST_TASKS)
# print("TECHTREE_TASKS: ", TECHTREE_TASKS)
# print("COMBAT_TASKS: ", COMBAT_TASKS)
# print("CREATIVE_TASKS: ", CREATIVE_TASKS)

# ===== Playground =====

def _make_playground(**kwargs):
    env = BaseTask(**kwargs)
    return env

# ===== Survival =====

def _make_survival(**kwargs):
    task_id = kwargs['task_id']
    if task_id not in SURVIVAL_TASKS:
        raise ValueError(f"Invalid task_id: {task_id}")
    
    task = SURVIVAL_TASKS[task_id]

    kwargs["guidance"] = task["guidance"]
    kwargs["survival_target_day"] = task["survival_target_day"]
    kwargs["initial_inventory"] = task["initial_inventory"]
    kwargs["goal"] = task["goal"]
    env = SurvivalTask(**kwargs)
    return env

# ===== Harvest =====

def _make_harvest(**kwargs):
    task_id = kwargs['task_id']
    if task_id not in HARVEST_TASKS:
        raise ValueError(f"Invalid task_id: {task_id}")

    # Harvest task name format:
    #     <single/multi>_harvest_<num_of_target_item>_<target_item>[_with_<num_of_tool>_<tool>]
    #     Be careful! Target_item and tool can contain "_".

    # parts = task_id.split("_")
    # if parts[1] != "harvest":
    #     raise ValueError(f"Invalid task_id: {task_id}")

    # num_of_target_item = int(parts[2])

    # # Identifying if there's a tool specified
    # if 'with' in parts:
    #     with_index = parts.index('with')
    #     target_item = '_'.join(parts[3:with_index])
    #     num_of_tool = int(parts[with_index+1])
    #     tool = '_'.join(parts[with_index+2:])
    # else:
    #     target_item = '_'.join(parts[3:])
    #     num_of_tool = 0
    #     tool = None
    
    task = HARVEST_TASKS[task_id]
    target_item = task["target"]
    num_of_target_item = task["number_of_target"]
    initial_inventory = task["initial_inventory"]
    guidance = task["guidance"]
    goal = task["goal"]
    env = HarvestTask(
        target_item=target_item,
        num_of_target_item=num_of_target_item,
        initial_inventory=initial_inventory,
        goal=goal,
        guidance=guidance,
        **kwargs,
    )
    return env

# ===== Techtree =====

def _make_techtree(**kwargs):
    task_id = kwargs['task_id']
    if task_id not in TECHTREE_TASKS:
        raise ValueError(f"Invalid task_id: {task_id}")

    # Techtree task name format:
    #     <single/multi>_techtree_<target_item>[_with_<num_of_tool>_<tool>]
    #     Be careful! Target_item and tool can contain "_".

    # parts = task_id.split("_")
    # if parts[1] != "techtree":
    #     raise ValueError(f"Invalid task_id: {task_id}")

    # num_of_target_item = 1

    # # Identifying if there's a tool specified
    # if 'with' in parts:
    #     with_index = parts.index('with')
    #     target_item = '_'.join(parts[2:with_index])
    #     num_of_tool = int(parts[with_index+1])
    #     tool = '_'.join(parts[with_index+2:])
    # else:
    #     target_item = '_'.join(parts[2:])
    #     num_of_tool = 0
    #     tool = None

    task = TECHTREE_TASKS[task_id]
    target_item = task["target"]
    num_of_target_item = task["number_of_target"]
    initial_inventory = task["initial_inventory"]
    guidance = task["guidance"]
    goal = task["goal"]
    env = TechtreeTask(
        target_item=target_item,
        num_of_target_item=num_of_target_item,
        initial_inventory=initial_inventory,
        goal=goal,
        guidance=guidance,
        **kwargs,
    )
    return env

# ===== Combat =====

def _make_combat(**kwargs):
    task_id = kwargs['task_id']
    if task_id not in COMBAT_TASKS:
        raise ValueError(f"Invalid task_id: {task_id}")

    # Combat task name format:
    #     <single/multi>_combat_<num_of_target>_<target>[_with_<num_of_tool>_<tool>]
    #     Be careful! Item and tool can contain "_".

    # parts = task_id.split("_")
    # if parts[1] != "combat":
    #     raise ValueError(f"Invalid task_id: {task_id}")

    # num_of_target = int(parts[2])

    # # Identifying if there's a tool specified
    # if 'with' in parts:
    #     with_index = parts.index('with')
    #     target = '_'.join(parts[3:with_index])
    #     num_of_tool = int(parts[with_index+1])
    #     tool = '_'.join(parts[with_index+2:])
    # else:
    #     target = '_'.join(parts[3:])
    #     num_of_tool = 0
    #     tool = None
    task = COMBAT_TASKS[task_id]
    target = task["target"]
    num_of_target = task["number_of_target"]
    initial_inventory = task["initial_inventory"]
    goal = task["goal"]

    env = CombatTask(
        target=target,
        num_of_target=num_of_target,
        goal=goal,
        initial_inventory=initial_inventory,
        **kwargs,
    )
    return env

# ===== Playthrough =====

def _make_playthrough(**kwargs):
    task_id = kwargs['task_id']
    
    if task_id != "playthrough":
        raise ValueError(f"Invalid task_id: {task_id}")
    
    env = PlaythroughTask(**kwargs)
    return env

# ===== Creative =====

def _make_creative(**kwargs):
    task_id = kwargs['task_id']
    if task_id not in CREATIVE_TASKS:
        raise ValueError(f"Invalid task_id: {task_id}")
    task = CREATIVE_TASKS[task_id]
    guidance = task["guidance"]
    initial_inventory = task["initial_inventory"]
    goal = task["goal"]
    env = CreativeTask(**kwargs, guidance=guidance, initial_inventory=initial_inventory, goal=goal)
    return env

def _make_construction(**kwargs):
    task_id = kwargs['task_id']
    print(CONSTRUCTION_TASKS)
    if task_id not in CONSTRUCTION_TASKS:
        raise ValueError(f"Invalid task_id: {task_id}")
    task = CONSTRUCTION_TASKS[task_id]
    goal = task["goal"]

    blueprint_file_name = task_id + "_blueprint.png"
    baseline_file_name = task_id + "_baseline.png"
    env = ConstructionTask(blueprint_file_name=blueprint_file_name, baseline_file_name=baseline_file_name, goal=goal, **kwargs)
    return env

def _make_stage_performance(**kwargs):
    task_id = kwargs['task_id']
    print(STAGE_PERFORMANCE_TASKS)
    if task_id not in STAGE_PERFORMANCE_TASKS:
        raise ValueError(f"Invalid task_id: {task_id}")
    task = STAGE_PERFORMANCE_TASKS[task_id]
    agent_names = task["agent_names"]
    critical_point = task["critical_point"]
    initial_inventory = task["initial_inventory"]
    personalities = task["personalities"]
    script = task["script"]
    system_instructions = task["system_instructions"]
    env = StagePerformanceTask(agent_names=agent_names, 
                               critical_point=critical_point, 
                               initial_inventory=initial_inventory,
                               personalities=personalities,
                               script=script,
                               system_instructions=system_instructions,
                               **kwargs)
    return env
    # print(task["agent_names"])
    # print(task["critical_point"][0])
    # print(task["critical_point"][0][2])
    # print(type(task["agent_names"]))
    # print(type(task["critical_point"][0]))
    # print(type(task["critical_point"][0][2]))
