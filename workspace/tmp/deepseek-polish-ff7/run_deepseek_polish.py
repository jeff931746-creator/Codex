#!/usr/bin/env python3
"""Run DeepSeek wording polish for the FF 7-day social-chain draft."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from archive.tools.lib.llm_client import chat_text

TARGET = ROOT / "workspace/projects/开发中/FF-指尖战记/策划/输出/7日强社交功能链路/文档/FF-7日强社交功能链路细化设计稿.md"
OUT = ROOT / "workspace/tmp/deepseek-polish-ff7/deepseek-polished-v2.md"


SYSTEM = """你是资深中文游戏策划编辑。你的任务不是把文本改得更“规范”，而是把它改得更像一篇能被策划、制作人和系统负责人顺着读下去的中文设计说明。

硬约束：
1. 只基于用户提供的原文改写，不新增外部事实、功能、数值或系统。
2. 保留 Markdown 结构、表格、代码块、Mermaid 图、D1-D7 主链和军团承接逻辑。
3. 不把研究稿改成单功能 GDD，不新增需求模板口吻，不把正文写成接口说明、后端规则或清单堆叠。
4. 重点改“读起来很累、没有终点”的问题：每一章先给终点判断，再说明路径和边界。
5. 尤其重写最后一章“军团首周承接框架”的章法：不要保留密密麻麻的九段说明感，要改成有起点、转折、落点的文章结构。可以调整最后一章的小节标题和段落组织，但不要丢失原有设计含义。
6. 语言要中文化、自然、干净。尽量少用英文词汇；D1-D7、PVEVP、GDD、Markdown、Mermaid 等原文必要缩写可以保留。
7. 避免高频重复“承接、进度、目标、组织、可见、需求”等词。能换成玩家行为、系统反馈、下一步去向的表达，就不要反复堆概念名词。
8. 不输出说明、清单、差异解释，只输出完整 Markdown 正文。
"""


def main() -> None:
    source = TARGET.read_text(encoding="utf-8")
    prompt = f"""请基于以下 Markdown 文档内容，做一次更中文化、更像文章的修饰。

优化目标：
- 让句子更顺、更像中文策划文章，而不是程序化的机制清单。
- 保留“个人成长 -> 多人感知 -> 公共收益 -> 高风险争夺 -> 战报仇人 -> 军团求助/协作 -> 军团共同目标”的机制链。
- 标题尽量表达设计动作或机制转化，不写“为什么/问题/思路/分析链”。
- 不新增示例化内容，不新增未在原文出现的抽象概念。
- 尽量少用英文词汇，能用中文表达的不要写英文；原文必要缩写可保留。
- “设计口径”章节要有明确终点：首周不是解释所有机制，而是说明玩家最后为什么会需要军团，以及 D7 之后为什么还有继续参与的理由。
- “军团首周承接框架”章节需要重组，不要保留密集的九小节说明。建议改成 4-6 个小节，每节都有清楚落点：玩家为何入团、个人收益如何变成共同收益、战报如何变成可处理事件、成员如何协作、首周如何落到后续军团玩法。
- 不要为了压缩而变空泛；保留必要的机制边界，如基础收益、额外收益、战报记录、求助、协助、防无限复仇、弱势玩家/低活跃玩家的保底。

原文如下：

```markdown
{source}
```
"""
    result = chat_text(
        prompt,
        system=SYSTEM,
        route="DeepSeek_Official_Pro",
        max_tokens=9000,
        temperature=0.2,
        timeout=300,
    )
    cleaned = result.strip()
    if cleaned.startswith("```markdown"):
        cleaned = cleaned.removeprefix("```markdown").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()
    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()
    OUT.write_text(cleaned + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
