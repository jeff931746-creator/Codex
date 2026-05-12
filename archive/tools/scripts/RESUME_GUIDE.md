# 题材库构建 - 断点续传说明

## 幂等性设计

脚本已实现完整的断点续传机制，**中断后可直接重新运行，已完成的部分会自动跳过**。

### 工作原理

#### Phase 1: Discovery（作品收集）
- 每条查询的响应保存在 `_raw/2026-05-09_discovery_*.txt`
- 重新运行时，如果文件存在且 >100 bytes，**直接读取缓存，不调用 API**
- 日志显示：`[discovery_anime_y2024_b1] 使用已有缓存`

#### Phase 2: Analysis（题材分析）
- 每批分析的响应保存在 `_raw/2026-05-09_analysis_batch*.txt`
- 同样机制：已有缓存则跳过 API 调用

#### Phase 3: Clustering（聚类）
- 基于 Phase 2 的结果，重新运行会重新聚类（成本可忽略）

### 中断场景处理

#### 场景1：网络中断
```bash
# 现象：部分查询失败，日志显示 "Remote end closed connection"
# 处理：直接重新运行脚本
./run_theme_library.sh

# 结果：
# - 已成功的 400 条查询：使用缓存，秒级跳过
# - 失败的 275 条查询：重新执行
```

#### 场景2：进程被杀（Ctrl+C / kill）
```bash
# 现象：进程终止，部分查询未完成
# 处理：直接重新运行
./run_theme_library.sh

# 结果：
# - 已完成的查询：使用缓存
# - 未完成的查询：继续执行
```

#### 场景3：机器重启
```bash
# 现象：所有进程终止
# 处理：重启后重新运行
cd /Users/mt/Documents/Codex/archive/tools/scripts
export SILICONFLOW_API_KEY="sk-spvgu..."
./run_theme_library.sh

# 结果：从缓存恢复，继续未完成的部分
```

#### 场景4：API 限流（429 错误）
```bash
# 现象：硅基流动返回 429 Too Many Requests
# 处理：等待 5-10 分钟后重新运行
sleep 600 && ./run_theme_library.sh

# 结果：
# - 重试机制会自动处理临时限流（2s/4s/6s 递增等待）
# - 如果仍失败，记录到 FAILURES.md，可稍后手动重跑
```

### 查看进度

#### 实时监控
```bash
# 查看日志
tail -f theme_library_*.log

# 查看已完成的查询数
ls -1 /Users/mt/Documents/Codex/archive/资料/历史题材库/_raw/ | wc -l

# 预期文件数：
# - Discovery: 675 个文件
# - Analysis: 1350 个文件
# - 总计: 2025 个文件
```

#### 检查失败项
```bash
# 查看失败报告
cat /Users/mt/Documents/Codex/archive/资料/历史题材库/FAILURES.md
```

### 手动清理缓存（如果需要重新运行某些查询）

#### 清理特定年份
```bash
# 删除 2024 年的所有缓存
rm /Users/mt/Documents/Codex/archive/资料/历史题材库/_raw/*_y2024_*.txt

# 重新运行，只会重新查询 2024 年
./run_theme_library.sh
```

#### 清理特定类型
```bash
# 删除所有文学作品的缓存
rm /Users/mt/Documents/Codex/archive/资料/历史题材库/_raw/*_lit_*.txt

# 重新运行，只会重新查询文学作品
./run_theme_library.sh
```

#### 完全重新开始
```bash
# 删除所有缓存和输出
rm -rf /Users/mt/Documents/Codex/archive/资料/历史题材库/_raw
rm -rf /Users/mt/Documents/Codex/archive/资料/历史题材库/题材聚类
rm /Users/mt/Documents/Codex/archive/资料/历史题材库/*.md

# 重新运行
./run_theme_library.sh
```

### 成本控制

由于幂等性设计，**重新运行不会重复计费**：
- 已缓存的查询：0 成本
- 仅失败的查询会重新调用 API

示例：
- 第一次运行：完成 400/675 条，成本 ¥0.6
- 中断后重跑：只执行剩余 275 条，成本 ¥0.4
- **总成本：¥1.0**（不会因重跑而翻倍）

### 最佳实践

1. **使用 nohup 后台运行**
   ```bash
   nohup ./run_theme_library.sh &
   ```
   即使 SSH 断开，进程继续运行

2. **定期检查进度**
   ```bash
   # 每小时检查一次
   watch -n 3600 'ls -1 /Users/mt/Documents/Codex/archive/资料/历史题材库/_raw/ | wc -l'
   ```

3. **失败后立即重跑**
   - 不需要等待，直接重新运行
   - 缓存机制会自动跳过已完成的部分

4. **保留日志文件**
   - 每次运行生成新的日志文件（带时间戳）
   - 可用于排查问题和统计成本

### 常见问题

**Q: 如何判断是否真的完成了？**
```bash
# 检查文件数
ls -1 /Users/mt/Documents/Codex/archive/资料/历史题材库/_raw/ | wc -l
# 应该接近 2025（675 discovery + 1350 analysis）

# 检查失败报告
cat /Users/mt/Documents/Codex/archive/资料/历史题材库/FAILURES.md
# 如果显示 "无"，则全部成功
```

**Q: 部分查询一直失败怎么办？**
```bash
# 1. 删除失败查询的缓存
rm /Users/mt/Documents/Codex/archive/资料/历史题材库/_raw/*_lit_y2024_b2.txt

# 2. 单独重跑（降低并发度）
# 编辑脚本，临时将并发度改为 3
# 然后重新运行
```

**Q: 如何估算剩余时间？**
```bash
# 查看已完成的文件数
DONE=$(ls -1 /Users/mt/Documents/Codex/archive/资料/历史题材库/_raw/ | wc -l)
TOTAL=2025
REMAINING=$((TOTAL - DONE))

# 假设平均每个查询 1 分钟
echo "剩余约 $((REMAINING / 10)) 小时"
```
