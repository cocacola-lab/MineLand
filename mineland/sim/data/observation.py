from typing import List, Dict
from ...utils import base64_to_image
from pydub import AudioSegment

class Observation:
    """Observation of the environment.
    """    

    def __init__(
        self,

        # ===== Basic Attributes =====
        name: str,

        # ===== RGB Frame =====
        rgb_height: int,
        rgb_width: int,
        rgb: str, # Constructor convert rgb from base64 to np.ndarray
                  # Be careful! The origin rgb may be an empty string, like "".
        
        # ===== Equipment =====
        equipment: Dict, # MineDojo-Style
        equip: Dict,     # MineLand-Style

        # ===== Inventory =====
        inventory_full_slot_count: int,
        inventory_empty_slot_count: int,
        inventory_slot_count: int,
        inventory_all: List,
        inventory: Dict,

        # ===== Voxels =====
        voxels:Dict,
        # ===== Face Vector =====
        face_vector:List,
        # ===== Life Statistics =====
        life_stats: Dict,
        
        # ===== Location Statistics =====
        location_stats: Dict,

        # ===== Time =====
        tick: int,
        time: int,
        day: int,
        age: int,
        
        # ===== World =====
        difficulty: str,

        # ===== Physical Attributes =====
        control_state: Dict,

        # ===== Event =====
        event: List,

        # ===== Target Entities =====
        target_entities: List,

        # ===== Sound =====
        sound: AudioSegment
    ):
        """Construct an observation.

        Args:
            tick (int): The current tick of the environment.
                        The tick will be reset to 0, when the environment is reset.

            time (int): The time of the day.
                        The range of time is [0, 24000).

            day (int): The day of the world.
        """        

        local_vars = locals()
        for name, value in local_vars.items():
            
            # === RGB Frame ===
            if name == 'rgb':
                setattr(self, "rgb_base64", value)
                rgb = base64_to_image(value, rgb_width, rgb_height)
                setattr(self, name, rgb)
            
            # === Self ===
            elif name == "self":
                continue
                
            # === Others ===
            else:
                setattr(self, name, value)
            
    
    def __str__(self) -> str:
        result = "Observation (\n"

        for name, value in self.__dict__.items():
            # === RGB Frame ===
            if name == "rgb":
                result += f"    {name}: {value.shape}\n"
            
            # === Base64 ===
            elif name == "rgb_base64":
                continue
            
            # === Dict ===
            elif isinstance(value, dict):
                dict_str = "    {\n"
                for k, v in value.items():
                    dict_str += f"         {k}: {v}\n"
                dict_str += "    }"
                result += f"    {name}: {dict_str}\n"
            
            # === Others ===
            else:
                result += f"    {name}: {value}\n"

        result += ")"
        return result
    
    def __getitem__(self, key):
        return getattr(self, key, None)
    
    @classmethod
    def from_json(cls, json):
        if json == {}:
            return None
        return cls(**json)
    
    @classmethod
    def from_json_list(cls, json_list):
        return [(cls.from_json(json) if json is not None else None) for json in json_list]
    