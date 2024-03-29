// Mine 3 cobblestone: mineBlock(bot, "stone", 3);
// Before using this function, there must be a block in the RGB picture. Do not cheat.
// The count parameter must be less than or equal to the number of block which you want to mine in your field of vision.
async function mineBlock(bot, name, count = 1) {
    // see the block and describe the position in the RGB picture before calling this function
    bot.chat("I can see the " + name + " in front of my eyes. It is at ..."); // replace '...' with the position of blocks in RGB picture
    const blocks = bot.findBlocks({
        matching: (block) => {
            return block.name === name;
        },
        maxDistance: 48,
        count: count,
    });
    const targets = [];
    for (let i = 0; i < Math.min(blocks.length, count); i++) {
        targets.push(bot.blockAt(blocks[i]));
    }
    await bot.collectBlock.collect(targets, { ignoreNoPath: true });
}
