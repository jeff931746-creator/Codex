#!/bin/bash
# 确保环境变量
export SILICONFLOW_API_KEY="${SILICONFLOW_API_KEY}"
export DEEPSEEK_FLASH_MODEL="${DEEPSEEK_FLASH_MODEL:-deepseek-ai/DeepSeek-V4-Flash}"

# 生成日志文件名
LOG_FILE="theme_library_$(date +%Y%m%d_%H%M%S).log"

echo "=========================================="
echo "题材库构建开始"
echo "=========================================="
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "日志文件: $LOG_FILE"
echo "预计完成: $(date -v+7H '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 后台运行
nohup python3 build_historical_theme_library.py > "$LOG_FILE" 2>&1 &
PID=$!

echo "✅ 已启动（PID: $PID）"
echo ""
echo "监控命令："
echo "  tail -f $LOG_FILE"
echo "  ps -p $PID"
echo ""
echo "进度查看："
echo "  ls -1 ../../../资料/历史题材库/_raw/ | wc -l"
echo ""

# 等待3秒确认启动
sleep 3
if ps -p $PID > /dev/null; then
    echo "✅ 进程运行正常"
    echo ""
    echo "前10行日志："
    head -10 "$LOG_FILE"
else
    echo "❌ 进程启动失败，查看日志："
    cat "$LOG_FILE"
fi
