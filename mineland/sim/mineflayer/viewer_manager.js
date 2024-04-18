const net = require('net');
// const puppeteer = require('puppeteer');
// const mineflayerViewer = require('prismarine-viewer-colalab').mineflayer;
const mineflayerHeadless = require('prismarine-viewer-colalab').headless;
const mineflayerFreecamera = require('prismarine-viewer-colalab').freecamera;

/**
 * A normal mutex lock class.
 */
class Lock {
    constructor() {
        this._locked = false;
        this._waiting = [];
    }

    async acquire() {
        while (this._locked) {
            await new Promise(resolve => this._waiting.push(resolve));
        }
        this._locked = true;
    }

    release() {
        this._locked = false;
        if (this._waiting.length > 0) {
            const resolve = this._waiting.shift();
            resolve();
        }
    }
}

/**
 * ViewerManager is responsible for creating viewers on bots and save their infomation.
 */
class ViewerManager {

    /**
     * Construct a viewer manager.
     */
    constructor() {
        this.lock = undefined
        this.views = {}
        this.image_width = 0
        this.image_height = 0

        this.cameras = {}
        this.cameras_loc = {}
        this.cameras_page = {}
    }

    /* ===== Bots' viewer ===== */

    /**
     * Try to listen to a port.
     * If the port has been occupied, try the next port until success.
     */
    async tryListening(port) {
        return new Promise((resolve, reject) => {
            const server = net.createServer();

            server.listen(port, '127.0.0.1')

            server.on('listening', function() {
                server.close();
                resolve(port)
            });
            
            server.on('error', function(err) {
                server.close()
                if (err.code === 'EADDRINUSE') {
                    resolve(tryListening(port + 1)); // Try the next port
                } else {
                    reject(new Error("Failed to find empty port and an error occurred: " + err.message))
                }
            })
        })
    }

    /**
     * Create viewers on all bots.
     * This function is asynchronous.
     */
    async createViewerOnAllBots(bots, image_width, image_height) {
        this.lock = new Lock()
        this.views = {}
        this.image_width = image_width
        this.image_height = image_height

        for (let i = 0; i < bots.length; i++) {
            bots[i].on("spawn", async () => {
                // await this.lock.acquire()
                // let port = await this.tryListening(start_port)
                // start_port = port + 1
                mineflayerHeadless(bots[i], this.views, { viewDistance: 3, height: image_height, width: image_width })
                // this.lock.release()

                // setInterval(async() => {
                //     // await page.screenshot({ path: `./assets/${bots[i].username}.jpg`})
                //     this.pics[bots[i].username] = await page.screenshot({ encoding: 'base64' })
                // }, 250)
            })
        }
    }

    async createViewerOnBot(bots, index, image_width, image_height) {
        bots[index].on("spawn", async () => {
            mineflayerHeadless(bots[index], this.views, { viewDistance: 3, height: image_height, width: image_width })
        })
    }

    /**
     * Get the first person view image of the bot in base64 format.
     * Be careful! The returned object may be null in the beginning.
     */
    getBotViewByName(name) {
        return this.views[name]
    }

    /* ===== Camera ===== */

    /**
     * Create a camera
     */
    async addCamera(bot, camera_id, image_width, image_height) {
        // get lock to request a port
        // await this.lock.acquire()
        // let port = await this.tryListening(start_port)
        this.cameras[camera_id] = mineflayerFreecamera(bot, { viewDistance: 3, height: image_height, width: image_width })
        // this.lock.release()

        this.cameras_loc[camera_id] = {
            pos: bot.entity.position.offset(0, 1.6, 0),
            yaw: 0,
            pitch: 0,
        }
        this.cameras[camera_id].set(this.cameras_loc[camera_id])
    }

    /**
     * Get a screenshot of a camera in base64 format.
     */
    getCameraView(camera_id) {
        return this.cameras[camera_id].get()
    }

    /**
     * Modify the location of a camera
     */
    modifyCameraLoc(camera_id, pos, yaw, pitch) {
        this.cameras_loc[camera_id].pos = pos
        this.cameras_loc[camera_id].yaw = yaw
        this.cameras_loc[camera_id].pitch = pitch
        this.cameras[camera_id].set(this.cameras_loc[camera_id])
    }

    /**
     * Make the camera forward
     */
    forwardCamera(camera_id, d) {

        // console.log("before add : ")
        // console.log(this.cameras_loc[camera_id].pos.x, this.cameras_loc[camera_id].pos.y, this.cameras_loc[camera_id].pos.z,this.cameras_loc[camera_id].yaw, this.cameras_loc[camera_id].pitch)
        
        // console.log(d_yaw, d_pitch)

        const yaw = this.cameras_loc[camera_id].yaw
        const forward_x = -d * Math.sin(yaw)
        const forward_y = 0
        const forward_z = -d * Math.cos(yaw)

        // console.log("after add : ")
        // console.log(this.cameras_loc[camera_id].pos.x, this.cameras_loc[camera_id].pos.y, this.cameras_loc[camera_id].pos.z, this.cameras_loc[camera_id].yaw, this.cameras_loc[camera_id].pitch)
        this.cameras_loc[camera_id].pos = this.cameras_loc[camera_id].pos.offset(forward_x, forward_y, forward_z)
    }
    /**
     * Make the camera move right
     */
    rightCamera(camera_id, d) {
        const yaw = this.cameras_loc[camera_id].yaw
        const right_x = d * Math.cos(yaw)
        const right_y = 0
        const right_z = -d * Math.sin(yaw)
        this.cameras_loc[camera_id].pos = this.cameras_loc[camera_id].pos.offset(right_x, right_y, right_z)

    }
    /**
     * Make the camera move up
     */
    upCamera(camera_id, d) {
        this.cameras_loc[camera_id].pos = this.cameras_loc[camera_id].pos.offset(0, d, 0)
    }

    /**
     * add a vector to the Loc of a camera
     */
    addCameraLoc(camera_id, d_pos, d_yaw, d_pitch) {
        // console.log("before add : ")
        // console.log(this.cameras_loc[camera_id].pos.x, this.cameras_loc[camera_id].pos.y, this.cameras_loc[camera_id].pos.z,this.cameras_loc[camera_id].yaw, this.cameras_loc[camera_id].pitch)
        
        // console.log(d_yaw, d_pitch)

        this.cameras_loc[camera_id].pos = this.cameras_loc[camera_id].pos.offset(d_pos.x, d_pos.y, d_pos.z)
        this.cameras_loc[camera_id].yaw += d_yaw
        this.cameras_loc[camera_id].pitch += d_pitch
        // console.log("after add : ")
        // console.log(this.cameras_loc[camera_id].pos.x, this.cameras_loc[camera_id].pos.y, this.cameras_loc[camera_id].pos.z, this.cameras_loc[camera_id].yaw, this.cameras_loc[camera_id].pitch)
        this.cameras[camera_id].set(this.cameras_loc[camera_id])
    }
    /**
     * Modify the position of a camera
     */
    modifyCameraPos(camera_id, pos) {
        this.cameras_loc[camera_id].pos = pos
        this.cameras[camera_id].set(this.cameras_loc[camera_id])
    }

    

    /**
     * Modify the compass of a camera
     */
    modifyCameraCompass(camera_id, yaw, pitch) {
        this.cameras_loc[camera_id].yaw = yaw
        this.cameras_loc[camera_id].pitch = pitch
        this.cameras[camera_id].set(this.cameras_loc[camera_id])
    }
}

module.exports = ViewerManager;