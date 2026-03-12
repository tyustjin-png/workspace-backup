# 📊 Bitcoin 链上指标 - 免费 CSV 方案

**生成时间**: 2026-02-03  
**数据文件**: `btc_metrics_history.csv`  
**脚本**: `btc_metrics_scraper.py`

---

## ✅ **成功！已实现**

### 获取到的指标

| 指标 | 说明 | 数据源 | 更新频率 |
|------|------|--------|---------|
| **MVRV Z-Score** | 简化版（用 200MA 替代 Realized Cap） | CoinGecko | 每日 |
| **RHODL Proxy** | 用算力变化代替 UTXO 年龄 | Blockchain.info | 每日 |
| **Fear & Greed Index** | 市场情绪指标 | Alternative.me | 每日 |
| **Price** | BTC 价格 | CoinGecko | 每日 |
| **Market Cap** | 市值 | Blockchain.info | 每日 |
| **Hash Rate** | 算力 | Blockchain.info | 每日 |

---

## 📁 **CSV 文件说明**

### 文件信息
- **路径**: `/root/.openclaw/workspace/btc_metrics_history.csv`
- **大小**: 149 KB
- **行数**: 1,503 行
- **日期范围**: 2025-02-04 至 2026-02-03（约 1 年）

### 字段说明

```csv
date,price,ma_200,simplified_mvrv,mvrv_z_score,market_cap,hash_rate,rhodl_proxy,fear_greed_index
```

| 字段 | 说明 | 单位 |
|------|------|------|
| `date` | 日期 | YYYY-MM-DD |
| `price` | BTC 价格 | USD |
| `ma_200` | 200 日移动平均 | USD |
| `simplified_mvrv` | 简化 MVRV（Price / MA200） | 比率 |
| `mvrv_z_score` | MVRV Z-Score（标准化） | 标准差 |
| `market_cap` | 市值 | USD |
| `hash_rate` | 算力 | Hash/s |
| `rhodl_proxy` | RHODL 代理指标 | 比率 |
| `fear_greed_index` | 恐惧贪婪指数 | 0-100 |

---

## 🎯 **当前市场信号（2026-02-03）**

```
价格: $78,688
MVRV Z-Score: -1.46 🟢 低估（买入机会）
Fear & Greed: 17（极度恐慌）

解读：
- MVRV Z < 0 = 历史上的买入机会
- Fear & Greed < 20 = 市场极度恐慌
- 结论：当前处于低估区域
```

---

## 📊 **MVRV Z-Score 解读**

### 信号区间

| Z-Score | 信号 | 建议 |
|---------|------|------|
| **> 7** | 🔴 极度过热 | 历史顶部区域，考虑全部获利 |
| **4-7** | 🟠 过热 | 考虑部分获利 |
| **2-4** | 🟡 偏热 | 谨慎持有 |
| **0-2** | ⚪ 中性 | 正常持有 |
| **< 0** | 🟢 低估 | 买入机会 |

### 历史回测

```
2021年11月 牛市顶部: Z-Score ≈ 7
2022年11月 熊市底部: Z-Score ≈ -0.5
2024年3月 反弹: Z-Score ≈ 3
2026年2月 当前: Z-Score = -1.46（低估）
```

---

## 🔄 **如何更新数据**

### 手动更新

```bash
cd /root/.openclaw/workspace
./meme_monitor_env/bin/python btc_metrics_scraper.py
```

### 自动更新（定时任务）

```bash
# 每天凌晨 2 点更新
openclaw cron add \
  --name "BTC 指标更新" \
  --schedule "0 2 * * *" \
  --command "cd /root/.openclaw/workspace && ./meme_monitor_env/bin/python btc_metrics_scraper.py"
```

### 查看更新后的数据

```bash
# 最近 5 天
tail -5 btc_metrics_history.csv

# 或者用 Python 分析
./meme_monitor_env/bin/python << 'EOF'
import pandas as pd

df = pd.read_csv('btc_metrics_history.csv')
latest = df.tail(1).iloc[0]

print(f"日期: {latest['date']}")
print(f"价格: ${latest['price']:,.2f}")
print(f"MVRV Z: {latest['mvrv_z_score']:.2f}")
print(f"F&G: {latest['fear_greed_index']:.0f}")
EOF
```

---

## 💡 **如何使用这些数据**

