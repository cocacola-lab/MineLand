import mineland
from PIL import Image
from mineland.utils import base64_to_image
import numpy as np
import math
import matplotlib.pyplot as plt
def pause():
    print("Press any key to continue")
    line = input()
    print("Pressed.")
    print("Continuing...")
    return get_resume_action()

def get_resume_action():
    return mineland.Action.no_op(1)

def print_obs(obs):
    for i in range(len(obs)):
        print(f'Bot#{obs[i]["name"]}: {obs[i]}')

def print_code_info(code_info):
    for i in range(len(code_info)):
        if code_info[i] is not None:
            print(f'Bot#{code_info[i]["name"]}: {code_info[i]}')

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
    pil_img.save(f'output_camera_image.jpg')


def adjust_camera() :
    global is_adjusting_camera
    while True : 
        print('''
Now that you can see the image of the camera and blueprint, adjust the camera position and angle to make the camera picture look as similar as possible to the blueprint.
Input format: d_forward d_up d_right d_yaw d_pitch.
The value you enter will change the location property of the current camera.
If you don't want to continue adjusting the camera this rount, input 'ok'.
If you don't want to continue adjusting the camera any more, input 'stop'.
            ''')
        show_image()
        content = input()
        if content == 'ok': break
        if content == 'stop': 
            is_adjusting_camera=False
            break
        d_loc = [float(i) for i in content.strip().split()]
        if len(d_loc) != 5 : 
            continue
        print(d_loc[0], d_loc[1], d_loc[2], d_loc[3], d_loc[4])
        mland.move_camera( [d_loc[0], d_loc[1], d_loc[2]], d_loc[3], d_loc[4])

         

# ===== Make =====
mland = mineland.make(
    task_id="construction_task_1",
    agents_count = 1,
    enable_mineclip=True,
    mineclip_ckpt_path='./mineclip_ckpt/avg.pth',
)

obs = mland.reset()

agents_count = len(obs)
agents_name = [obs[i]['name'] for i in range(agents_count)]

is_adjusting_camera = True

for i in range(5000):
    if i > 0 and i % 20 == 0:
        print("task_info: ", task_info)
        show_image()
        # if(is_adjusting_camera) : 
        #     adjust_camera()
        # print("mineclip score: ", mland.get_score_by_mineclip())

    act = get_resume_action()

    obs, code_info, event, done, task_info = mland.step(action=act)

    assert task_info is not None, "task_info should not be None"

    if done:
        print(" ===== Task Done! ===== ")
        print("task_info: ", task_info)
        break

    # TODO: 任务tick 和 服务器log tick 不一致的问题（可能是任务tick为时间tick，而不是服务器log tick）
