const bodyParser = require("body-parser");
const Vec3 = require("vec3");

const express = require("express");

const PORT = 21301;
const app = express();

const BotManager = require("./bot_manager");
const bot_manager = new BotManager()

app.use(bodyParser.json({ limit: "50mb" }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: false }));

app.listen(PORT, () => {
    console.log(`JS side listener started on port ${PORT}`);
});

app.post("/start", async (req, res) => {
    if (!req.body.agents_count || !req.body.server_host || !req.body.server_port || !req.body.minecraft_version || !req.body.agents_config) {
        return res.status(400).json({ return_code: 400, error: 'Missing required properties in the request body' });
    }
    
    otherError = (err)=>{
        console.log("global error : " + err)
        return
    }

    bot_manager.stopAll()
    number_of_bot = req.body.agents_count;
    server_host = req.body.server_host;
    server_port = req.body.server_port;
    version = req.body.minecraft_version;
    configs = req.body.agents_config;

    for(var i = 0; i < number_of_bot; i++) {
        console.log(i + " : " + configs[i].name)
        await new Promise(resolve => setTimeout(resolve, 500))
        bot_manager.createBot(configs[i].name, server_host, server_port, version)
    }

    // The following function needs to complete its execution within 3 seconds.
    if(req.body.headless) {
        console.log("Headless Mode")
    } else {
        console.log("RGB Mode: (" + req.body.image_width + ", " +req.body.image_height + ")")
        await new Promise(resolve => setTimeout(resolve, 2000))
        bot_manager.createViewerOnAllBots(width = req.body.image_width, height = req.body.image_height)
    }

    // ===== Get Observations =====
    setTimeout(() => {
        obs = []
        for(let i = 0; i < number_of_bot; i++) {
            console.log("Get Observation: " + i)
            obs.push(bot_manager.getBotObservation(i));
        }
        res.status(200).json({
            return_code: 200,
            observation: obs,
        })
    }, 5000) // wait for 5 seconds to make sure all bots are spawned

})

app.post("/step_pre", (req, res) => {
    data = req.body
    let ticks = data.ticks
    let is_low_level_action = data.is_low_level_action
    let bots_count = data.action.length

    // when bots_count !== bot_manager.bots.length, we need to throw an exception
    if(bots_count !== bot_manager.getBotNumber()) {
        return res.status(404).json({
            return_code: 404,
            error: "Action length does not equal to the number of bots.",
        })
    }

    // ===== Start Global Catch Exceptions =====
    process.on('uncaughtException', otherError)

    // ===== Execute Actions =====
    if (is_low_level_action) {
        for(let i = 0; i < bots_count; i++) {
            if (!bot_manager.getBotIsActive(i)) continue;

            // console.log("Low Level Action: ", req.body.action[i])

            // TODO
            // 1. iterate action[0..7]
            let actionList = JSON.parse(req.body.action[i]);
            //转成list

            bot_manager.runLowLevelActionByOrder(i, actionList)
            // 2. execute actions in action[i]
            // - call a func

            // 3. In another file, low-level-action-utils.js
            // - implement a lot of functions
        }
    } else {
        for(let i = 0; i < bots_count; i++) {
            if (!bot_manager.getBotIsActive(i)) continue;

            code = req.body.action[i].code;
            if(req.body.action[i].type == 0) {
                bot_manager.addCodeTick(i, ticks)
                continue;
            }
            // TODO: execute actions
            bot_manager.interruptBotByOrder(i);
            bot_manager.runCodeByOrder(i, code)
            bot_manager.changeCodeTick(i, 0)
        }
    }

    // bot_manager.stopTpInterval();
    
    // ===== Run Ticks =====
    res.status(200).json({ return_code:200 })
})

app.post("/step_lst", (req, res) => {
    data = req.body
    let ticks = data.ticks
    
    // ===== Get Observations =====
    setTimeout(()=>{
        bot_manager.updateBotsPositions();
        bot_manager.startTpInterval();
        obs = []
        for(let i = 0; i < number_of_bot; i++) {
            obs.push(bot_manager.getBotObservation(i));
        }

        codeInfo = []
        for(let i = 0; i < number_of_bot; i++) {
            codeInfo.push(bot_manager.getCodeInfo(i));
        }
        bot_manager.clearCodeErorrs()

        events = []
        for(let i = 0; i < number_of_bot; i++) {
            events.push(bot_manager.getEvent(i));
        }
        bot_manager.clearEvents()

        process.off('uncaughtException',otherError);
        res.status(200).json({
            return_code:200,
            observation: obs,
            code_info: codeInfo,
            event: events
        })
    }, ticks * 50)
})

app.post("/end", (req, res) => {
    bot_manager.stopAll();
    res.status(200).json({ return_code:200 })
})

app.post("/add_an_agent", (req, res) => {
    if (!req.body.agent_config) {
        return res.status(400).json({ return_code: 400, error: 'Missing required properties in the request body' });
    }
    
    number_of_bot += 1;

    console.log("Add an agent: " + req.body.agent_config.name)
    bot_manager.createBot(req.body.agent_config.name, server_host, server_port, version)

    // The following function needs to complete its execution within 3 seconds.
    if(!req.body.headless) {
        bot_manager.createViewerOnLastBot(width = req.body.image_width, height = req.body.image_height)
    }

    // ===== Get Observations =====
    setTimeout(() => {
        res.status(200).json({ return_code:200 })
    }, 1000) // wait for 1 seconds to make sure the bot is spawned
})