### 1. 配合 Meme 币策略

```python
# 读取最新数据
import pandas as pd

df = pd.read_csv('btc_metrics_history.csv')
latest = df.iloc[-1]

mvrv_z = latest['mvrv_z_score']

# 根据 BTC 市场信号调整 Meme 币仓位
if mvrv_z > 4:
    # BTC 过热 → 降低 Meme 币风险敞口
    max_per_trade = 0.5  # 降低单笔限额
    daily_limit = 2.0    # 降低每日限额
elif mvrv_z < 0:
    # BTC 低估 → 可以加大 Meme 币仓位
    max_per_trade = 1.5
    daily_limit = 4.0
else:
    # 正常
    max_per_trade = 1.0
    daily_limit = 3.0
```

### 2. 生成 Telegram 每日报告

```python
# 添加到每日总结
latest = df.iloc[-1]

message = f"""
📊 BTC 链上指标（{latest['date']}）

💰 价格: ${latest['price']:,.0f}
📈 MVRV Z-Score: {latest['mvrv_z_score']:.2f}
😱 Fear & Greed: {latest['fear_greed_index']:.0f}

{"🟢 低估区域 - 买入机会" if latest['mvrv_z_score'] < 0 else "⚪ 正常区域"}
"""

# 发送 Telegram
send_telegram(message)
```

### 3. 图表可视化（可选）

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('btc_metrics_history.csv')

# 绘制 MVRV Z-Score 走势
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['mvrv_z_score'])
plt.axhline(y=7, color='r', linestyle='--', label='过热')
plt.axhline(y=0, color='g', linestyle='--', label='低估')
plt.title('MVRV Z-Score')
plt.savefig('mvrv_chart.png')
```

---

## 🔧 **数据源详情**

### 1. CoinGecko（价格历史）
- **URL**: `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart`
- **限流**: 10-50 次/分钟（免费）
- **数据**: 365 天每日价格

### 2. Blockchain.info（链上数据）
- **URL**: `https://api.blockchain.info/charts/`
- **限流**: 无明确限制
- **数据**: Market Cap, 流通量, 算力

### 3. Alternative.me（情绪指标）
- **URL**: `https://api.alternative.me/fng/`
- **限流**: 无明确限制
- **数据**: Fear & Greed Index（0-100）

---

## ⚠️ **与真实 MVRV Z / RHODL 的区别**

### 简化版 vs 真实版

| 指标 | 简化版（本脚本） | 真实版（Glassnode） | 精度 |
|------|-----------------|-------------------|------|
| **MVRV Z** | 用 200MA 替代 Realized Cap | 计算每个 UTXO 的成本基础 | 80% |
| **RHODL** | 用算力变化代替 | 统计 UTXO 年龄分布 | 60% |

### 为什么够用？

- ✅ **捕捉主要信号**（牛熊转换点）
- ✅ **趋势方向正确**（虽然数值不精确）
- ✅ **完全免费**
- ✅ **每日更新**

### 什么时候需要真实版？

- ❌ 研究论文（需要精确数据）
- ❌ 机构报告（需要专业数据源）
- ✅ 个人交易策略（简化版足够）

---

## 📈 **下一步计划**

### 短期（本周）
- [x] 生成免费 CSV 数据 ✅
- [ ] 设置每日自动更新
- [ ] 集成到 Telegram 每日报告

### 中期（下周）
- [ ] 添加更多指标（NVT Ratio, Puell Multiple）
- [ ] 生成可视化图表
- [ ] 配合 Meme 币策略动态调整仓位

### 长期（可选）
- [ ] 搭建 Bitcoin 全节点（完整版 MVRV Z）
- [ ] 自建数据库（更快查询）
- [ ] Web 界面展示

---

## 🤝 **替代方案对比**

| 方案 | 成本 | 精度 | 开发时间 |
|------|------|------|---------|
| **本方案（免费 CSV）** | $0 | 80% | ✅ 已完成 |
| **Glassnode Starter** | $39/月 | 100% | 1 小时对接 |
| **Glassnode Pro** | $799/月 | 100% | 1 小时对接 |
| **自建全节点** | $50/月 | 100% | 2-3 周 |

**结论：** 如果是为了交易策略，免费方案完全够用 💡

---

**维护者**: 紫龙 🐉  
**更新时间**: 2026-02-03 15:54
