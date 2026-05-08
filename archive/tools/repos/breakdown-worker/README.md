# breakdown-worker

用大模型批量产出游戏机制拆解初稿，Claude 审校后落到 `机制库/`。支持 **SiliconFlow（默认）** 和 **Gemini**。

This workflow follows the root workspace session protocol in [`/Users/mt/Documents/Codex/CLAUDE.md`](/Users/mt/Documents/Codex/CLAUDE.md).

## 用法

```bash
# 1. 把游戏资料放进 inputs/<游戏名>/（.md 或 .txt）
mkdir -p inputs/某游戏
cp ~/Downloads/*.md inputs/某游戏/

# 2. 出初稿（默认走 SiliconFlow + GLM-5.1）
python3 run.py --game "某游戏"

# 3. 跟 Claude 说："审校 某游戏"
#    Claude 读 outputs/某游戏/ → 按《拆解质量标准》改 → 写入 机制库/某游戏/
```

## 选项

- `--provider gemini`：切到 Gemini
- `--model Pro/zai-org/GLM-4.5`：覆盖默认模型
- `--dry-run`：只导出完整 prompt 到 `_dryrun_<game>.txt`，不调 API

## 环境

`.env` 里放：

```
PROVIDER=siliconflow                        # 或 gemini

SILICONFLOW_API_KEY=sk-...
SILICONFLOW_MODEL=Pro/zai-org/GLM-5.1
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.5-pro
```

## 工作原理

1. 读 `prompts/system.md`（规则）
2. 读 `机制库/拆解质量标准.md`（必过标准）
3. 读 `机制库/保卫向日葵/` 整套（作为 few-shot 范式）
4. 读 `inputs/<游戏名>/` 下所有资料
5. 按 `--provider` 调对应 API，要求响应用 `===FILE: xxx===` 分隔多个文件
6. 拆分并写到 `outputs/<游戏名>/`
