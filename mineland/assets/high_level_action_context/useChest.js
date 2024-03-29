// Get a torch from chest at (30, 65, 100): getItemFromChest(bot, new Vec3(30, 65, 100), {"torch": 1});
// Before using this function, there must be a chest in the RGB picture. Do not cheat.
// This function will work only the bot can see the chest.
async function getItemFromChest(bot, chestPosition, itemsToGet) {
    // see and describe the chest in the RGB picture before calling this function.
    bot.chat("I can see the chest in front of my eyes. The chest is at ..."); // replace '...' with the position in RGB picture
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
    bot.chat("I can see the chest in front of my eyes. The chest is at ..."); // replace '...' with the position in RGB picture
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
    bot.chat("I can see the chest in front of my eyes. The chest is at ..."); // replace '...' with the position in RGB picture
    await moveToChest(bot, chestPosition);
    const chestBlock = bot.blockAt(chestPosition);
    await bot.openContainer(chestBlock);
    // You must close the chest after opening it if you are asked to open a chest
    await closeChest(bot, chestBlock);
}
