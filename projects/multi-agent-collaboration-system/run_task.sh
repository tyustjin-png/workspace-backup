#!/bin/bash
# 多 Agent 系统快捷启动脚本

if [ $# -eq 0 ]; then
    echo "用法: ./run_task.sh '任务描述'"
    echo "示例: ./run_task.sh '搜索 OpenAI o3 并改写成推文'"
    exit 1
fi

TASK="$*"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔════════════════════════════════════════════════════════╗"
echo "║         多 Agent 协作系统                              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📋 任务: $TASK"
echo ""

cd "$SCRIPT_DIR"
python3 src/master_agent.py "$TASK"

echo ""
echo "💡 提示: 将上述执行计划发给紫龙，让他执行流水线"
echo "或者直接说: '紫龙，用多 agent 系统执行这个任务'"
