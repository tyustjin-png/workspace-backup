#!/bin/bash
# 检查是否需要发送日程提醒

cd ~/.openclaw/workspace

CURRENT_HOUR=$(date +%H)
TODAY=$(date +%Y-%m-%d)
STATE_FILE="/tmp/schedule_reminder_state.json"

# 初始化状态文件
if [ ! -f "$STATE_FILE" ] || [ "$(jq -r .date 2>/dev/null < "$STATE_FILE")" != "$TODAY" ]; then
    echo "{\"date\":\"$TODAY\",\"reminded\":{\"10\":false,\"15\":false,\"19\":false,\"20\":false}}" > "$STATE_FILE"
fi

# 检查是否该提醒
should_remind() {
    local hour=$1
    local reminded=$(jq -r ".reminded.\"$hour\"" < "$STATE_FILE")
    
    if [ "$CURRENT_HOUR" == "$hour" ] && [ "$reminded" == "false" ]; then
        return 0  # 需要提醒
    fi
    return 1  # 不需要提醒
}

# 标记已提醒
mark_reminded() {
    local hour=$1
    jq ".reminded.\"$hour\" = true" < "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
}

# 检查并发送提醒
send_reminder() {
    local hour=$1
    local type=$2  # "reminder" 或 "summary"
    
    if should_remind "$hour"; then
        if [ "$type" == "summary" ]; then
            python3 daily_schedule_manager.py --summary > /tmp/schedule_message.txt
        else
            python3 daily_schedule_manager.py --reminder > /tmp/schedule_message.txt
        fi
        
        mark_reminded "$hour"
        echo "sent"  # 返回"已发送"标记
    fi
}

# 执行检查
if [ "$CURRENT_HOUR" == "10" ]; then
    send_reminder "10" "reminder"
elif [ "$CURRENT_HOUR" == "15" ]; then
    send_reminder "15" "reminder"
elif [ "$CURRENT_HOUR" == "19" ]; then
    send_reminder "19" "reminder"
elif [ "$CURRENT_HOUR" == "20" ]; then
    send_reminder "20" "summary"
fi
