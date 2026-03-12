# 🔗 Base 链自动交易系统设置指南

**创建时间：** 2026-02-01 15:58 GMT+8

---

## 🎯 系统概述

已完成 **多链自动交易系统**，同时支持：
- ✅ Solana（Jupiter Swap）
- ✅ Base（Uniswap V3 / 1inch）

---

## 📦 已完成的工作

### 1️⃣ Base 交易模块

**文件：** `base_trader.py`

**功能：**
- ✅ EVM 钱包管理
- ✅ ETH 余额查询
- ✅ 代币余额查询
- ✅ 1inch API 集成（报价）
- ⏳ Uniswap V3 交易（待完成）

### 2️⃣ 多链监控系统

**文件：** `meme_monitor_simple.py`（已更新）

**功能：**
- ✅ 同时识别 Solana 地址（32-44 字符）
- ✅ 同时识别 EVM 地址（0x + 40 hex）
- ✅ 自动标记链类型
- ✅ DexScreener 多链数据获取
- ✅ 统一评分系统

### 3️⃣ 多链交易管理器

**文件：** `multichain_trader.py`

**功能：**
- ✅ 统一管理 Solana + Base 交易
- ✅ 独立的每日限额（Solana 3 SOL, Base 0.3 ETH）
- ✅ 自动选择交易器
- ✅ 交易记录统一管理

---

## 🔐 钱包配置（重要！）

### 方式 1：导入已有钱包（推荐）

```bash
cd /root/.openclaw/workspace

# 导入你的 Base 钱包私钥
./meme_monitor_env/bin/python << 'EOF'
from base_trader import import_wallet

private_key = "YOUR_PRIVATE_KEY_HERE"  # 替换为你的私钥
import_wallet(private_key)
EOF
```

**私钥格式：**
- 带 0x：`0x1234567890abcdef...`
- 不带 0x：`1234567890abcdef...`（自动添加）

### 方式 2：创建新钱包

```bash
cd /root/.openclaw/workspace
./meme_monitor_env/bin/python -c "from base_trader import create_wallet; create_wallet()"
```

**输出：**
```
✅ Base 钱包已创建
📍 地址: 0x1234...
🔐 私钥已保存到: ~/.config/base/trading-bot-key.json

⚠️  请向该地址充值 ETH（用于交易和 Gas）
```

---

## 💰 充值 ETH

**钱包地址查看：**
```bash
cat ~/.config/base/trading-bot-key.json
```

**建议充值：**
- 最少：0.05 ETH（可交易 + Gas）
- 推荐：0.1-0.2 ETH

**Base 链 Gas 费：**
- 一般交易：~$0.01-0.05
- 复杂交易：~$0.05-0.10

---

## ⚙️ 系统配置

### 风控参数

**文件：** `multichain_trader.py`

```python
# Solana
MAX_PER_TRADE_SOL = 1.0   # 单笔最多 1 SOL
DAILY_LIMIT_SOL = 3.0     # 每日最多 3 SOL

# Base
MAX_PER_TRADE_ETH = 0.1   # 单笔最多 0.1 ETH
DAILY_LIMIT_ETH = 0.3     # 每日最多 0.3 ETH
```

### 买入金额计算

| 评分 | Solana | Base |
|------|--------|------|
| 85+ | 1.0 SOL | 0.1 ETH |
| 75-84 | 0.5 SOL | 0.05 ETH |
| 70-74 | 0.2 SOL | 0.02 ETH |

---

## 🔧 测试系统

### 1. 检查钱包

```bash
cd /root/.openclaw/workspace
./meme_monitor_env/bin/python base_trader.py
```

**输出：**
```
🐉 Base 链交易系统

钱包地址: 0x1234...
ETH 余额: 0.1000
```

### 2. 测试监控

```bash
cd /root/.openclaw/workspace
./meme_monitor_env/bin/python meme_monitor_simple.py
```

**检查输出：**
- ✅ 发现 Solana 地址
- ✅ 发现 Base(EVM) 地址
- ✅ 正确标记链类型

### 3. 测试多链交易

```bash
./meme_monitor_env/bin/python multichain_trader.py
```

---

## 📊 监控输出示例

**发现 Base 链机会时：**

