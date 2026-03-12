#!/bin/bash
# 内存监控脚本

# 获取内存使用百分比
mem_used=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')

# 超过 80% 发出警告
if [ "$mem_used" -gt 80 ]; then
    echo "⚠️ 内存警告：使用率 ${mem_used}%" > /tmp/memory_alert.txt
    free -h >> /tmp/memory_alert.txt
    echo "---" >> /tmp/memory_alert.txt
    ps aux --sort=-%mem | head -10 >> /tmp/memory_alert.txt
fi
