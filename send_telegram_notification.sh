#!/bin/bash
# 统一 Telegram 通知脚本
# 用法: ./send_telegram_notification.sh "消息内容"

MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    echo "❌ 错误: 未提供消息内容"
    echo "用法: $0 '消息内容'"
    exit 1
fi

# 通过 openclaw message 发送
openclaw message send --target telegram --message "$MESSAGE" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 通知已发送"
    exit 0
else
    echo "❌ 通知发送失败"
    exit 1
fi