```
✅ 扫描完成，发现 1 个新机会
  - 0x1234... [BASE] 评分: 85

通知内容：
🆕 发现新机会！
🔗 链：Base
💎 代币：$BASED
📝 合约：0x1234...
📊 评分：85 分
💰 流动性：$120,000
📈 24h交易量：$350,000
```

---

## 🚀 运行流程

### 自动化流程（已配置）

```
1. Moltbook 热帖监控（每 5 分钟）
   ↓
2. 提取 Solana + Base 地址
   ↓
3. DexScreener 数据获取
   ↓
4. AI 评分（通用算法）
   ↓
5. 评分 ≥ 70 分？
   ↓
6. 检查链类型
   ↓
   ├─ Solana → Jupiter Swap
   └─ Base → Uniswap V3 / 1inch
   ↓
7. 执行交易
   ↓
8. 持仓管理
   ↓
9. 止盈止损
```

---

## 📁 文件结构

```
meme_monitor_simple.py      - 多链监控
base_trader.py              - Base 交易模块
multichain_trader.py        - 多链管理器
full_auto_trader.py         - Solana 交易（原有）
position_manager.py         - 持仓管理（需更新）

~/.config/solana/trading-bot.json  - Solana 钱包
~/.config/base/trading-bot-key.json  - Base 钱包

multichain_trade_history.json  - 多链交易记录
```

---

## ⚠️ 重要注意事项

### 1. 钱包安全

- 🔐 私钥文件权限：600（仅所有者可读）
- ❌ 不要泄露私钥
- ✅ 建议加密存储（可选）

### 2. 资金管理

**分散风险：**
- Solana：4 SOL（已充值）
- Base：0.1-0.2 ETH（待充值）

**总投入控制：**
- 每日最多 3 SOL + 0.3 ETH
- 约等于 $15-20（按当前价格）

### 3. Gas 费预留

**Base 链：**
- 交易 Gas：~0.0001-0.0005 ETH/次
- 建议预留：0.01 ETH（够 20-100 次交易）

### 4. DEX 选择

**Base 链 DEX：**
1. Uniswap V3（主流）
2. Aerodrome（Base 原生）
3. 1inch（聚合器，推荐）

**当前实现：**
- ✅ 1inch API 报价
- ⏳ Uniswap V3 交易执行（待完成）

---

## 🔨 待完成工作

### 高优先级

1. **完成 Uniswap V3 交易**
   - 交易路由
   - 交易签名
   - Gas 估算
   - 发送到链上

2. **更新持仓管理**
   - 支持 Base 链持仓
   - 查询 ERC20 余额
   - 计算 ETH 盈亏

3. **测试流程**
   - 小额测试（0.01 ETH）
   - 验证完整流程
   - 错误处理

### 中优先级

4. **优化 DEX 集成**
   - 1inch Swap API 完整集成
   - Aerodrome 支持
   - 自动选择最优路由

5. **多链通知**
   - Telegram 通知区分链
   - 交易成功/失败提示
   - 持仓状态更新

---

## 📝 下一步操作

**你需要做：**

1. **准备 Base 钱包私钥** ✅
   - 已有钱包：准备私钥
   - 新钱包：系统可自动创建

2. **导入钱包**
   ```bash
   # 使用上面的导入命令
   ```

3. **充值 ETH**
   - 向钱包地址充值 0.1-0.2 ETH

**我继续做：**

1. ⏳ 完成 Uniswap V3 交易集成
2. ⏳ 更新持仓管理器
3. ⏳ 测试完整流程

---

## ✅ 系统状态

| 模块 | Solana | Base |
|------|--------|------|
| 监控 | ✅ | ✅ |
| 评分 | ✅ | ✅ |
| 钱包 | ✅ | ⏳ 待导入 |
| 交易执行 | ⏳ | ⏳ |
| 持仓管理 | ✅ | ⏳ |
| 止盈止损 | ✅ | ⏳ |

---

## 🎯 预期效果

**多链监控优势：**
- ✅ 机会更多（Solana + Base）
- ✅ 风险分散（不同生态）
- ✅ 灵活配置（独立限额）

**示例场景：**
```
同时发现：
- Solana: $PEPE (90 分) → 买入 1 SOL
- Base: $BASED (85 分) → 买入 0.1 ETH

分散投资，降低单链风险
```

---

**准备好你的 Base 钱包私钥后告诉我，我立即帮你配置！** 🐉🔗
