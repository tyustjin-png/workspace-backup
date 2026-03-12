#!/bin/bash
# 日程助手子Agent包装脚本
# 接收用户输入，调用分类脚本，返回结果

USER_INPUT="$1"

if [ -z "$USER_INPUT" ]; then
    echo "❌ 错误：未提供输入内容"
    exit 1
fi

# 切换到工作目录
cd ~/.openclaw/workspace

# 调用日程管理器
RESULT=$(python3 daily_schedule_manager.py "$USER_INPUT" 2>&1)

# 返回结果
echo "$RESULT"

# 记录日志
echo "[$(date)] 处理输入：$USER_INPUT → 结果：$RESULT" >> /tmp/schedule_assistant.log
