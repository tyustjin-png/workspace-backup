#!/bin/bash
# 每日07:00重置 heartbeat 状态文件

STATE_FILE="/Users/qianzhao/.openclaw/workspace/heartbeat_state.json"
TODAY=$(date '+%Y-%m-%d')

cat > "$STATE_FILE" << EOF
{
  "date": "$TODAY",
  "sent": {
    "xiaoding": false,
    "schedule_10": false,
    "schedule_15": false,
    "schedule_19": false
  }
}
EOF

echo "✅ Heartbeat 状态已重置: $TODAY"
