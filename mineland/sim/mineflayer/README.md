# Mineland-Mineflayer

* 因为之前的依赖依托，所以重组一下

## How to build & run

* ```bash
  pnpm install
  pnpm build # 需要编译mineflayer-collectblock等库
  ```

* 注意，每次修改 `src/lib/uncompiled/mineflayer-collectblock` 等需要编译的库（即typescript库）之后，都需要执行 `pnpm build`，对这些库进行编译！

  * 编译源文件通常位于  `src/lib/uncompiled/lib_name` 
  * 编译结果通常位于 `src/lib/lib_name`

