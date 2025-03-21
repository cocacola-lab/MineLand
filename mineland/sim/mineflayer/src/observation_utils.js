const ViewerManager = require("./viewer_manager");
const { Vec3 } = require("vec3");


function roundTo2(num) {
    return Math.round((num + Number.EPSILON) * 100) / 100;
}

/**
 * This utils class provides a set of functions to generate bots' observations.
 */
class ObservationUtils {

    /**
     * Get the observation of a bot.
     */
    static getObservation(bot, viewer_manager, tick) {

        let rgb_base64 = viewer_manager.getBotViewByName(bot.username)
        if (rgb_base64 === undefined) rgb_base64 = ""

        let main_hand = this.getEquipmentInfo(bot.inventory.slots[bot.getEquipmentDestSlot('hand')]);
        let foot = this.getEquipmentInfo(bot.inventory.slots[bot.getEquipmentDestSlot('feet')]);
        let leg = this.getEquipmentInfo(bot.inventory.slots[bot.getEquipmentDestSlot('legs')]);
        let body = this.getEquipmentInfo(bot.inventory.slots[bot.getEquipmentDestSlot('torso')]);
        let head = this.getEquipmentInfo(bot.inventory.slots[bot.getEquipmentDestSlot('head')]);
        let off_hand = this.getEquipmentInfo(bot.inventory.slots[bot.getEquipmentDestSlot('off-hand')]);

        return {
            // ===== Basic Attributes =====
            name: bot.username,

            // ===== RGB Frames =====
            rgb_height: viewer_manager.image_height,
            rgb_width: viewer_manager.image_width,
            rgb: rgb_base64,

            // ===== Equipment =====
            // MineDojo Style
            equipment: {
                "name": [main_hand["name"], foot["name"], leg["name"], body["name"], head["name"], off_hand["name"]],
                "quantity": [main_hand["quantity"], foot["quantity"], leg["quantity"], body["quantity"], head["quantity"], off_hand["quantity"]],
                "variant": [main_hand["variant"], foot["variant"], leg["variant"], body["variant"], head["variant"], off_hand["variant"]],
                "cur_durability": [main_hand["cur_durability"], foot["cur_durability"], leg["cur_durability"], body["cur_durability"], head["cur_durability"], off_hand["cur_durability"]],
                "max_durability": [main_hand["max_durability"], foot["max_durability"], leg["max_durability"], body["max_durability"], head["max_durability"], off_hand["max_durability"]],
            },
            // MineLand Style
            equip: {
                "main hand": main_hand,
                "foot": foot,
                "leg": leg,
                "body": body,
                "head": head,
                "off hand": off_hand,
            },


            // ===== Inventory =====
            //MineDojo Style
            inventory:this.getSimplifiedInventoryInMinedojoStyle(bot.inventory),

            //MineLand Style
            inventory_full_slot_count: (bot.inventory.inventoryEnd - bot.inventory.inventoryStart) - bot.inventory.emptySlotCount(),
            inventory_empty_slot_count: bot.inventory.emptySlotCount(),
            inventory_slot_count: (bot.inventory.inventoryEnd - bot.inventory.inventoryStart),
            inventory_all: this.getSimplifiedInventory(bot.inventory),


            // ===== Voxels =====
            //MineDojo Style
            voxels: this.getVoxels(bot),
            // ===== Face Vector =====
            face_vector: this.getFaceVector(bot.entity.yaw, bot.entity.pitch),
            // ===== Life Statistics =====
            life_stats: {
                "life": roundTo2(bot.health),
                "oxygen": (bot.oxygenLevel !== undefined ? roundTo2(bot.oxygenLevel) : 20),
                "armor": "TODO",
                "food": roundTo2(bot.food),
                "saturation": roundTo2(bot.foodSaturation),
                "is_sleeping": bot.isSleeping,
                "xp": bot.experience.points,

                "xp_level": bot.experience.level,
                "xp_progress": roundTo2(bot.experience.progress),
            },

            // ===== Location Statistics =====
            location_stats: {
                "pos": [
                    roundTo2(bot.entity.position.x),
                    roundTo2(bot.entity.position.y),
                    roundTo2(bot.entity.position.z),
                ],
                "yaw": roundTo2(bot.entity.yaw),
                "pitch": roundTo2(bot.entity.pitch),
                "biome_id": "TODO",
                "rainfall": roundTo2(bot.rainState),
                "temperature": "TODO",
                "can_see_sky": "TODO",
                "is_raining": bot.isRaining,
                "light_level": "TODO",
                "sky_light_level": "TODO",
                "sun_brightness": "TODO",
                "sea_level": "TODO",

                "vel": [
                    roundTo2(bot.entity.velocity.x),
                    roundTo2(bot.entity.velocity.y),
                    roundTo2(bot.entity.velocity.z),
                ],
                "is_on_ground": bot.entity.onGround,
            },

            // ===== Time =====
            tick: tick,
            time: bot.time.timeOfDay,
            day: bot.time.day,
            age: bot.time.age,


            // ===== World =====
            difficulty: bot.game.difficulty,

            // ===== Physics Attributes =====
            control_state: JSON.stringify(bot.controlState),

            // ===== Target Entities =====
            target_entities: this.getTargetEntities(bot),

            // ===== Sound =====
            sound: "placeholder",
        }
    }

    /**
     * Get a simplified item object.
     * The returned object contains only the name and count of the item.
     */
    static simplifiedItem(item) {
        if (item === null) return null
        return {
            "name": item.name,
            "count": item.count,
        }
    }

