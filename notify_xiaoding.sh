#!/bin/bash
# 读取定投通知并返回内容（供 OpenClaw cron 调用）

NOTIFY_FILE="/tmp/xiaoding_notify.txt"

if [ -f "$NOTIFY_FILE" ]; then
    cat "$NOTIFY_FILE"
else
    echo "❌ 定投通知文件不存在"
    exit 1
fi
