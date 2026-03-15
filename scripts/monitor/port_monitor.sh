#!/bin/bash
# 端口连通性监控脚本

LOG_FILE="/tmp/port_monitor.log"
ALERT_FILE="/tmp/port_alert.txt"

echo "[$(date)] 🔍 检查关键端口..." >> $LOG_FILE

# 测试 443 端口（Telegram API）
if timeout 3 bash -c "echo > /dev/tcp/api.telegram.org/443" 2>/dev/null; then
    echo "[$(date)] ✅ 443 端口正常" >> $LOG_FILE
else
    echo "[$(date)] ❌ 443 端口异常！" >> $LOG_FILE
    echo "⚠️ 警告：443 端口（HTTPS）不可达！所有外部API连接断开。请检查安全组设置。" > $ALERT_FILE
fi

# 检查 OpenClaw 状态
if pgrep -x "openclaw" > /dev/null; then
    echo "[$(date)] ✅ OpenClaw 运行中" >> $LOG_FILE
else
    echo "[$(date)] ❌ OpenClaw 未运行！" >> $LOG_FILE
    echo "⚠️ 警告：OpenClaw 进程停止！" >> $ALERT_FILE
fi
