# 🚀 半自动交易系统使用指南

## 📋 系统流程

```
1. 监控系统发现机会
   ↓
2. 发送 Telegram 通知给你
   ↓
3. 你回复 "买" 或 "购买"
   ↓
4. 系统自动执行交易
   ↓
5. 发送交易结果
```

---

## ⚙️ 设置步骤

### 1. 安装 Solana CLI 并创建钱包

```bash
cd /root/.openclaw/workspace
chmod +x setup_wallet.sh
./setup_wallet.sh
```

**会输出你的钱包地址，类似：**
```
📍 你的钱包地址:
7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
```

**重要：** 记下这个地址，充值 SOL！

---

### 2. 充值钱包

**推荐金额：** 0.5 - 1 SOL

**充值方式：**
- 从交易所提现到钱包地址
- 或从你的主钱包转账

**验证余额：**
```bash
solana balance
```

---

### 3. 安装交易依赖

```bash
cd /root/.openclaw/workspace
./meme_monitor_env/bin/pip install solana solders base58
```

---

### 4. 测试系统

```bash
./meme_monitor_env/bin/python auto_trader.py
```

**应该看到：**
```
🐉 紫龙自动交易系统
钱包地址: 7xKXtg2...
SOL 余额: 0.5000
✅ 报价获取成功
```

---

## 🎮 使用方法

### 场景 1：发现新机会

你会收到类似这样的通知：

```
🚨 发现新代币机会！

📝 信息
合约: D3RjWyMW3uoob...
帖子: The One True Currency
作者: Shellraiser

💰 链上数据
流动性: $173,000
交易量: $5,200,000

🎯 分析
评分: 75/100
推荐: 🔥 强烈推荐

💵 建议买入金额: 0.2 SOL

---
回复 "买" 或 "购买" 确认交易
回复 "跳过" 忽略
```

### 场景 2：你的回复

**回复 "买" 或 "购买"：**
```
买
```

**我会自动：**
1. 验证钱包余额
2. 获取最新报价
3. 执行交易
4. 发送交易结果

### 场景 3：交易结果

```
✅ 交易成功！

合约: D3RjWyMW3uoob...
买入金额: 0.2 SOL
获得代币: 67,340 个
交易签名: 4Kx9s2...

🔗 查看交易
https://solscan.io/tx/4Kx9s2...
```

---

## 🛡️ 安全设置

### 单笔限额

编辑 `auto_trader.py`，修改：

```python
MAX_PER_TRADE = 0.5  # 单笔最多 0.5 SOL
```

### 每日限额

```python
DAILY_LIMIT = 2.0  # 每天最多 2 SOL
```

### 黑名单代币

```python
BLACKLIST = [
    "RugPullTokenAddress123...",
    "ScamTokenAddress456..."
]
```

---

## 📊 查看交易历史

```bash
cd /root/.openclaw/workspace
cat pending_trades.json
```

---

## 🔧 高级功能

### 止盈止损（未来版本）

```python
# 自动设置止盈
trader.set_take_profit(contract, multiplier=2.0)  # 2x 止盈

# 自动设置止损
trader.set_stop_loss(contract, multiplier=0.5)    # -50% 止损
```

### 批量买入

```
回复: 买 0.5
```
意思是买入 0.5 SOL（而不是建议金额）

---

## ⚠️ 重要注意事项

### 1. **资金安全**
- 专用钱包，不要放太多钱
- 建议初始 0.5-1 SOL
- 盈利后定期提现

### 2. **交易风险**
- Meme 币波动大，可能归零
- 建议单笔不超过 0.2 SOL
- 只用你能承受损失的资金

### 3. **滑点设置**
- 当前默认 5%
- 流动性低的币可能需要更高滑点
- 可以在代码中调整

### 4. **Gas 费**
- 每笔交易约 0.0001-0.001 SOL
- 钱包需要预留 Gas 费

---

## 🐛 故障排查

### 问题：交易失败

**检查：**
```bash
# 1. 余额是否足够
solana balance

# 2. RPC 是否正常
curl https://api.mainnet-beta.solana.com -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}'

# 3. 代币流动性
# 访问 https://dexscreener.com/solana/{合约地址}
```

### 问题：报价获取失败

可能原因：
- 代币太新（刚创建）
- 流动性太低
- Jupiter 不支持

**解决：** 等待几分钟后重试

---

## 📈 性能监控

### 查看交易记录

```bash
./meme_monitor_env/bin/python -c "
import json
with open('pending_trades.json') as f:
    data = json.load(f)
    print(f'总交易数: {len(data[\"history\"])}')
    
    success = [t for t in data['history'] if t['status'] == 'executed']
    print(f'成功: {len(success)}')
    
    for t in data['history'][-5:]:
        print(f'{t[\"timestamp\"][:16]} {t[\"token_name\"]} {t[\"status\"]}')
"
```

---

## 🚀 下一步改进

- [ ] 完整的交易签名实现
- [ ] 止盈止损自动化
- [ ] 多钱包管理
- [ ] 盈亏统计面板
- [ ] 回测系统

---

**有问题随时问紫龙！** 🐉