app.post("/disconnect_an_agent", (req, res) => {
    if (!req.body.name) {
        return res.status(400).json({ return_code: 400, error: 'Missing required properties in the request body' })
    }
    const name = req.body.name
    console.log("Disconnect an agent: " + name)
    bot_manager.disconnectBot(name)
    res.status(200).json({ return_code:200 })
})

/* ===== World ===== */

app.post("/createWorld", (req, res) => {
    if (!req.body.world_name || !req.body.world_type) {
        return res.status(400).json({return_code: 400, error: 'Missing required properties in the request body' });
    }
    world_name = req.body.world_name;
    world_type = req.body.world_type;
    if(world_type !== 'END' && world_type !== 'NETHER' && world_type !== 'NORMAL') {
        return res.status(400).json({ return_code: 400,error: 'world_type is not valid.' })
    }
    bot_manager.getBotByOrder(0).chat("/mw create " + world_name + ' ' + world_type);
    res.status(200).json({return_code:200})
}) 

app.post("/switchWorld", (req, res) => {
    if (!req.body.world_name) {
        return res.status(400).json({return_code: 400, error: 'Missing required properties in the request body' });
    }
    world_name = req.body.world_name;
    bot_manager.allBotChat("/mw tp " + world_name);
    setTimeout(()=>{res.status(200).json({return_code:200})}, 6000)//wait 6s for tp
})

app.post("/spawn", (req, res) => {
    bot_manager.allBotChat("/mw spawn ");
    setTimeout(()=>{res.status(200).json({return_code:200})}, 20)
})

app.post("/setSpawn", (req, res) => {
    bot_manager.allBotChat("/mw setSpawn ");
    setTimeout(()=>{res.status(200).json({return_code:200})}, 20)
})

/* ===== Camera ===== */

app.post("/addCamera", (req, res) => {
    if (!req.body.camera_id || !req.body.image_width || !req.body.image_height) {
        return res.status(400).json({return_code: 400, error: 'Missing required properties (camera_id or image_width or image_height) in the request body' });
    }
    camera_id = req.body.camera_id;
    image_width = req.body.image_width;
    image_height = req.body.image_height;
    bot_manager.addCamera(camera_id, image_width, image_height);
    res.status(200).json({return_code:200})
})

app.post("/getCameraView", (req, res) => {
    if (!req.body.camera_id) {
        return res.status(400).json({return_code: 400, error: 'Missing required properties (camera_id) in the request body' });
    }
    camera_id = req.body.camera_id;

    res.status(200).json({return_code: 200, rgb: bot_manager.getCameraView(camera_id)})
})

app.post("/updateCameraLocation", (req, res) => {
    console.log(req.body)
    if (req.body.camera_id === undefined || req.body.pos === undefined || req.body.yaw === undefined || req.body.pitch === undefined) {
        return res.status(400).json({return_code: 400, error: 'Missing required properties (camera_id or pos or yaw or pitch) in the request body' });
    }
    console.log(req.body)
    camera_id = req.body.camera_id;
    pos = new Vec3(req.body.pos[0], req.body.pos[1], req.body.pos[2]);
    yaw = req.body.yaw;
    pitch = req.body.pitch;
    bot_manager.modifyCameraLoc(camera_id, pos, yaw, pitch);
    res.status(200).json({return_code:200})
})
app.post("/addCameraLocation", (req, res) =>{
    if (req.body.camera_id === undefined || req.body.d_pos === undefined || req.body.d_yaw === undefined || req.body.d_pitch === undefined) {
        return res.status(400).json({return_code: 400, error: 'Missing required properties (camera_id or d_pos or d_yaw or d_pitch) in the request body' });
    }
    console.log(req.body)
    camera_id = req.body.camera_id;
    d_pos = new Vec3(req.body.d_pos[0], req.body.d_pos[1], req.body.d_pos[2]);
    d_yaw = req.body.d_yaw;
    d_pitch = req.body.d_pitch;
    bot_manager.addCameraLoc(camera_id, d_pos, d_yaw, d_pitch);
    res.status(200).json({return_code:200})
})

app.post("/moveCameraLocation", (req, res) =>{
    if (req.body.camera_id === undefined || req.body.d_pos === undefined || req.body.d_yaw === undefined || req.body.d_pitch === undefined) {
        return res.status(400).json({return_code: 400, error: 'Missing required properties (camera_id or d_pos or d_yaw or d_pitch) in the request body' });
    }
    // console.log(req.body)
    camera_id = req.body.camera_id;
    d_pos = new Vec3(req.body.d_pos[0], req.body.d_pos[1], req.body.d_pos[2]);
    d_yaw = req.body.d_yaw;
    d_pitch = req.body.d_pitch;
    bot_manager.moveCameraLoc(camera_id, d_pos, d_yaw, d_pitch);
    setTimeout(()=> {res.status(200).json({return_code:200})}, 2000)
})
