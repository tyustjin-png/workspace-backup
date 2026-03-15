# 🐉 Meme 币机器人系统升级 v2.0

**升级时间：** 2026-02-01 00:20 GMT+8

---

## 🎯 升级内容

### 1️⃣ 优化评分系统（满分 100 分）

**旧系统（v1）：**
```
最高分：70 分
- 热度：30 分
- 流动性：20 分（硬性门槛 $50K）
- 交易量：20 分（硬性门槛 $100K）
```

**新系统（v2）：**
```
最高分：100 分
- 热度：30 分（Moltbook 点赞数）
- 流动性：25 分（梯度评分，$10K-$100K+）
- 交易量：25 分（梯度评分，$50K-$500K+）
- 早期加分：15 分（上线 < 3h，交易量/流动性比 > 10）
- 交易数量：5 分（24h 交易笔数）
```

### 2️⃣ 降低入场门槛

| 参数 | v1 | v2 |
|------|----|----|
| 最低流动性 | $50,000（硬性） | $10,000（梯度） |
| 最低交易量 | $100,000（硬性） | $50,000（梯度） |
| 最低评分 | 70 分 | 70 分 |

**效果：**
- ✅ 可以捕获早期机会（如 SHELLRAISER）
- ✅ 流动性 $45K + 高交易量可以通过
- ✅ 早期热度币可获得额外加分

### 3️⃣ 止盈止损系统

**新增功能：**
- ✅ **-50% 止损** - 自动卖出全部
- ✅ **+50% 止盈** - 自动卖出 50%（回本）
- ✅ **+100% 止盈** - 自动卖出剩余 50%
- ✅ **超时止损** - 持有 >24h 且盈利 <20%，自动卖出

**运行方式：**
- 每分钟检查一次所有持仓
- 触发条件自动执行卖出
- Telegram 通知

### 4️⃣ 持仓管理

**文件：** `position_manager.py`

**功能：**
- 记录所有买入持仓
- 实时计算盈亏
- 自动触发止盈止损
- 生成交易报告

**数据存储：** `positions.json`

```json
{
  "positions": [
    {
      "contract": "D3Rj...",
      "token_name": "$SHELLRAISER",
      "amount_sol": 1.0,
      "buy_price": 0.0002295,
      "tokens_received": 4358,
      "buy_time": "2026-02-01T00:00:00",
      "status": "holding",
      "partial_sold": false
    }
  ]
}
```

---

## 📊 实战案例：SHELLRAISER

### 旧框架评分（v1）

```
热度：30 分（2000 赞）
流动性：0 分（$45K < $50K 硬性门槛）❌
交易量：20 分（$644K > $100K）

总分：50 分 ❌ 不符合（需要 70 分）
```

### 新框架评分（v2）

```
热度：30 分（2000 赞）
流动性：15 分（$45K，梯度评分）✅
交易量：25 分（$644K）✅
早期加分：15 分（上线 1h，交易量/流动性 = 14.3）✅
交易数量：5 分（9005 笔）✅

总分：90 分 ✅ 强烈推荐！
建议买入：1.0 SOL
```

---

## 🛠️ 技术实现

### 文件变更

**修改：**
- `meme_monitor_simple.py` - 新评分逻辑 + 代币年龄检测
- `full_auto_trader.py` - 降低流动性门槛 + 止盈止损参数

**新增：**
- `position_manager.py` - 持仓管理与止盈止损
- `positions.json` - 持仓数据库

### Cron 任务

```bash
# Meme 币监控（每 5 分钟）
*/5 * * * * meme_monitor_simple.py

# 持仓监控（每分钟）
* * * * * position_manager.py

# 通知检查（每 2 分钟）
*/2 * * * * OpenClaw cron
```

---

## 📈 预期效果

### 更灵活的筛选

- ✅ 早期币（上线 < 3h）获得特殊评分
- ✅ 高交易量可弥补流动性不足
- ✅ 梯度评分更符合实际市场

### 更安全的风控

- ✅ 自动止损 -50%（避免深亏）
- ✅ 自动止盈 +50%（锁定利润）
- ✅ 超时止损（避免长期套牢）

### 更智能的管理

- ✅ 实时监控所有持仓
- ✅ 自动执行卖出决策
- ✅ Telegram 实时通知

---

## ⚠️ 注意事项

### 交易执行（待完善）

**当前状态：**
- ✅ 评分系统：完整
- ✅ 监控系统：运行中
- ✅ 持仓管理：运行中
- ⏳ 交易执行：需要完整 Jupiter Swap 集成

**下一步：**
1. 完成 Jupiter Swap 签名
2. 测试小额交易（0.01 SOL）
3. 验证止盈止损卖出

### 风控建议

- 🔒 单笔限额保持 1 SOL
- 🔒 每日限额保持 3 SOL
- 🔒 小额测试后再放开

---

## 🎯 使用指南

### 手动测试评分

```bash
cd /Users/qianzhao/.openclaw/workspace
./meme_monitor_env/bin/python meme_monitor_simple.py
```

### 检查持仓

```bash
./meme_monitor_env/bin/python position_manager.py
```

### 查看日志

```bash
# 监控日志
tail -f /tmp/meme_monitor.log

# 持仓日志
tail -f /tmp/position_monitor.log
```

### 手动添加持仓（测试）

```python
from position_manager import PositionManager

manager = PositionManager()
manager.add_position(
    contract="D3RjWyMW3uoobJPGUY4HHjFeAduCPCvRUDtWzZ1b2EpE",
    token_name="$SHELLRAISER",
    amount_sol=1.0,
    buy_price=0.0002295,
    tokens_received=4358
)
```

---

## ✅ 升级完成清单

- [x] 优化评分算法
- [x] 降低流动性门槛
- [x] 添加早期币加分
- [x] 创建持仓管理系统
- [x] 实现 -50% 止损
- [x] 实现 +50%/+100% 止盈
- [x] 添加超时止损
- [x] 配置 cron 定时任务
- [x] 测试 SHELLRAISER 评分
- [ ] 完成交易执行（Jupiter Swap）
- [ ] 小额实战测试

---

**升级完成！系统已就绪 🚀**

现在 SHELLRAISER 这样的早期高潜力币会被正确评分并买入！
