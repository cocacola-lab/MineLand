// Kill a pig and collect the dropped item: killMob(bot, "pig", 300);
// Before using this function, there must be a mob in the RGB picture. Do not cheat.
async function killMob(bot, mobName, timeout = 300) {
    // see the mob and describe the position in the RGB picture before calling this function
    bot.chat("I can see the " + mobName + " in front of my eyes. It is at ..."); // replace '...' with the position of mob in RGB picture
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
