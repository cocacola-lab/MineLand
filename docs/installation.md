# Installation Documentation

* TODO

## Q&A

* Why server reports `Netty Server IO ERROR, Thread dumps`

  * ![qa1](./pics/qa1.png)
  * In fact, the cause of this problem is unknown. This may be related to personal computer configuration.
  * **Answer**
    * Restart MineLand to try again.

* Why mineflayer reports `Type Error: Cannot read properties of undefined (reading 'yaw')

  * ![qa2](./pics/qa2.png)

  * **Answer**

    * The bot has not been fully initialized yet.

    * You can increase the initialization duration in `app.post("/start"...)` of `./mineland/sim/mineflayer/index.js`.

    * ```javascript
      setTimeout(() => {
          obs = []
          for(let i = 0; i < number_of_bot; i++) {
              obs.push(bot_manager.getBotObservation(i));
          }
          res.status(200).json({
              return_code: 200,
              observation: obs,
          })
      }, 20000) // wait for 20 seconds to make sure all bots are spawned
      // You can change 20000 to 30000 to avoid this problem
      ```