#!/bin/bash
# 生成日程提醒消息并立即推送

WORKSPACE="/Users/qianzhao/.openclaw/workspace"
OUTPUT_FILE="/tmp/schedule_message.txt"
STATE_FILE="$WORKSPACE/heartbeat_state.json"

# 获取当前小时（用于状态追踪）
HOUR=$(date +%H)

# 生成当天日程汇报
cd "$WORKSPACE" && python3 schedule_report.py > "$OUTPUT_FILE" 2>&1

# 检查是否成功生成
if [ ! -s "$OUTPUT_FILE" ]; then
    echo "❌ 日程汇报生成失败"
    exit 1
fi

# 读取消息内容
MESSAGE=$(cat "$OUTPUT_FILE")

# 立即推送（使用 OpenClaw 内部推送机制）
# 注意：这里应该调用 OpenClaw CLI，但我们先写入标记文件让 heartbeat 立即推送
echo "$MESSAGE" > "/tmp/schedule_push_${HOUR}.txt"

# 更新状态文件
python3 << EOF
import json
from datetime import datetime

try:
    with open("$STATE_FILE", "r") as f:
        state = json.load(f)
except:
    state = {"date": datetime.now().strftime("%Y-%m-%d"), "sent": {}}

# 标记为待推送（而非已推送）
hour_key = f"schedule_{HOUR}"
state["sent"][hour_key] = False  # 让 heartbeat 推送
state[f"{hour_key}_generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

with open("$STATE_FILE", "w") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print(f"✅ 日程汇报已生成，等待推送: {hour_key}")
EOF

exit 0
