#!/bin/bash
# 题材库构建启动脚本

set -e

cd "$(dirname "$0")"

# 检查环境变量
if [ -z "$SILICONFLOW_API_KEY" ]; then
    echo "❌ 错误：未设置 SILICONFLOW_API_KEY"
    echo "请运行：export SILICONFLOW_API_KEY='your-key'"
    exit 1
fi

# 设置默认模型
export DEEPSEEK_FLASH_MODEL="${DEEPSEEK_FLASH_MODEL:-deepseek-ai/DeepSeek-V4-Flash}"

echo "=========================================="
echo "题材库构建工具"
echo "=========================================="
echo "模型：$DEEPSEEK_FLASH_MODEL"
echo "输出：/Users/mt/Documents/Codex/archive/资料/历史题材库"
echo "预计时间：13-15小时"
echo "预计成本：¥1.0"
echo ""
echo "优化配置："
echo "  - 重试机制：3次（递增等待2s/4s/6s）"
echo "  - 超时时间：180秒"
echo "  - 并发度：Discovery 10 / Analysis 8"
echo "=========================================="
echo ""

read -p "确认开始运行？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 后台运行并记录日志
LOG_FILE="theme_library_$(date +%Y%m%d_%H%M%S).log"
echo "开始运行，日志文件：$LOG_FILE"
echo ""

nohup python3 build_historical_theme_library.py > "$LOG_FILE" 2>&1 &
PID=$!

echo "✅ 已启动（PID: $PID）"
echo ""
echo "监控命令："
echo "  tail -f $LOG_FILE          # 实时查看日志"
echo "  ps -p $PID                 # 检查进程状态"
echo "  kill $PID                  # 停止运行"
echo ""
echo "预计完成时间：$(date -v+15H '+%Y-%m-%d %H:%M')"
