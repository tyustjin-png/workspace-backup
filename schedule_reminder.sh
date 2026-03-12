#!/bin/bash
# 每日日程提醒脚本

cd ~/.openclaw/workspace

# 获取提醒内容
REMINDER=$(python3 daily_schedule_manager.py --reminder)

# 发送到 Telegram（通过 OpenClaw）
# 注意：这里需要通过主session来发送消息
# 由于是cron触发，我们写入临时文件让主session读取

REMINDER_FILE="/tmp/schedule_reminder.txt"
echo "$REMINDER" > "$REMINDER_FILE"

# 记录日志
echo "[$(date)] 提醒已生成: $REMINDER_FILE" >> /tmp/schedule_reminder.log
