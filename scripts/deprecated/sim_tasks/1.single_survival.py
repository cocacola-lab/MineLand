import sys
sys.path.append('../..')

import mineland


def pause():
    print("Press any key to continue")
    line = input()
    print("Pressed.")
    print("Continuing...")
    return get_resume_action()

def get_resume_action():
    return [
        { "type": mineland.Action.RESUME, "code": "" },
    ]
def get_eat_action() :
    code = '''
        await bot.chat('/give @a apple 10')
        const foodItem = bot.inventory.items().find(item => item.name.includes('apple'));
        console.log(bot.inventory)
        console.log(bot.inventory.items())
        if (foodItem) {
            // 把食物移动到手中
            bot.equip(foodItem, 'hand', (err) => {
            if (err) {
                console.log('Error equipping food:', err);
                return;
            }

            
            
            });
            // 吃食物
            bot.consume((err) => {
                if (err) {
                console.log('Error consuming food:', err);
                } else {
                console.log('Food has been consumed.');
                }
            });
            console.log("Eating finished!")
        } else {
            console.log('No food found in inventory.');
        }
        ''' 
    return [
        { "type": mineland.Action.NEW, "code": code },
    ]
def print_obs(obs):
    for i in range(len(obs)):
        print(f'Bot#{obs[i]["name"]}: {obs[i]}')

def print_code_info(code_info):
    for i in range(len(code_info)):
        if code_info[i] is not None:
            print(f'Bot#{code_info[i]["name"]}: {code_info[i]}')

# ===== Make =====
mindland = mineland.make(
    task_id="survival_1_days",
    agents_count = 1,

    is_printing_server_info=True,
    is_printing_mineflayer_info=True,

    enable_auto_pause=False,
)

obs = mindland.reset()

agents_count = len(obs)
agents_name = [obs[i]['name'] for i in range(agents_count)]
agents_chat_action = [{ "type": mineland.Action.NEW, "code": "bot.chat('I am here')" }]
for i in range(5000):

    if i > 0 and i % 20 == 0:
        print("current_tick: ", obs[0].tick)
        print("task_info: ", task_info)

    

    act = get_resume_action()
    if i > 0 and i % 10 == 0:
        act = agents_chat_action
    # if i > 0 and i % 50 == 0:
    #     print("eating...")
    #     act = get_eat_action()

    obs, code_info, event, done, task_info = mindland.step(action=act)

    assert task_info is not None, "task_info should not be None"

    if done:
        print(" ===== Task Done! ===== ")
        print("task_info: ", task_info)
        break

    # TODO: 任务tick 和 服务器log tick 不一致的问题（可能是任务tick为时间tick，而不是服务器log tick）
