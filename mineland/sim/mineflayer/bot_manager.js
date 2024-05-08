const fs = require('fs');

const mineflayer = require("mineflayer");

const { AbortController } = require('abort-controller');
const ObservationUtils = require("./observation_utils");
const ViewerManager = require("./viewer_manager");
const pvp = require("mineflayer-pvp").plugin;
const tool = require("mineflayer-tool").plugin;
const minecraftHawkEye = require("minecrafthawkeye");
const {
    Movements,
    goals: {
        Goal, GoalBlock, GoalNear, GoalXZ, GoalNearXZ, GoalY, GoalGetToBlock, GoalLookAtBlock,
        GoalBreakBlock, GoalCompositeAny, GoalCompositeAll, GoalInvert, GoalFollow, GoalPlaceBlock,
    },
    pathfinder,
    Move, ComputedPath, PartiallyComputedPath, ZCoordinates,
    XYZCoordinates, SafeBlock, GoalPlaceBlockOptions,
} = require("mineflayer-pathfinder");
const { Vec3 } = require('vec3');
const { assert } = require('console');
const collectBlock = require("mineflayer-collectblock-colalab").plugin;

// basic functions that ai can use
let filePathPrefix = '../../assets/high_level_action/'
let filePathsRaw = ['craftHelper.js', 'craftItem.js', 'givePlacedItemBack.js', 'killMob.js', 'mineBlock.js','placeItem.js', 'shoot.js', 'smeltItem.js', 'useChest.js', 'waitForMobRemoved.js']
let filePaths = filePathsRaw.map((filePath) => filePathPrefix + filePath)

