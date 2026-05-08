# 模块槽位塔防：API 自动出图方案

## 现在这套方案能做什么

- 不再依赖 Gemini 网页
- 默认调用官方 Gemini 原生图片生成 API
- 也保留 Imagen API 作为可选后端
- 自动读取玩法图 prompt
- 自动保存图片到本地文件夹
- 自动保存对应 prompt 和原始 API 响应

## 前提

你需要先提供一个 `GEMINI_API_KEY`。

当前环境里还没有设置这个变量。

## 设置方式

临时设置当前终端：

```bash
export GEMINI_API_KEY="你的key"
```

如果想长期生效，可以写进 `~/.zshrc`。

## 运行方式

生成整套 1 到 6：

```bash
/Library/Frameworks/Python.framework/Versions/3.10/bin/python3 \
  /Users/mt/Documents/Codex/模块槽位塔防/generate_gameplay_series_via_api.py
```

只生成指定编号：

```bash
/Library/Frameworks/Python.framework/Versions/3.10/bin/python3 \
  /Users/mt/Documents/Codex/模块槽位塔防/generate_gameplay_series_via_api.py 2 3 4
```

每张图一次生成 2 张备选：

```bash
/Library/Frameworks/Python.framework/Versions/3.10/bin/python3 \
  /Users/mt/Documents/Codex/模块槽位塔防/generate_gameplay_series_via_api.py \
  --sample-count 2
```

如果你有可用的 Imagen 付费计划，也可以手动切换：

```bash
/Library/Frameworks/Python.framework/Versions/3.10/bin/python3 \
  /Users/mt/Documents/Codex/模块槽位塔防/generate_gameplay_series_via_api.py \
  --backend imagen
```

## 输出位置

图片会保存到：

[玩法图片输出_api](/Users/mt/Documents/Codex/模块槽位塔防/玩法图片输出_api)

每个编号会有自己的子目录，里面包含：

- `prompt.txt`
- `response.json`
- `图X_xxx.png`

## Prompt 来源

- 图 1：来自 [模块槽位塔防_玩法图Prompts.md](/Users/mt/Documents/Codex/模块槽位塔防/模块槽位塔防_玩法图Prompts.md)
- 图 2 到图 6：来自 [图2-图6_布局锁定修正版Prompts.md](/Users/mt/Documents/Codex/模块槽位塔防/图2-图6_布局锁定修正版Prompts.md)

这样图 2 之后默认都走“强制继承图 1 布局”的版本。
