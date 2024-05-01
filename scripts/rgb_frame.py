#
# You can run this script to get the RGB frame of the game.
# The RGB frame will be saved
#     as output_image_MineflayerBot0.jpg and output_image_MineflayerBot1.jpg
#     every 0.25 seconds.
# You can open the image and see the visual information of the agents.
#

import mineland
from PIL import Image
import numpy as np
import base64
import io
import cv2

AGENTS_COUNT = 2
AGENTS_CONFIG = [{"name": f"MineflayerBot{i}"} for i in range(AGENTS_COUNT)]

def get_resume_action():
    return [mineland.Action(type=mineland.Action.RESUME, code="") for _ in range(AGENTS_COUNT)]

def get_continuous_jump_action():
    return [mineland.Action(type=mineland.Action.NEW, code="bot.setControlState('jump', true)") for _ in range(AGENTS_COUNT)]

def save_image(obs):
    for i in range(len(obs)):
        img = np.transpose(obs[i]['rgb'], (1, 2, 0))
        pil_img = Image.fromarray(img)
        pil_img.save(f'output_image_{AGENTS_CONFIG[i]["name"]}.jpg')

# ===== Make =====
mland = mineland.make(
    task_id="harvest_1_oak_log", # no any task

    agents_count=AGENTS_COUNT,
    agents_config=AGENTS_CONFIG,

    image_size=(180, 320),
)

obs = mland.reset()
for i in range(5000):
    act = get_resume_action()
    if i == 0:
        act = get_continuous_jump_action()
        print('The program is running. You can check the output_image_*.jpg in the working directory.')
    obs, code_info, event, done, task_info = mland.step(action=act)
    save_image(obs)