    /**
     * Get the name of an item.
     */
    static getItemName(item, defaultValue = null) {
        if (item === null) return defaultValue
        return item.name
    }

    /**
     * Get the information of an equipment
     */
    static getEquipmentInfo(item) {
        if (item === null) { return {
            "name": "air",
            "quantity": 0,
            "variant": "",
            "cur_durability": 0,
            "max_durability": 0,
        }} else { return {
            "name": item.name,
            "quantity": item.count,
            "variant": item.enchants,
            "cur_durability": item.maxDurability - item.durabiliityUsed,
            "max_durability": item.maxDurability,
        }}
    }

    /**
     * Get a simplified inventory object.
     * The returned object contains a list of names and counts of the items.
     */
    static getSimplifiedInventory(inventory) {
        let result = {}
        const inventoryStart = inventory.inventoryStart;
        const inventoryEnd = inventory.inventoryEnd;
        for (let i = inventoryStart; i < inventoryEnd; i++) {
            if(inventory.slots[i] === null) continue
            result[i] = {
                "name": inventory.slots[i].name,
                "count": inventory.slots[i].count,
            }
        }
        return result
    }
    /**
     * Get a simplified inventory object of minedojo style.
     */
    static getSimplifiedInventoryInMinedojoStyle(inventory) {
        let result = {
            "name":[],
            "quantity":[],
            "cur_durability":[],
            "max_durability":[],
        }
        const inventoryStart = inventory.inventoryStart;
        const inventoryEnd = inventory.inventoryEnd;
        for (let i = inventoryStart; i < inventoryEnd; i++) {
            if(inventory.slots[i] == null) {
                result["name"].push(null);
                result["quantity"].push(null);
                result["cur_durability"].push(null);
                result["max_durability"].push(null);
                continue;
            }
            result["name"].push(inventory.slots[i].name);
            result["quantity"].push(inventory.slots[i].count);
            if(inventory.slots[i].maxDurability) {
                result["max_durability"].push(inventory.slots[i].maxDurability);
                result["cur_durability"].push(inventory.slots[i].maxDurability - inventory.slots[i].nbt.value.Damage.value);
            }
            else {
                result["max_durability"].push(null);
                result["cur_durability"].push(null);
            }
            
        }
        // console.log(result);
        return result;
    }
    
    static getVoxels(bot) {
        let voxels = {
            "block_name":[[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]]],
            "is_collidable":[[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]]],
            "is_tool_not_required":[[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]]], 
            "blocks_movement":[[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]]],
            "is_liquid":[[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]]],
            "is_solid":[[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]]],
            "can_burn":[[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]]],
            "blocks_light":[[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]]],
            "cos_look_vec_angle":[[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]],[[null,null,null],[null,null,null],[null,null,null]]],
        }

        // console.log(bot)
        if(!bot || !bot.entity) {
            return voxels;
        }
        for(let i = 0; i < 3; ++i) {
            for(let j = 0; j < 3; ++j) {
                for(let k = 0; k < 3; ++k){
                    
                    if(!('position' in bot.entity)) continue
                    let block = bot.blockAt(bot.entity.position.offset(i - 1, j - 1, k - 1));
                    if(block === null) continue
                    voxels.block_name[i][j][k] = block.name;
                    voxels.is_collidable[i][j][k] = block.diggable;
                    voxels.is_tool_not_required[i][j][k] = block.harvestTools?false: true;
                    voxels.is_liquid[i][j][k] = (block.boundingBox === 'empty' && block.name !== 'air');
                    voxels.is_solid[i][j][k] = block.boundingBox === 'block';
                    // todo : voxels.can_burn[i][j][k] = block.boundingBox === 'block';
                    voxels.blocks_light[i][j][k] = !block.transparent;
                    // todo : voxels.cos_look_vec_angle[i][j][k] = block.boundingBox === 'block';


                }  
            }
        }
        // console.log(JSON.stringify(voxels,null, 2));
        return voxels;
    }
    static getFaceVector(yaw, pitch) {
        let face_vector = [-Math.sin(yaw), Math.sin(pitch), -Math.cos(yaw)]
        return face_vector

    }
    // Function to convert yaw and pitch to 3D vector
    static getVectorFromYawPitch(yaw, pitch) {
        const horizontalAngle = yaw * (Math.PI / 180); // Convert to radians
        const verticalAngle = pitch * (Math.PI / 180); // Convert to radians

        const x = Math.cos(verticalAngle) * Math.sin(horizontalAngle);
        const y = Math.sin(verticalAngle);
        const z = Math.cos(verticalAngle) * Math.cos(horizontalAngle);

        return [x,y,z]
    }

    // Function to calculate the dot product between two vectors
    static calculateDotProduct(vector1, vector2) {
        return vector1[0] * vector2[0] + vector1[1] * vector2[1] + vector1[2] * vector2[2];
    }

    // Function to get near special entities
    static getTargetEntities(bot) {
        let getName = (string) => string.substring(9, string.length - 2);
        const entities = Object.values(bot.entities).filter(entity => {
            return entity.metadata !== undefined && entity.metadata[2] !== undefined && entity.metadata[2] !== null;
        }).map((
            {position, metadata, name}
        ) => ({
            "name": getName(metadata[2]),
            "kind": name,
            "health": metadata[9],
            position, 
        }));
        return entities;
    }
}

module.exports = ObservationUtils;