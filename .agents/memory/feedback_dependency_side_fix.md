---
name: feedback-dependency-side-fix
description: "环境/依赖类故障优先从依赖侧补足，不要只改坏掉的组件，不过早下\"无解\"结论"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1f72e28b-3192-4c5d-9607-eec8e14b2df2
---

遇到"某组件因找不到依赖而失败"的问题（如 hook 报 `jq not on PATH`），不要只盯着改那个组件本身（改它的配置、改它的 PATH、禁用它）。组件改不动 ≠ 无解——反向想：能不能把依赖送到它能找到的地方。

**Why:** GDD 方法论沉淀后 commit 被一个 skills-plugin 运行时注入的 hook 拦截（它用 jq，但运行环境 PATH 里没有 jq）。我先试改 hook 配置、改全局 settings.json 的 env.PATH，都失败，于是过早下了"修不了，只能终端提交"的结论。用户两次追问"是不是真没办法 / 还是你不想解决"，才逼我想到正解：jq 在 `/usr/bin/jq`，而 hook 按 homebrew 习惯在 `/opt/homebrew/bin` 找，`ln -s /usr/bin/jq /opt/homebrew/bin/jq` 让 hook 找到 jq，一次解决且持久。报错那句 "install jq" 本就指明了依赖该放哪，我当时没读懂。

**How to apply:** 故障排查先把问题分两侧——"坏掉的组件"侧 vs "它依赖的环境"侧。组件够不到/改不动时，转向补足依赖（往往更简单、更持久）。下"无解/修不了"结论前，先自查"我是不是只试了一侧"。报错信息里的修复建议（如 "install X"）常常直接指向依赖该放的位置。这与 [[feedback-system-vs-linear-thinking]] 一脉相承：先理解对方（这里是 hook）实际怎么找依赖，再对症，而不是按自己假设的方式硬改。
