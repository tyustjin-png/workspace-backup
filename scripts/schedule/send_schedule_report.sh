#!/bin/bash
# 日程汇报主动推送脚本
# 替代原来的 generate_schedule_reminder.sh

WORKSPACE="/Users/qianzhao/.openclaw/workspace"
SCHEDULE_FILE="/tmp/schedule_message.txt"
LOG_FILE="/tmp/schedule_report.log"

cd "$WORKSPACE" || exit 1

# 生成最新日程汇报
python3 schedule_report.py > "$SCHEDULE_FILE" 2>&1

if [ ! -s "$SCHEDULE_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ❌ 日程汇报生成失败" >> "$LOG_FILE"
    exit 1
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ 日程汇报已生成" >> "$LOG_FILE"

# 主动推送到 Telegram
/Users/qianzhao/.openclaw/workspace/send_telegram_notification.sh "$(cat $SCHEDULE_FILE)"

if [ $? -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ 已推送到 Telegram" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') ❌ Telegram 推送失败" >> "$LOG_FILE"
    exit 1
fi

exit 0
