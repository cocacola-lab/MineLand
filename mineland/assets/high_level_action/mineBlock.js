async function mineBlock(bot, name, count = 1) {
    // return if name is not string
    if (typeof name !== "string") {
        throw new Error(`name for mineBlock must be a string`);
    }
    if (typeof count !== "number") {
        throw new Error(`count for mineBlock must be a number`);
    }
    const blockByName = mcData.blocksByName[name];
    if (!blockByName) {
        throw new Error(`No block named ${name}`);
    }
    const blocks = bot.findBlocks({
        matching: [blockByName.id],
        maxDistance: 48,
        count: count,
    });
    if (blocks.length === 0) {
        bot.chat(`No ${name} nearby, please explore first, try to go to a new place`);
        return;
    }
    bot.chat(`Try to mine ${blocks.length} ${name} nearby`)
    const targets = [];
    for (let i = 0; i < blocks.length; i++) {
        targets.push(bot.blockAt(blocks[i]));
    }
    try
    {
        await bot.collectBlock.collect(targets, {
            ignoreNoPath: true,
            count: count,
        });
        bot.chat(`Mined ${blocks.length} ${name}`);
    }
    catch (err) {
        bot.chat(`Error mining ${name}: ${err.message}`);
    }
}
