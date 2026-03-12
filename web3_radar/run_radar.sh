#!/bin/bash
# Web3 早期项目雷达执行脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
LOG_FILE="$SCRIPT_DIR/radar.log"

# 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_DIR" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 创建虚拟环境..." >> "$LOG_FILE"
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" -q
fi

# 运行脚本
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行雷达扫描..." >> "$LOG_FILE"
"$VENV_DIR/bin/python3" "$SCRIPT_DIR/email_radar.py" >> "$LOG_FILE" 2>&1

# 结果通知
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 执行成功" >> "$LOG_FILE"
    echo "✅ Web3 雷达执行成功" > /tmp/web3_radar_notify.txt
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 执行失败" >> "$LOG_FILE"
    echo "❌ Web3 雷达执行失败，检查日志: $LOG_FILE" > /tmp/web3_radar_notify.txt
fi
