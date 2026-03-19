#!/bin/bash
# 小定自动定投执行脚本

XIAODING_DIR="/Users/qianzhao/.openclaw/workspace/xiaoding"
WORKSPACE="/Users/qianzhao/.openclaw/workspace"
LOG_FILE="$XIAODING_DIR/data/dca_log.txt"
NOTIFY_FILE="/tmp/xiaoding_notify.txt"

cd "$XIAODING_DIR" || exit 1

echo "================================" >> "$LOG_FILE"
echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

# 执行定投
python3 "$XIAODING_DIR/binance_auto_buy.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 定投执行成功" >> "$LOG_FILE"
    
    # 生成通知内容
    echo "💰 小定定投执行完成" > "$NOTIFY_FILE"
    echo "" >> "$NOTIFY_FILE"
    tail -20 "$LOG_FILE" >> "$NOTIFY_FILE"
    
    # 更新日程状态（v2统一格式）
    python3 "$WORKSPACE/scripts/schedule/daily_schedule_v2.py" complete "定投" >> "$LOG_FILE" 2>&1
    echo "✅ 已更新日程" >> "$LOG_FILE"
else
    echo "❌ 定投执行失败，退出码: $EXIT_CODE" >> "$LOG_FILE"
    
    echo "⚠️ 小定定投执行失败" > "$NOTIFY_FILE"
    echo "" >> "$NOTIFY_FILE"
    echo "退出码: $EXIT_CODE" >> "$NOTIFY_FILE"
    echo "" >> "$NOTIFY_FILE"
    tail -30 "$LOG_FILE" >> "$NOTIFY_FILE"
fi

echo "================================" >> "$LOG_FILE"
exit $EXIT_CODE
