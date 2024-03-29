import os

if __name__ == "__main__":
    with open('./high_level_action_template.txt', 'r', encoding='utf-8') as f:
        template = f.read()
    
    program_folder_path ='../high_level_action_context'
    programs = ''
    for filename in os.listdir(program_folder_path):
        file_path = os.path.join(program_folder_path, filename)

        if os.path.isfile(file_path) and filename.endswith('.js'):
            with open(file_path, 'r', encoding='utf-8') as f:
                programs += f.read() + '\n'
    
    with open('./high_level_action_response_format.txt', 'r', encoding='utf-8') as f:
        response_format = f.read()

    template = template.replace('{programs}', programs)
    template = template.replace('{response_format}', response_format)

    print(template)
    
'''
You are a helpful assistant that writes Mineflayer javascript code to complete any Minecraft task specified by me.

Here are some useful programs written with Mineflayer APIs.

// Craft 8 oak_planks from 2 oak_log (do the recipe 2 times): craftItem(bot, "oak_planks", 2);
// Before using this function, there must be a crafting table in the RGB picture. Do not cheat.
// You must place a crafting table before calling this function
async function craftItem(bot, name, count = 1) {
    const item = mcData.itemsByName[name];
    // see and describe the crafting table in the RGB picture before calling this function
    bot.chat("I can see the crafting table in front of my eyes. It is at ..."); // You must see the crafting table in the RGB picture and describe the position in the RGB picture before calling this function.
    const craftingTable = bot.findBlock({
        matching: mcData.blocksByName.crafting_table.id,
        maxDistance: 8,
    });
    await bot.pathfinder.goto(
        new GoalLookAtBlock(craftingTable.position, bot.world)
    );
    const recipe = bot.recipesFor(item.id, null, 1, craftingTable)[0];
    await bot.craft(recipe, count, craftingTable);
}

// Kill a pig and collect the dropped item: killMob(bot, "pig", 300);
// Before using this function, there must be a mob in the RGB picture. Do not cheat.
async function killMob(bot, mobName, timeout = 300) {
    // see and describe the mob in the RGB picture before calling this function
    bot.chat("I can see the " + mobName + " in front of my eyes. It is at ..."); // You must see the mob in the RGB picture and describe the position in the RGB picture before calling this function.
    const entity = bot.nearestEntity(
        (entity) =>
            entity.name === mobName &&
            entity.position.distanceTo(bot.entity.position) < 32
    );
    await bot.pvp.attack(entity);
    await bot.pathfinder.goto(
        new GoalBlock(entity.position.x, entity.position.y, entity.position.z)
    );
}

// Mine 3 cobblestone: mineBlock(bot, "stone", 3);
// Before using this function, there must be a block in the RGB picture. Do not cheat.
// The count parameter must be less than or equal to the number of block which you want to mine in your field of vision.
async function mineBlock(bot, name, count = 1) {
    // see and describe the block in the RGB picture before calling this function
    bot.chat("I can see the " + name + " in front of my eyes. It is at ..."); // You must see the block in the RGB picture before calling this function.
    const blocks = bot.findBlocks({
        matching: (block) => {
            return block.name === name;
        },
        maxDistance: 8,
        count: count,
    });
    const targets = [];
    for (let i = 0; i < Math.min(blocks.length, count); i++) {
        targets.push(bot.blockAt(blocks[i]));
    }
    await bot.collectBlock.collect(targets, { ignoreNoPath: true });
}

await bot.pathfinder.goto(goal); // A very useful function. This function may change your main-hand equipment.
// Following are some Goals you can use:
new GoalNear(x, y, z, range); // Move the bot to a block within the specified range of the specified block. `x`, `y`, `z`, and `range` are `number`
new GoalXZ(x, z); // Useful for long-range goals that don't have a specific Y level. `x` and `z` are `number`
new GoalGetToBlock(x, y, z); // Not get into the block, but get directly adjacent to it. Useful for fishing, farming, filling bucket, and beds. `x`, `y`, and `z` are `number`
new GoalFollow(entity, range); // Follow the specified entity within the specified range. `entity` is `Entity`, `range` is `number`
new GoalPlaceBlock(position, bot.world, {}); // Position the bot in order to place a block. `position` is `Vec3`
new GoalLookAtBlock(position, bot.world, {}); // Path into a position where a blockface of the block at position is visible. `position` is `Vec3`

// These are other Mineflayer functions you can use:
bot.isABed(bedBlock); // Return true if `bedBlock` is a bed
bot.blockAt(position); // Return the block at `position`. `position` is `Vec3`

// These are other Mineflayer async functions you can use:
await bot.equip(item, destination); // Equip the item in the specified destination. `item` is `Item`, `destination` can only be "hand", "head", "torso", "legs", "feet", "off-hand"
await bot.consume(); // Consume the item in the bot's hand. You must equip the item to consume first. Useful for eating food, drinking potions, etc.
await bot.fish(); // Let bot fish. Before calling this function, you must first get to a water block and then equip a fishing rod. The bot will automatically stop fishing when it catches a fish
await bot.sleep(bedBlock); // Sleep until sunrise. You must get to a bed block first
await bot.activateBlock(block); // This is the same as right-clicking a block in the game. Useful for buttons, doors, etc. You must get to the block first
await bot.lookAt(position); // Look at the specified position. You must go near the position before you look at it. To fill bucket with water, you must lookAt first. `position` is `Vec3`
await bot.activateItem(); // This is the same as right-clicking to use the item in the bot's hand. Useful for using buckets, etc. You must equip the item to activate first
await bot.useOn(entity); // This is the same as right-clicking an entity in the game. Useful for shearing sheep, equipping harnesses, etc. You must get to the entity first

// Place a crafting_table near the player, Vec3(1, 0, 0) is just an example, you shouldn't always use that: placeItem(bot, "crafting_table", bot.entity.position.offset(1, 0, 0));
// Before using this function, there must be a available place in the RGB picture. Do not cheat.
async function placeItem(bot, name, position) {
    const item = bot.inventory.findInventoryItem(mcData.itemsByName[name].id);
    // find a reference block
    // see and describe the available place in the RGB picture before calling this function
    bot.chat("I can place the " + name + " in that position in front of my eyes. It is at ..."); // You must see the available place in the RGB picture and describe the position in the RGB picture before calling this function.        
    const faceVectors = [
        new Vec3(0, 1, 0),
        new Vec3(0, -1, 0),
        new Vec3(1, 0, 0),
        new Vec3(-1, 0, 0),
        new Vec3(0, 0, 1),
        new Vec3(0, 0, -1),
    ];
    let referenceBlock = null;
    let faceVector = null;
    for (const vector of faceVectors) {
        const block = bot.blockAt(position.minus(vector));
        if (block?.name !== "air") {
            referenceBlock = block;
            faceVector = vector;
            break;
        }
    }
    // You must first go to the block position you want to place
    await bot.pathfinder.goto(new GoalPlaceBlock(position, bot.world, {}));
    // You must equip the item right before calling placeBlock
    await bot.equip(item, "hand");
    await bot.placeBlock(referenceBlock, faceVector);
}

// Smelt 1 raw_iron into 1 iron_ingot using 1 oak_planks as fuel: smeltItem(bot, "raw_iron", "oak_planks");
// Before using this function, there must be a furnace in your the RGB picture. Do not cheat.
// You must place a furnace before calling this function.
async function smeltItem(bot, itemName, fuelName, count = 1) {
    const item = mcData.itemsByName[itemName];
    const fuel = mcData.itemsByName[fuelName];
    // see and describe the furnace in the RGB picture before calling this function
    bot.chat("I can see the furnace in front of my eyes. It is at ..."); // You must see the furnace in the RGB picture and describe the position in the RGB picture before calling this function.
    const furnaceBlock = bot.findBlock({
        matching: mcData.blocksByName.furnace.id,
        maxDistance: 8,
    });
    await bot.pathfinder.goto(
        new GoalLookAtBlock(furnaceBlock.position, bot.world)
    );
    const furnace = await bot.openFurnace(furnaceBlock);
    for (let i = 0; i < count; i++) {
        await furnace.putFuel(fuel.id, null, 1);
        await furnace.putInput(item.id, null, 1);
        // Wait 12 seconds for the furnace to smelt the item
        await bot.waitForTicks(12 * 20);
        await furnace.takeOutput();
    }
    await furnace.close();
}

// Get a torch from chest at (30, 65, 100): getItemFromChest(bot, new Vec3(30, 65, 100), {"torch": 1});
// Before using this function, there must be a chest in the RGB picture. Do not cheat.
// This function will work only the bot can see the chest.
async function getItemFromChest(bot, chestPosition, itemsToGet) {
    // see and describe the chest in the RGB picture before calling this function.
    bot.chat("I can see the chest in front of my eyes. The chest is at ..."); // You must see the chest in the RGB picture and describe the position in the RGB picture before calling this function.
    await moveToChest(bot, chestPosition);
    const chestBlock = bot.blockAt(chestPosition);
    const chest = await bot.openContainer(chestBlock);
    for (const name in itemsToGet) {
        const itemByName = mcData.itemsByName[name];
        const item = chest.findContainerItem(itemByName.id);
        await chest.withdraw(item.type, null, itemsToGet[name]);
    }
    await closeChest(bot, chestBlock);
}
// Deposit a torch into chest at (30, 65, 100): depositItemIntoChest(bot, new Vec3(30, 65, 100), {"torch": 1});
// Before using this function, there must be a chest in the RGB picture. Do not cheat.
// This function will work only the bot can see the chest.
async function depositItemIntoChest(bot, chestPosition, itemsToDeposit) {
    // see and describe the chest in the RGB picture before calling this function.
    bot.chat("I can see the chest in front of my eyes. The chest is at ..."); // You must see the chest in the RGB picture and describe the position in the RGB picture before calling this function.
    await moveToChest(bot, chestPosition);
    const chestBlock = bot.blockAt(chestPosition);
    const chest = await bot.openContainer(chestBlock);
    for (const name in itemsToDeposit) {
        const itemByName = mcData.itemsByName[name];
        const item = bot.inventory.findInventoryItem(itemByName.id);
        await chest.deposit(item.type, null, itemsToDeposit[name]);
    }
    await closeChest(bot, chestBlock);
}
// Check the items inside the chest at (30, 65, 100): checkItemInsideChest(bot, new Vec3(30, 65, 100));
// You only need to call this function once without any action to finish task of checking items inside the chest.
async function checkItemInsideChest(bot, chestPosition) {
    // see and describe the chest in the RGB picture before calling this function.
    bot.chat("I can see the chest in front of my eyes. The chest is at ..."); // You must see the chest in the RGB picture and describe the position in the RGB picture before calling this function.
    await moveToChest(bot, chestPosition);
    const chestBlock = bot.blockAt(chestPosition);
    await bot.openContainer(chestBlock);
    // You must close the chest after opening it if you are asked to open a chest
    await closeChest(bot, chestBlock);
}




At each round of conversation, I will give you

Code info: ...
Events: ...
RGB size: (height, weight)
RGB: ...
Equipment: ...
Invenrtory: ...
Life states: ...
Location stats: ...
Task: ...
Plan: ...

You should then respond to me with
Explain (if applicable): What can you see in the RGB picture? Are there any steps missing in your plan? Why does the code not complete the task? What does code info imply? What can be inferred from these events? What impact do these events have on the task? How will you respond to these events?
Plan: How to complete the task step by step. You should pay attention to Inventory since it tells what you have.
Code:
    1) Write an async function taking the bot as the only argument.
    2) You can obtain the in-game information by looking at pictures. Observe the world with your eyes instead of using in-game information. Do not cheat. You must see the certain blocks in the RGB picture before use them as target. If you are not sure what you are looking at, you can use `bot.blockAtCursor(maxDistance=8)` or `bot.entityAtCursor(maxDistance=3.5)`.
    3) Reuse the above useful programs as much as possible.
        - Use `mineBlock(bot, name, count)` to collect blocks. Do not use `bot.dig` directly.
        - Use `craftItem(bot, name, count)` to craft items. Do not use `bot.craft` or `bot.recipesFor` directly.
        - Use `smeltItem(bot, name count)` to smelt items. Do not use `bot.openFurnace` directly.
        - Use `placeItem(bot, name, position)` to place blocks. Do not use `bot.placeBlock` directly.
        - Use `killMob(bot, name, timeout)` to kill mobs. Do not use `bot.attack` directly.
    4) Your function will be reused for building more complex functions. Therefore, you should make it generic and reusable. You should not make strong assumption about the inventory (as it may be changed at a later time), and therefore you should always check whether you have the required items before using them. If not, you should first collect the required items and reuse the above useful programs.
    5) Functions in the "Code from the last round" section will not be saved or executed. Do not reuse functions listed there.
    6) Anything defined outside a function will be ignored, define all your variables inside your functions.
    7) Call `bot.chat` to show the intermediate progress.
    8) You should select a direction at random every time instead of constantly using (1, 0, 1).
    9) You must make sure there are targets in the RGB picture and use `bot.chat` to describe where is the target before use `bot.findBlocks` and `bot.findBlock`. Otherwise, it cannot be invoked. Do not cheat.
    10) `maxDistance` should always be 8 for `bot.findBlocks` and `bot.findBlock` and you must sure you can see it directly. Do not cheat.
    11) Do not write infinite loops or recursive functions.
    12) Do not use `bot.on` or `bot.once` to register event listeners. You definitely do not need them.
    13) Name your function in a meaningful way (can infer the task from the name).

You should only respond in the format as described below:
RESPONSE FORMAT:
Explain: ...
Plan:
1) ...
2) ...
3) ...
...
Code:
```javascript
// helper functions (only if needed, try to avoid them)
...
// main function after the helper functions
async function yourMainFunctionName(bot) {
  // ...
}
// use the function
await yourMainFunctionName(bot);
```

'''
    

