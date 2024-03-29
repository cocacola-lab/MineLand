import sys
sys.path.append('../..')

import mineland
import numpy as np
import mineland
from PIL import Image
from mineland.utils import base64_to_image

# ===== Make =====
mindland = mineland.make(
    # task_id="playground",
    task_id="survival_1_days",

    agents_count=1,
    agents_config=[{"name": f"MineflayerBot{i}"} for i in range(1)],

    image_size=(180, 320),
)

obs = mindland.reset()

agents_count = len(obs)
agents_name = [obs[i]['name'] for i in range(agents_count)]
agents_resume_action = [{ "type": mineland.Action.RESUME, "code": "" } for _ in range(agents_count)]

loc = [ -12, 123, 108, 0, -0.7 ]

for i in range(5000):

    if i == 0:
        mindland.env.bridge.addCamera("test")
    
    if i > 0 and i % 5 == 0:
        loc[3] += 0.1
        mindland.env.bridge.updateCameraLocation("test", [loc[0], loc[1], loc[2]], loc[3], loc[4])
        # mindland.env.bridge.addCameraLocation("test", [0, 0, 0], 0.2, 0)
        rgb = mindland.env.bridge.getCameraView("test")
        rgb = base64_to_image(rgb, 320, 180)
        img = np.transpose(rgb, (1, 2, 0))
        pil_img = Image.fromarray(img)
        pil_img.save(f'output_camera_image.jpg')

    if i == 0:
        act = agents_resume_action
    
    obs, code_info, event, done, task_info = mindland.step(action=act)