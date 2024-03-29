// Smelt 1 raw_iron into 1 iron_ingot using 1 oak_planks as fuel: smeltItem(bot, "raw_iron", "oak_planks");
// Before using this function, there must be a furnace in your the RGB picture. Do not cheat.
// You must place a furnace before calling this function.
async function smeltItem(bot, itemName, fuelName, count = 1) {
    const item = mcData.itemsByName[itemName];
    const fuel = mcData.itemsByName[fuelName];
    // see and describe the furnace in the RGB picture before calling this function
    bot.chat("I can see the furnace in front of my eyes. It is at ..."); // replace '...' with the position in RGB picture
    const furnaceBlock = bot.findBlock({
        matching: mcData.blocksByName.furnace.id,
        maxDistance: 48,
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
