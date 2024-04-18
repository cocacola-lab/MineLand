import gymnasium as gym
import threading
import time

from typing import Tuple, List, Dict, Union

from mineland.sim.data.task_info import TaskInfo

from .server_manager import ServerManager
from .mineflayer_manager import MineflayerManager
from .sound_system import SoundSystem
from .bridge import Bridge
from .data.action import Action
from .data.observation import Observation
from .data.code_info import CodeInfo
from .data.event import Event
from ..utils import green_text

std_print = print
def print(*args, end='\n'):
    text = [green_text(str(arg)) for arg in args]
    std_print("[MineLand]", *text, end=end)

class MineLand(gym.Env):
    def __init__(
        self,

        agents_count: int,
        agents_config: List[Dict[str, Union[int, str]]] = None,

        world_type: str = "normal",

        ticks_per_step: int = 5,
        enable_auto_pause: bool = False,
        enable_sound_system: bool = False,

        server_host: str = None,
        server_port: int = None,
        image_size: Tuple[int, int] = (144, 256),
        is_printing_server_info: bool = True,
        is_printing_mineflayer_info: bool = True,

        headless: bool = False,
    ):

        print("MineLand Simulator is initializing...")

        # ===== Save Config =====
        self.ticks_per_step = ticks_per_step
        self.enable_auto_pause = enable_auto_pause
        self.enable_sound_system = enable_sound_system

        self.agents_count = agents_count
        self.agents_config = agents_config
        self.image_size = image_size

        self.is_reset = False
        self.is_closed = False

        # ===== Default Config =====
        if self.agents_config is None:
            self.agents_config = [{"name": f"MineflayerBot{i}"} for i in range(agents_count)]
        
        # ===== Server =====
        if server_host is None:
            self.server_host = "localhost"
            self.server_port = 25565
            print("Starting server...")
            self.server_manager = ServerManager(is_printing_server_info=is_printing_server_info)
            if world_type == "normal":
                self.server_manager.select_to_normal_world()
            else : 
                self.server_manager.select_to_construction_world()
            self.server_manager.start()
            self.server_manager.wait_for_running()
            print("Server started.")
        else:
            self.server_host = server_host
            self.server_port = server_port
            self.server_manager = None
            print("MineLand will connect to the existing server by host:", server_host, "port:", server_port)
            self.enable_auto_pause = False
            print("AUTO PAUSE mode is disabled because you are connecting to an existing server.")

        # ===== Server Settings =====

        # Pause
        if self.server_manager is not None and self.enable_auto_pause:
            self.server_manager.execute("pause")
            print("Server has been paused.")
        else:
            print("Pause is disabled!")

        # Ensure that the username exists
        for i in range(agents_count):
            if "name" not in self.agents_config[i]:
                self.agents_config[i]["name"] = f"MineflayerBot{i}"

        if self.server_manager is not None:
            # Give all bots op permission
            for i in range(agents_count):
                self.server_manager.execute(f"op {self.agents_config[i]['name']}")

        # Wait for start
        time.sleep(3)

        # ===== Mineflayer =====
        print("Mineflayer is starting.")
        mineflayer_manager = MineflayerManager(is_printing_mineflayer_info=is_printing_mineflayer_info)
        mineflayer_manager.start()
        mineflayer_manager.wait_for_running()
        # time.sleep(1)
        print("Mineflayer started.")

        # ===== Sound System =====
        if self.enable_sound_system:
            print("Sound System is enabled.")
            self.sound_system = SoundSystem(agents_count)
            self.sound_last_tick = 0
        
        # ===== Bridge =====
        self.bridge = Bridge(
            agents_count=self.agents_count,
            agents_config=self.agents_config,
            ticks_per_step=self.ticks_per_step,
            enable_auto_pause=self.enable_auto_pause,
            image_size=self.image_size,
            minecraft_server_host=self.server_host,
            minecraft_server_port=self.server_port,
            mineflayer_manager=mineflayer_manager,
            server_manager=self.server_manager,
            headless=headless,
        )
        
        print("MineLand Simulator is initialized.")

    def reset(self) -> List[Observation]:
        print("Starting reset... This may take a few seconds.")
        obs = self.bridge.reset()

        if self.server_manager is not None:
            # Clear the inventory of all bots
            self.server_manager.execute("clear @a")

            # Set agents' gamemode to survival
            for i in range(self.agents_count):
                self.server_manager.execute(f"gamemode survival {self.agents_config[i]['name']}")
        
            self.server_manager.execute("tp @e[type=!minecraft:player] 0 -100 0")

            if self.enable_auto_pause:
                # Runtick 20 ticks (1 second) to execute all preset commands
                self.server_manager.execute("runtick 20")
                self.server_manager.is_runtick_finished = False # Force server to wait 20 ticks, then step

        print("Reset finished. MineLand Simulator is started.")
        if self.enable_auto_pause:
            print("You enabled AUTO PAUSE mode, the minecraft game will run for a certain ticks when you call the step() function.")
        else:
            print("You didn't enable AUTO PAUSE mode, the minecraft game is running now.")

        self.is_reset = True

        return obs

    def step(
        self,
        action: List[Action]
    ) -> Tuple[List[Observation], List[CodeInfo], List[Event], bool, TaskInfo]:
        """Step the environment.

        Args:
            action (List[Action]): The list of (action types and codes) that needs to be executed.

        Returns:
            Tuple[List[Observation], List[CodeInfo], List[Event], bool, TaskInfo]: The result of step.
        """
        if not self.is_reset:
            raise RuntimeError("You must call reset() before calling step().")

        if self.server_manager is not None and self.enable_auto_pause:
                self.server_manager.wait_for_runtick_finish()

        obs, code_info, event = self.bridge.step(action)

        if self.enable_sound_system:
            for i in range(self.agents_count):
                obs[i].sound = self.sound_system.get(i, self.sound_last_tick, obs[0].tick, event[i])
            self.sound_last_tick = obs[0].tick

        return obs, code_info, event, False, None
    
    def add_an_agent(self, config: Dict[str, Union[int, str]] = None):
        if not self.is_reset:
            raise RuntimeError("You must call reset() before calling step().")

        self.agents_count += 1

        if config is None:
            config = {"name": f"MineflayerBot{self.agents_count - 1}"}
        if 'name' not in config:
            config['name'] = f"MineflayerBot{self.agents_count - 1}"
        self.agents_config.append(config)

        if self.server_manager is not None:
            self.server_manager.execute(f"op {config['name']}")
            self.server_manager.execute(f"gamemode survival {config['name']}")
        
        if self.enable_sound_system:
            assert False, "TODO: Sound System supports for adding agents."

        self.bridge.add_an_agent(config)
    
    def disconnect_an_agent(self, name: str):
        self.bridge.disconnect_an_agent(name)

    def render(self, mode: str = 'human'):
        pass

    def close(self):
        if not self.is_reset:
            raise RuntimeError("You must call reset() before calling step().")
        
        if self.is_closed:
            return
        self.bridge.close()
        if self.server_manager is not None:
            self.server_manager.shutdown()
        return
