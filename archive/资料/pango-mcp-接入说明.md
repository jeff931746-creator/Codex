# pango-mcp 接入说明

根据《简介.docx》整理的 Cursor MCP 接入配置。

## 结论

- MCP 服务地址：`https://pango.forevernine.net/api/v2/mcp`
- 认证方式：`Authorization: Bearer <盘古token>`
- 推荐的 Cursor server 名称：`pango-skillsrv`

## 已创建配置

- [`.cursor/mcp.json`](/Users/mt/Documents/Codex/.cursor/mcp.json)

当前文件里使用的是占位 token，原因是文档要求的 `盘古token` 需要从飞书里的 `neeko-妮蔻` 申请，当前工作区没有真实密钥。

## 使用步骤

1. 打开 Cursor 的 MCP 设置。
2. 确认项目级 `.cursor/mcp.json` 已被识别。
3. 把 `__REPLACE_WITH_YOUR_PANGO_TOKEN__` 替换成真实的盘古 token。
4. 回到 MCP 列表页检查连接状态，绿灯表示成功。

## 文档要点

- `pango-mcp` 提供九九互动内部系统和内部数据，可供 agent 调用。
- 有权限中心控制，项目级权限不足时无法查询或操作对应项目。
- 环境强制隔离，操作类 tool 不能修改线上环境，只能改非发布环境。
- 工具涵盖：
  - 用户与项目查询
  - 服务端日志查询
  - 枚举配置读写与回滚
  - 游戏类配置读写上传
  - 非游戏类配置查询、增改和历史查看

## 备注

- 这是一个远程 HTTP 型 MCP，不是本地命令型 MCP。
- 如果你后面拿到真实 token，我可以继续帮你把占位值替换掉，并顺手做一次可用性检查。
