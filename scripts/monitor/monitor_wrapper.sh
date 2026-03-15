#!/bin/bash
# Meme 币监控包装脚本
# 监控程序运行，发现通知后通过 OpenClaw 发送

WORKSPACE="/root/.openclaw/workspace"
NOTIFY_FILE="/tmp/meme_monitor_notify.txt"
PYTHON_ENV="$WORKSPACE/meme_monitor_env/bin/python"

cd $WORKSPACE

# 清空旧通知
rm -f $NOTIFY_FILE

# 后台运行监控
$PYTHON_ENV meme_monitor_mvp.py &
MONITOR_PID=$!

echo "🐉 监控系统已启动 (PID: $MONITOR_PID)"
echo "📝 监控日志: $WORKSPACE/monitor.log"
echo "💬 通知将发送到 Telegram"
echo ""
echo "停止监控: kill $MONITOR_PID"
