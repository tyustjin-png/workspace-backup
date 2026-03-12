# 💰 小定 - 自动化定投助手

小定是一个专注于执行分区间定投策略的独立Agent。

## ✅ 当前状态

- ✅ Agent已创建
- ✅ 币安API已配置
- ✅ z值自动获取（看板：http://8.216.6.8/）
- ✅ **已开启自动定投**（每天08:00）

---

## 📊 定投配置

### 基础参数
- **基础份额**: 182.65 USDT
- **总预算**: 100,000 USDT
- **预期倍数**: 1.5x
- **投入周期**: 365天
- **交易对**: BTCUSDT
- **模式**: continuous（持续定投）

### 买入倍数（斐波那契）
| z值 | 市场状态 | 倍数 | 买入金额 |
|-----|---------|------|---------|
| 0 | 牛市高位 | 0x | 不买入 |
| 1 | 开始低估 | 1x | 182.65 USDT |
| 2 | 中等低估 | 2x | 365.30 USDT |
| 3 | 较低位置 | 3x | 547.95 USDT |
| 4 | 低位区间 | 5x | 913.24 USDT |
| 5 | 很低位置 | 8x | 1,461.19 USDT |
| 6 | 极端底部 | 13x | 2,374.43 USDT |

---

## 🤖 自动化流程

**每天 08:00**：
1. 自动从看板获取最新z值
2. 计算买入倍数和金额
3. 如果 z >= 1，执行币安买入
4. 记录交易到日志
5. 通知金哥

**通知方式**：
- 紫龙会在每天 08:05 检查小定的执行结果
- 自动汇报给金哥

---

## 📁 重要文件

- **配置**: `config/binance_auto_buy.json`
- **日志**: `data/dca_log.txt`
- **状态**: `data/binance_buy_state.json`
- **历史**: `data/binance_buy_history.jsonl`
- **通知**: `/tmp/xiaoding_notify.txt`

---

## 🛠️ 手动操作

### 查看状态
```bash
cd ~/.openclaw/workspace/xiaoding
python3 binance_auto_buy.py --status
```

### 查看日志
```bash
tail -50 ~/.openclaw/workspace/xiaoding/data/dca_log.txt
```

### 手动执行定投
```bash
cd ~/.openclaw/workspace/xiaoding
python3 binance_auto_buy.py
```

### 模拟运行（不实际买入）
```bash
cd ~/.openclaw/workspace/xiaoding
python3 binance_auto_buy.py --dry-run
```

---

## ⚙️ 修改配置

编辑配置文件：
```bash
nano ~/.openclaw/workspace/xiaoding/config/binance_auto_buy.json
```

修改后无需重启，下次定投时自动生效。

---

## 🔒 安全措施

- ✅ 币安API限制IP白名单（43.167.241.223）
- ✅ API仅开启现货交易权限
- ✅ 禁用提现功能
- ✅ 所有操作记录日志
- ✅ 异常情况自动通知

---

**小定的使命**：纪律执行，理性定投，避免人性弱点

🐉 紫龙会代替小定向你汇报定投情况
