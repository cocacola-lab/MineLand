
#
# In this example, you can connect to the game server, and build a construction to check MineLand's output.
#

import mineland
from PIL import Image
from mineland.utils import base64_to_image
import numpy as np
import matplotlib.pyplot as plt

def show_image():
    rgb = mland.get_camera_view()
    rgb = base64_to_image(rgb, 320, 180)
    img1 = np.transpose(rgb, (1, 2, 0))
    img2 = mland.get_blueprint_np()
    img2 = np.transpose(img2, (1, 2, 0))
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.imshow(img1)
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(img2)
    plt.axis('off')  # 关闭坐标轴
    plt.show()
    pil_img = Image.fromarray(img1)
    pil_img.save(f'output_image_camera.jpg')

mland = mineland.make(
    task_id="construction_task_1",
    agents_count = 1,
    # enable_mineclip=True,
    # mineclip_ckpt_path='./mineclip_ckpt/avg.pth',
)

obs = mland.reset()

agents_count = len(obs)
agents_name = [obs[i]['name'] for i in range(agents_count)]

for i in range(5000):
    if i > 0 and i % 20 == 0:
        print("task_info: ", task_info)
        show_image()

    act = mineland.Action.no_op(agents_count)
    obs, code_info, event, done, task_info = mland.step(action=act)

    # Construction Task has no end, so we don't need to check done