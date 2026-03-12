#!/bin/bash
# 监控脚本守护进程 - 确保监控永远在线

LOG_FILE="/tmp/meme_monitor.log"
PID_FILE="/tmp/meme_monitor.pid"
SCRIPT="/root/.openclaw/workspace/meme_monitor_simple.py"
PYTHON="/root/.openclaw/workspace/meme_monitor_env/bin/python"

# 检查进程是否运行
check_running() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# 启动监控
start_monitor() {
    cd /root/.openclaw/workspace
    nohup $PYTHON $SCRIPT > $LOG_FILE 2>&1 &
    echo $! > $PID_FILE
    echo "[$(date)] 监控已启动，PID: $(cat $PID_FILE)" >> /tmp/watchdog.log
}

# 主逻辑
if ! check_running; then
    echo "[$(date)] ⚠️  监控脚本已停止，正在重启..." >> /tmp/watchdog.log
    start_monitor
else
    echo "[$(date)] ✅ 监控脚本正常运行" >> /tmp/watchdog.log
fi