class BotManager {

constructor() {
    this.bots = [];
    this.events = []; // all events during one step
    this.code_status = []
    this.code_error = []
    this.code_tick = []
    this.abort_controllers = []
    this.current_code = []
    this.viewer_manager = new ViewerManager()
    this.tp_interval = null // tp_interval is used to stop bots'movements when pausing.
    this.bots_positions = []
    this.mineflayer_timeout_interval = 1000000 // 600s
    this.mineflayer_view_distance = 'normal' // far/normal/short/tiny, refer to https://github.com/PrismarineJS/mineflayer/blob/master/docs/api.md#botsettingsviewdistance

    this.hearing_distance = 50.0
    this.high_level_action_code = ""

    this.tick = 0
}

createBot = (username, host, port, version) => {
    const self = this;

    const bot = mineflayer.createBot({
        host: host,
        port: port,
        username: username,
        version: version,
        checkTimeoutInterval: self.mineflayer_timeout_interval,
        viewDistance: self.mineflayer_view_distance,
    });
    
    bot.loadPlugin(pathfinder);
    bot.loadPlugin(collectBlock);
    bot.loadPlugin(pvp);
    bot.loadPlugin(tool);
    bot.loadPlugin(minecraftHawkEye)
    this.bots.push(bot);
    this.code_status.push('ready')
    this.abort_controllers.push(new AbortController())
    this.code_error.push('')
    this.current_code.push('')
    this.events.push([])
    this.code_tick.push(0)
    bot.on('spawn', () => {
        self.bots_positions.push(bot.entity.position);
    })
    this.addEventListener(bot);
    this.high_level_action_code = this.loadHighLevelActionCode()

    // track the tick
    if (this.bots.length === 1) {
        bot.on('physicsTick', () => {
            this.tick += 1
        })
    }

    // is active
    bot.mineland_is_active = true;
}

/**
 * Disconnect a bot
 */
disconnectBot = (username) => {
    const bot = this.getBotByName(username)
    bot.mineland_is_active = false;
    bot.end();
}


/**
 * load high level action
 */
loadHighLevelActionCode = () => {
    var high_level_action_code = ""
    for(var i = 0; i < filePaths.length; ++i) {
        const path = filePaths[i]
        const fileContent = fs.readFileSync(path, 'utf-8');
        high_level_action_code += fileContent
    }
    return high_level_action_code
}

/**
 * Add event listener to a bot
 * @param {mineflayer.Bot} bot
 */
addEventListener = (bot, is_first_bot=false) => {
    //TODO: add more event listeners
    const self = this;
    
    // on bot get hurt
    bot.on('entityHurt', (entity) => {
        if(this.calc_dis(entity.position, bot.entity.position) < this.hearing_distance) {
            if (entity === bot.entity) {
                this.events[this.bots.indexOf(bot)].push({
                    type: 'entityHurt',
                    entity_type: 'self',
                    entity_name: bot.username,
                    message: 'bot#' + bot.username + ' get hurt',
                    tick: self.tick,
                })
            } else if (this.getBotByName(entity.username) !== null) {
                this.events[this.bots.indexOf(bot)].push({
                    type: 'entityHurt',
                    entity_type: 'bot',
                    entity_name: bot.username,
                    message: 'bot#' + bot.username + ' get hurt',
                    tick: self.tick,
                })
            } else if (entity.type === 'player') {
                this.events[this.bots.indexOf(bot)].push({
                    type: 'entityHurt',
                    entity_type: entity.type,
                    entity_name: entity.username,
                    message: entity.username + ' is hurt',
                    tick: self.tick,
                })
            } else if (entity.type === 'mob') {
                this.events[this.bots.indexOf(bot)].push({
                    type: 'entityHurt',
                    entity_type: entity.type,
                    entity_name: entity.name,
                    message: entity.displayName + ' is hurt',
                    tick: self.tick,
                })
            }
        }
    });

    // on arbitrary entity dead
    bot.on('entityDead', (entity) => {
        if(this.calc_dis(entity.position, bot.entity.position) < this.hearing_distance) {
            this.events[this.bots.indexOf(bot)].push({
                type: 'entityDead',
                entity_type: entity.type,
                entity_name: entity.name,
                message: entity.name + ' dead',
                tick: self.tick,
            })
        }
    })
    
    // eat something
    bot.on('entityEat', (entity) => {
        if(this.calc_dis(entity.position, bot.entity.position) < this.hearing_distance) {
            this.events[this.bots.indexOf(bot)].push({
                type: 'entityEat',
                entity_type: entity.type,
                entity_name: entity_name,
                tick: self.tick,
            })
        }
    })

    // spawn
    bot.on('entitySpawn', (entity) => {
        if(this.calc_dis(entity.position, bot.entity.position) < 10.0 && (
            entity.type === 'animal' || entity.type === 'hostile' || entity.type === 'mob'
            || entity.type === 'water_creature' || entity.type === 'ambient'
        )) {
            this.events[this.bots.indexOf(bot)].push({
                type: 'entitySpawn',
                entity_type: entity.type,
                entity_name: entity.name,
                position: entity.position,
                tick: self.tick,
            })
        }
    })

    // on get chat message
    bot.on('chat', (username, message) => {
        if (username === 'Server') return;
        if (message.startsWith('commands.pause')) return;
        if (message.startsWith('/')) return;
        if (message.startsWith('Teleported')) return;

        const sending_bot = this.getBotByName(username)
        if(sending_bot) {
            if(this.calc_dis(bot.entity.position, sending_bot.entity.position) < this.hearing_distance) {
                this.events[this.bots.indexOf(bot)].push({
                    type: 'chat',
                    only_message : message,
                    username : username,
                    message: "<" + username + '> ' + message,
                    tick: self.tick,
                })
            }
        } else {
            this.events[this.bots.indexOf(bot)].push({
                type: 'chat',
                only_message : message,
                username : username,
                message: "<" + username + '> ' + message,
                tick: self.tick,
            })
        }
        // console.log("check finish!")
    });

    bot.on('death', () => {
        this.events[this.bots.indexOf(bot)].push({
            type: 'death',
            message: 'bot#' + bot.username + ' dead',
            tick: self.tick,
        })
        
        // console.log('bot#' + bot.username + ' dead')
    }); 

    bot.on('blockBreakProgressEnd', (block, entity) => {
        this.events[this.bots.indexOf(bot)].push({
            type: 'blockIsBeingBroken',
            block_name: block.name,
            message: 'A ' + block.name + ' block is being broken',
            tick: self.tick,
        })
    })

    bot.on('playerJoined', (player) => {
        this.events[this.bots.indexOf(bot)].push({
            type: 'playerJoined',
            player_name: player.username,
            message: player.username + ' joined',
            tick: self.tick,
        })
    })

    bot.on('playerLeft', (player) => {
        this.events[this.bots.indexOf(bot)].push({
            type: 'playerLeft',
            player_name: player.username,
            message: player.username + ' left',
            tick: self.tick,
        })
    })
}



calc_dis = (pos1, pos2)=>{
    return Math.sqrt((pos1.x-pos2.x) * (pos1.x-pos2.x) + (pos1.y-pos2.y) * (pos1.y-pos2.y) + (pos1.z-pos2.z) * (pos1.z-pos2.z))
}

updateBotsPositions = () => {
    for(let i = 0; i < this.bots.length; ++i) {
        if (this.bots[i].mineland_is_active) {
            this.bots_positions[i] = this.bots[i].entity.position;
        }
    }
}

startTpInterval = () => {
    // const self = this;
    // this.tp_interval = setInterval(() => {
    //     //tp bots to themselves
    //     for(let i = 0; i < self.bots.length; ++i) {
    //         self.bots[i].chat('/tp ' + self.bots[i].username + ' ' + self.bots_positions[i].x+ ' ' + self.bots_positions[i].y+ ' ' + self.bots_positions[i].z);
    //     }
    // }, 5)
}
changeCodeTick = (id, tick) => {
    this.code_tick[id] = tick
}
addCodeTick = (id, tick) =>{
    this.code_tick[id] += tick
}
stopTpInterval = () => {
    if(this.tp_interval) {
        clearInterval(this.tp_interval);
        this.tp_interval = null;
    }
}

stopAll = () => {
    this.bots.forEach(bot => {
        if (bot.mineland_is_active) {
            bot.end();
        }
    });
    this.bots = [];
    this.code_status = [];
}


interruptBotByOrder = (id) => {
    const bot = this.bots[id];
    if (bot.mineland_is_active) {
        if(this.abort_controllers[id]) {
            this.abort_controllers[id].abort();
        }
        bot.pathfinder.setGoal(null);
        bot.clearControlStates();
        bot.stopDigging();
        this.code_status[id] = 'ready'
    }
}
runCodeByOrder = async (id, code) => {
    this.abort_controllers[id]=new AbortController()
    const self = this;
    self.code_status[id] = 'running';

    let bot = self.bots[id];
    if (bot.mineland_is_active) {
        const mcData = require("minecraft-data")(bot.version);
        const movements = new Movements(bot, mcData);
        bot.pathfinder.setMovements(movements);
        self.abort_controllers[id].signal.addEventListener( 'abort', () => { 
            bot=undefined 
        } 
        );
        
        try {
            let mineflayer_bot_id = id
            this.current_code[id] = code
            await eval("(async () =>{" +this.high_level_action_code+ "\n" + code +"\n"+"})()")
            self.code_status[mineflayer_bot_id] = 'ready'
        }
        catch(e) {
            console.log("catched after eval" , e);
            if(bot) {
                this.code_status[id] = 'ready';
                this.code_error[id] = e;
            }
        }
    }
}

runCodeByName = async(name, code) => {
    for(let i = 0;i < this.bots.length; ++i) {
        if (!this.bots[i].mineland_is_active) continue
        if (this.bots[i].username == name) {
            runCodeByOrder(i, code)
            return
        }
    }
}

setMovementControl(bot, action, directions) {
    directions.forEach((direction, index) => {
        bot.setControlState(direction, action === index + 1);
    });
}

runLowLevelActionByOrder = async (id, action) => {

    // Forward and backward
    // 0: noop, 1: forward, 2: back
    const forwardBack = ['forward', 'back'];
    assert(Number.isInteger(action[0]), 'action[0] is not an integer')
    assert(action[0] >= 0 && action[0] <= 2, 'action[0] is out of range')
    setMovementControl(this.bots[id], action[0], forwardBack);

    // Move left and right
    // 0: noop, 1: move left, 2: move right
    const leftRight = ['left', 'right'];
    assert(Number.isInteger(action[1]), 'action[1] is not an integer')
    assert(action[1] >= 0 && action[1] <= 2, 'action[1] is out of range')
    setMovementControl(this.bots[id], action[1], leftRight);

    // Jump, sneak, and sprint
    // 0: noop, 1: jump, 2: sneak, 3:sprint
    const jumpSneakSprint = ['jump', 'sneak', 'sprint'];
    assert(Number.isInteger(action[2]), 'action[2] is not an integer')
    assert(action[2] >= 0 && action[2] <= 3, 'action[2] is out of range')
    setMovementControl(this.bots[id], action[2], jumpSneakSprint);

    
    const currentPitch = this.bots[id].entity.pitch
    const currentYaw = this.bots[id].entity.yaw

    // Camera delta pitch
    // 0: -180 degree, 24: 180 degree
    assert(Number.isInteger(action[3]), 'action[3] is not an integer')
    assert(action[3] >= 0 && action[3] <= 24, 'action[3] is out of range')
    const deltaPitchDegrees = (action[3] - 12) * 15;
    const deltaPitchRadians = deltaPitchDegrees * (Math.PI / 180);
    const newPitchDegrees = currentPitch + deltaPitchRadians;

    // Camera delta yaw
    // 0: -180 degree, 24: 180 degree
    assert(Number.isInteger(action[4]), 'action[4] is not an integer')
    assert(action[4] >= 0 && action[4] <= 24, 'action[4] is out of range')
    const deltaYawDegrees = (action[4] - 12) * 15;
    const deltaYawRadians = deltaYawDegrees * (Math.PI / 180);
    const newYawDegrees = currentYaw + deltaYawRadians;

    await this.bots[id].look(newPitchDegrees, newYawDegrees);

    const blockAtCursor = this.bots[id].blockAtCursor();
    const entityAtCursor = this.bots[id].entityAtCursor();
    const heldItem = this.bots[id].heldItem;

    // Functional actions
    // 0: noop, 1: use, 2: drop, 3: attack, 4: craft, 5: equip, 6: place, 7: destroy
    assert(Number.isInteger(action[5]), 'action[5] is not an integer')
    assert(action[5] >= 0 && action[5] <= 7, 'action[5] is out of range')
    if (action[5] === 1) {
        if (blockAtCursor) {
            await this.bots[id].activateBlock(blockAtCursor)
        }
        if (entityAtCursor) {
            this.bots[id].useEntity(entityAtCursor, 0)
        } else if (heldItem) {
            this.bots[id].activateItem()
        }
    } else if (action[5] === 2) {
        if (heldItem) {
            await this.bots[id].tossStack(heldItem);
        }
    } else if (action[5] === 3) {
        if (entityAtCursor) {
            this.bots[id].useEntity(target, 1)
        }
        this.bots[id].swingArm()
    } else if (action[5] === 4) {
        // TODO: craft
    } else if (action[5] === 5) {
        // TODO: equip
        assert(Number.isInteger(action[7]), 'Slot index must be an integer.')
        assert(action[7] >= 0 && action[7] <= 35, 'Slot index must be between 0 and 35.')
        const slotItem = bot.inventory.slots[action[7]]
        if (slotItem) {
            this.bots[id].equip(slotItem.type, 'hand')
        }
    } else if (action[5] === 6) {
        // TODO: place
        assert(Number.isInteger(action[7]), 'Slot index must be an integer.')
        assert(action[7] >= 0 && action[7] <= 35, 'Slot index must be between 0 and 35.')
        if (slotItem && blockAtCursor) {
            this.bots[id].equip(slotItem.type, 'hand')
            const faceVectors = [
                new Vec3(0, 1, 0),
                new Vec3(0, -1, 0),
                new Vec3(1, 0, 0),
                new Vec3(-1, 0, 0),
                new Vec3(0, 0, 1),
                new Vec3(0, 0, -1),
            ];
            let faceVector = null;
            for (const vector of faceVectors) {
                const block = bot.blockAt(blockAtCursor.position.minus(vector));
                if (block?.name === "air") {
                    faceVector = vector;
                    break;
                }
            }
            await this.bots[id].placeBlock(blockAtCursor, faceVector);
        }
    } else if (action[5] === 7) {
        // TODO: destroy
        assert(Number.isInteger(action[7]), 'Slot index must be an integer.')
        assert(action[7] >= 0 && action[7] <= 35, 'Slot index must be between 0 and 35.')
        await this.bots[id].creative.clearSlot(action[7]);

    }

}

clearCodeErorrs = () => {
    for(let i = 0; i < this.bots.length; ++i) {
        if (!this.bots[i].mineland_is_active) continue
        this.code_error[i] = ''
    }
}
getBotByName = (name) => {
    for(var i = 0; i < this.bots.length; i++){
        if (!this.bots[i].mineland_is_active) continue
        const bot = this.bots[i]
        if(bot.username == name) {
            return bot
        }
    }
    return null
}

getBotByOrder = (id) => {
    let len = this.bots.length;
    if(id >= len) {
        return this.bots[len - 1];
    }
    return this.bots[id];
}
getCodeStatus = () =>{
    return this.code_status;
}
getBotNumber = () => { 
    return this.bots.length;
}

getBotIsActive = (id) => {
    return this.bots[id].mineland_is_active
}

/**
 * Get the observation space of a bot
 */
getBotObservation = (id) => {
    if (!this.bots[id].mineland_is_active) return null

    return ObservationUtils.getObservation(this.bots[id], this.viewer_manager, this.tick);
}

/**
 * Create viewer on all bots
 */
createViewerOnAllBots(width, height) {
    this.viewer_manager.createViewerOnAllBots(this.bots, width, height)
}

/**
 * Create viewer on a bot
 */
createViewerOnLastBot(width, height) {
    this.viewer_manager.createViewerOnBot(this.bots, this.bots.length - 1, width, height)
}

/**
 * Get the code execute error of a bot
 */
getCodeError = (id) => {
    if (!this.bots[id].mineland_is_active) return null

    let error = this.code_error[id];
    if(error==='') return {};

    return {
        error_type: error.name,
        error_message: error.message,
        error_stack: error.stack,
    }
}

/**
 * Get the code info of a bot
 */
getCodeInfo = (id) => {
    if (!this.bots[id].mineland_is_active) return null

    let name = this.bots[id].username;
    let is_running = this.code_status[id] === 'running';
    let is_ready = is_running ? false : true;
    let error = this.getCodeError(id);
    let last_code = this.current_code[id]
    let code_tick = this.code_tick[id]
    return {
        name: name,
        is_running: is_running,
        is_ready: is_ready,
        last_code: last_code,
        code_tick: code_tick,
        code_error: error,
    }
}

/**
 * Get the event of a bot
 */
getEvent = (id) => {
    if (!this.bots[id].mineland_is_active) return []

    if(id < this.events.length) return this.events[id]
    else return []
}

/**
 * Clear all events
 */
clearEvents = () => {
    for(let i = 0; i < this.bots.length; ++i) {
        this.events[i] = []
    }
}
allBotChat = (s) => {
    for(let i = 0; i < this.bots.length; ++i) {
        if (!this.bots[i].mineland_is_active) continue

        this.bots[i].chat(s)
    }
}

/* ===== Camera ===== */

/**
 * Create a camera
 */
addCamera = (camera_id, image_width, image_height) => {
    this.viewer_manager.addCamera(this.bots[0], camera_id, image_width, image_height)
}

/**
 * Get a screenshot of a camera in base64 format.
 */
getCameraView(camera_id) {
    return this.viewer_manager.getCameraView(camera_id)
}

/**
 * Modify the location of a camera
 */
modifyCameraLoc(camera_id, pos, yaw, pitch) {
    this.viewer_manager.modifyCameraLoc(camera_id, pos, yaw, pitch)
}

addCameraLoc(camera_id, d_pos, d_yaw, d_pitch) {
    this.viewer_manager.addCameraLoc(camera_id, d_pos, d_yaw, d_pitch)
}

moveCameraLoc(camera_id, d_pos, d_yaw, d_pitch) {
    this.viewer_manager.forwardCamera(camera_id, d_pos.x)
    this.viewer_manager.upCamera(camera_id, d_pos.y)
    this.viewer_manager.rightCamera(camera_id, d_pos.z)
    this.viewer_manager.addCameraLoc(camera_id, new Vec3(0, 0, 0), d_yaw, d_pitch)
}
/**
 * Modify the position of a camera
 */
modifyCameraPos(camera_id, pos) {
    this.viewer_manager.modifyCameraPos(camera_id, pos)
}

/**
 * Modify the compass of a camera
 */
modifyCameraCompass(camera_id, yaw, pitch) {
    this.viewer_manager.modifyCameraCompass(camera_id, yaw, pitch)
}

}

module.exports = BotManager;