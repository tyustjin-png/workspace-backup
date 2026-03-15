# 🤖 自动交易系统配置

**启用时间**: 2026-02-03 14:53  
**状态**: ✅ 运行中（PID 1087963）

---

## 💰 钱包信息

- **地址**: `7tLcKDnqBwvs3ZSz99qU6PcWYqhq73N3tsCfv96kQvyB`
- **当前余额**: 4.0000 SOL
- **私钥位置**: `~/.config/solana/trading-bot.json`

---

## ⚙️ 风控参数（当前设置）

```python
# 交易限额
MAX_PER_TRADE = 1.0 SOL      # 单笔最多 1 SOL
DAILY_LIMIT = 3.0 SOL        # 每日最多 3 SOL

# 信号过滤
MIN_SCORE = 70               # 最低评分 70 分
MIN_LIQUIDITY = $10,000      # 最低流动性

# 止盈止损
STOP_LOSS = -50%             # -50% 止损
TAKE_PROFIT_BREAKEVEN = +100%  # 翻倍卖出 50% 回本
```

---

## 📊 评分分配（100 分制）

| 维度 | 权重 | 说明 |
|------|------|------|
| Moltbook 热度 | 30% | upvotes / 1000 * 30 |
| 流动性 | 25% | >$100k=25, >$50k=20, >$30k=15, >$10k=10 |
| 交易量 | 25% | >$500k=25, >$100k=20, >$50k=15 |
| 早期加分 | 15% | <3h 且活跃（交易量/流动性>10） |
| 交易笔数 | 5% | >5000=5, >2000=3, >1000=2 |

---

## 💸 买入金额规则

根据评分自动决定：

- **85+ 分** → 1.0 SOL（强烈推荐）
- **75-84 分** → 0.5 SOL（推荐）
- **70-74 分** → 0.2 SOL（及格）
- **<70 分** → 跳过

---

## 🔄 运行逻辑

```
1. 每 5 分钟扫描一次 Moltbook 最新帖子
2. 提取合约地址（Solana + Base）
3. 查询 DexScreener 获取代币数据
4. AI 评分
5. 过滤（评分 >= 70，流动性 >= $10k）
6. 风控检查（单笔限额、每日限额、余额）
7. 调用 Jupiter Swap 自动买入
8. 记录交易历史
9. Telegram 通知金哥
```

---

## 📁 关键文件

| 文件 | 说明 |
|------|------|
| `meme_monitor_simple.py` | 监控脚本（持续运行） |
| `full_auto_trader.py` | 自动交易执行器 |
| `meme_signals.json` | 信号缓存 |
| `trade_history.json` | 交易记录（自动创建） |
| `/tmp/meme_monitor.log` | 运行日志 |
| `/tmp/meme_notify_pending.json` | 待通知信号 |

---

## 🎯 实际案例（模拟）

**信号**: MOLT Token  
**评分**: 55 分 → ⏸️ 观望（低于 70）  
**结果**: 不交易

**如果评分 75 分：**
1. ✅ 通过风控
2. 💰 买入 0.5 SOL
3. 🚀 Jupiter Swap 执行
4. 📝 记录到历史
5. 📱 Telegram 通知

---

## 🛑 如何停止

```bash
# 停止监控
pkill -f meme_monitor_simple.py

# 查看当前运行状态
ps aux | grep meme_monitor

# 查看日志
tail -f /tmp/meme_monitor.log
```

---

## 📊 查看交易历史

```bash
cd /Users/qianzhao/.openclaw/workspace
cat trade_history.json
```

---

## ⚠️ 重要提示

1. **真金白银交易** - 这不是模拟，是真实链上交易
2. **风控已启用** - 单笔最多 1 SOL，每日最多 3 SOL
3. **自动运行** - 发现符合条件的信号会自动买入
4. **需要监控** - 建议每天检查交易记录
5. **止损重要** - 记得手动止损（或等我完善自动止损）

---

## 🔧 下一步优化（可选）

- [ ] 自动止损执行
- [ ] 自动止盈执行
- [ ] 持仓监控面板
- [ ] 更多数据源（Twitter、Discord）
- [ ] 回测系统
- [ ] Base 链交易支持

---

**生成时间**: 2026-02-03 14:53  
**维护者**: 紫龙 🐉
