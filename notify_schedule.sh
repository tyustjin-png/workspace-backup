#!/bin/bash
# 读取日程文件并返回内容（供 OpenClaw cron 调用）

SCHEDULE_FILE="/tmp/schedule_message.txt"

if [ -f "$SCHEDULE_FILE" ]; then
    cat "$SCHEDULE_FILE"
else
    echo "❌ 日程文件不存在"
    exit 1
fi
