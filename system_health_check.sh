#!/bin/bash
# 系统健康检查脚本

echo "🔍 系统健康检查 - $(date)"
echo "="*60

# 1. 监控进程
echo -e "\n📊 监控进程:"
if ps aux | grep "meme_monitor_simple.py" | grep -v grep > /dev/null; then
    PID=$(ps aux | grep "meme_monitor_simple.py" | grep -v grep | awk '{print $2}')
    UPTIME=$(ps -p $PID -o etime= 2>/dev/null)
    echo "  ✅ 运行中 (PID: $PID, 运行时间: $UPTIME)"
else
    echo "  ❌ 未运行"
fi

# 2. 钱包余额
echo -e "\n💰 钱包余额:"
cd /root/.openclaw/workspace
./meme_monitor_env/bin/python << 'EOF'
from full_auto_trader import Wallet
wallet = Wallet()
balance = wallet.get_balance()
print(f"  地址: {wallet.get_address()}")
print(f"  余额: {balance:.4f} SOL")
EOF

# 3. 定时任务
echo -e "\n⏰ 定时任务:"
CRON_COUNT=$(openclaw cron list | grep -c "enabled.*true")
echo "  活跃任务数: $CRON_COUNT"

# 4. 最近信号
echo -e "\n📡 最近信号:"
if [ -f "/root/.openclaw/workspace/meme_signals.json" ]; then
    SIGNAL_COUNT=$(grep -c "contract" /root/.openclaw/workspace/meme_signals.json 2>/dev/null || echo 0)
    echo "  发现信号: $SIGNAL_COUNT 个"
else
    echo "  无信号文件"
fi

# 5. 持仓
echo -e "\n📊 持仓:"
if [ -f "/root/.openclaw/workspace/positions.json" ]; then
    POS_COUNT=$(grep -c "contract" /root/.openclaw/workspace/positions.json 2>/dev/null || echo 0)
    echo "  当前持仓: $POS_COUNT 个"
else
    echo "  无持仓"
fi

echo -e "\n="*60
echo "✅ 检查完成"
