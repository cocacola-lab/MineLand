#
# You can run this script directly to test the task.
#

create_wooden_pickaxe_using_logs = '''
// 将橡木原木转换为木板
let plankRecipe = bot.recipesAll(mcData.itemsByName['oak_planks'].id, null, null)[0];
if (!plankRecipe) {
    console.log("无法找到木板的配方");
    return;
}
await bot.craft(plankRecipe, 10, null); // 每个橡木原木可以制作4个木板

// 将木板转换为木棍
let stickRecipe = bot.recipesAll(mcData.itemsByName['stick'].id, null, null)[0];
if (!stickRecipe) {
    console.log("无法找到木棍的配方");
    return;
}
await bot.craft(stickRecipe, 3, null); // 每2个木板可以做4个木棍

// 制作工作台
let craftingTableRecipe = bot.recipesFor(mcData.itemsByName['crafting_table'].id)[0];
if (!craftingTableRecipe) {
    console.log("无法找到工作台的配方");
    return;
}
await bot.craft(craftingTableRecipe, 1, null);

// 放置工作台
let craftingTableItem = bot.inventory.findInventoryItem('crafting_table', null);
if (!craftingTableItem) {
    console.log("没有找到工作台");
    return;
}
await bot.equip(craftingTableItem, 'hand');
await bot.placeBlock(bot.blockAtCursor(), new Vec3(0, 1, 0));
'''

create_wooden_pickaxe_using_logs_2 = '''
let craftingTable = bot.findBlock({
  point: bot.entity.position,
  matching: mcData.blocksByName.crafting_table.id,
  maxDistance: 32, // 搜索范围，这里设置为64个方块
  count: 1,        // 找到的工作台数量
});

if (craftingTable) {
  console.log('找到了工作台:', craftingTable.position);
} else {
  console.log('附近没有工作台');
}

// 制作木稿（木制稿）
let woodenPickaxeRecipe = bot.recipesAll(mcData.itemsByName['wooden_pickaxe'].id, null, craftingTable)[0];
if (!woodenPickaxeRecipe) {
    console.log("无法找到木稿的配方");
    return;
}
await bot.craft(woodenPickaxeRecipe, 1, bot.blockAtCursor());
'''

import sys
sys.path.append('../..')

import mineland
import numpy as np
import mineland
from PIL import Image

def pause():
    print("Press any key to continue")
    line = input()
    print("Pressed.")
    print("Continuing...")
    return agents_resume_action

def get_next_action_from_stdin():
    actions = []
    for i in range(len(agents_name)):
        print(f" ===== Enter next action code for {agents_name[i]} (use \"END\" to stop entering): =====")
        action_code = ""
        while True:
            line = input()
            if line.startswith("END"):
                break
            action_code += line + '\n'
        action_code += "\n"
        if action_code.startswith('END'):
            actions.append({ "type": mineland.Action.RESUME, "code": "" })
        else:
            actions.append({ "type": mineland.Action.NEW, "code": action_code })
    print(" ===== Action Begin ===== ")
    print(actions)
    print(" ===== Action End ===== ")
    return actions

def print_obs(obs):
    for i in range(len(obs)):
        print(f'Bot#{obs[i]["name"]}: {obs[i]}')

def print_code_info(code_info):
    for i in range(len(code_info)):
        if code_info[i] is not None:
            print(f'Bot#{code_info[i]["name"]}: {code_info[i]}')

def save_image(obs):
    for i in range(len(obs)):
        print("img.shape: ", obs[i]['rgb'].shape)
        img = np.transpose(obs[i]['rgb'], (1, 2, 0))
        pil_img = Image.fromarray(img)
        pil_img.save(f'output_image_{agents_name[i]}.jpg')

# ===== Make =====
mindland = mineland.make(
    task_id="harvest_1_dirt",
    mode='competitive',
    agents_count=2,
    agents_config=[{"name": f"MineflayerBot{i}"} for i in range(2)],
    is_printing_server_info=True,
    is_printing_mineflayer_info=True,
)

obs = mindland.reset()

agents_count = len(obs)
agents_name = [obs[i]['name'] for i in range(agents_count)]
agents_resume_action = [{ "type": mineland.Action.RESUME, "code": "" } for _ in range(agents_count)]

for i in range(5000):

    # print("inventory.name:", obs[0]['inventory']['name'])
    # print("inventory.quantity:", obs[0]['inventory']['quantity'])
    # if i == 0:
    #     act = [{ "type": mineland.Action.NEW, "code": create_wooden_pickaxe_using_logs } for _ in range(agents_count)]
    # elif i == 25:
    #     act = [{ "type": mineland.Action.NEW, "code": create_wooden_pickaxe_using_logs_2 } for _ in range(agents_count)]
    # else:
    act = agents_resume_action
    
    # print("action:", act[0])

    obs, code_info, event, done, task_info = mindland.step(action=act)

    assert task_info is not None, "task_info should not be None"

    if done:
        print(" ===== Task Done! ===== ")
        print("task_info: ", task_info)
        break

    # TODO: 任务tick 和 服务器log tick 不一致的问题（可能是任务tick为时间tick，而不是服务器log tick）
