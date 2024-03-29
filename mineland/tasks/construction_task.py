from mineland.sim.data.task_info import TaskInfo
from mineland.utils import base64_to_image

from .base_task import BaseTask
from .utils import *
import os
import cv2
import numpy as np
import base64
import math
from PIL import Image

class ConstructionTask(BaseTask):
    def __init__(
        self,
        blueprint_file_name:str,
        baseline_file_name:str,
        **kwargs,
    ):
        self.blueprint_file_name = blueprint_file_name
        self.baseline_file_name = baseline_file_name
        kwargs["world_type"] = "construction"
        self.goal = f'agent(s) need to build a construction like the picture \n '
        self.guidance = f'this is creative mode, you can use any system instruction, such as /give oak_log, to give yourself some oak logs'
        
        picture_path = os.path.join(os.path.dirname(__file__), 'description_files')
        picture_path = os.path.join(picture_path, 'construction_tasks_pictures')
        
        self.blueprint_file_path = os.path.join(picture_path, self.blueprint_file_name)
        self.baseline_file_path = os.path.join(picture_path, self.baseline_file_name)
        self.initiate_picture_message()
        super().__init__(**kwargs)
        print(f'agent(s) need to build a construction like the picture \n ')
    
    def reset(self):
        obs = self.env.reset()
        # self.server_manager.execute("gamemode creative")
        self.env.bridge.addCamera("construction_camera")
        return obs
    
    def initiate_picture_message(self) :
        # baseline score
        baseline_img = cv2.imread(self.baseline_file_path, cv2.IMREAD_COLOR)
        blueprint_img = cv2.imread(self.blueprint_file_path, cv2.IMREAD_COLOR)
        print(self.baseline_file_path)
        baseline_img = np.transpose(baseline_img, (2, 0, 1))
        blueprint_img = np.transpose(blueprint_img, (2, 0, 1))
        self.baseline_score = get_image_similarity_by_orb(baseline_img, blueprint_img)
        
        # blueprint_img_base64
        blueprint_img_file = open(self.blueprint_file_path, 'rb')
        self.blueprint_img_base64 = base64.b64encode(blueprint_img_file.read())
        self.blueprint_img_np = blueprint_img
        # check image 
        # rgb = base64_to_image(self.blueprint_img_base64, 320, 180)
        # img = np.transpose(rgb, (1, 2, 0))
        # pil_img = Image.fromarray(img)
        # pil_img.show()
        # pil_img.save(f'output_camera_image.jpg')

        # image_files
        print("baseline is : " + str(self.baseline_score))
        pass
    
    def move_camera(self, pos, yaw, pitch) :
        self.env.bridge.moveCamera("construction_camera", pos, yaw, pitch)
    
    
    
    def get_blueprint_base64(self) :
        return self.blueprint_img_base64
    
    def get_blueprint_np(self) :
        rgb = base64_to_image(self.blueprint_img_base64, 320, 180)
        return rgb
    
    def get_camera_view(self) :
        
        return self.env.bridge.getCameraView("construction_camera")

    def get_score(self) :
        camera_view = self.get_camera_view()
        camera_view = base64_to_image(camera_view, 320, 180)
        score = get_image_similarity_by_orb(camera_view, self.blueprint_img_np) / self.baseline_score
        return score
    
    def step(self, action):
        obs, code_info, events, done, task_info = self.env.step(action)

        task_info = TaskInfo(
            task_id=self.task_id,
            score = self.get_score(),
            is_success=False,
            is_failed=False,
            goal=self.goal,
            guidance=self.guidance,
        )

        return obs, code_info, events, False, task_info
