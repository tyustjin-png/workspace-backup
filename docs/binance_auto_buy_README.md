# 币安自动买入 - 分区间定投策略

## 📖 策略说明

基于文章《分区间定投完整指南》的策略，使用多维度评分体系自动执行买入。

### 核心机制

1. **多维度评分**：均线、MVRV Z-Score、RHODL Ratio、已实现盈亏比、成本结构
2. **z 值范围**：0-6，代表市场从高位到低位
3. **定投倍数**：采用斐波那契数列 (0, 1, 2, 3, 5, 8, 13)

### z 值与买入倍数映射

| z 值 | 定投倍数 | 市场状态 |
|------|---------|----------|
| 0    | 0x      | 牛市/高位，不买入 |
| 1    | 1x      | 开始进入熊市低位 |
| 2    | 2x      | 中等低估区间 |
| 3    | 3x      | 较低位置 |
| 4    | 5x      | 低位区间 |
| 5    | 8x      | 很低位置 |
| 6    | 13x     | 极端底部 |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install requests
```

### 2. 配置文件

```bash
# 复制配置模板
cp ~/.openclaw/workspace/config/binance_auto_buy.json.example \
   ~/.openclaw/workspace/config/binance_auto_buy.json

# 编辑配置
vim ~/.openclaw/workspace/config/binance_auto_buy.json
```

### 3. 配置币安 API

1. 登录币安账户
2. 进入 API 管理：https://www.binance.com/zh-CN/my/settings/api-management
3. 创建新的 API Key
4. **权限设置**：只需启用 "现货交易" 权限
5. **IP 白名单**：建议设置服务器 IP（提高安全性）
6. 将 API Key 和 Secret 填入配置文件

### 4. 配置参数

```json
{
  "binance_api_key": "你的API_KEY",
  "binance_api_secret": "你的API_SECRET",
  
  "symbol": "BTCUSDT",          // 交易对
  "quote_asset": "USDT",         // 计价货币
  
  "mode": "fixed_budget",        // 模式：fixed_budget 或 continuous
  
  "total_budget": 100000,        // 总预算（美元）
  "expected_multiplier": 1.5,    // 期望倍数
  "cycle_days": 365,             // 周期天数
  
  "manual_z_value": 1            // 手动设置 z 值（临时）
}
```

**基础份额计算公式**：
```
base_amount = total_budget / (expected_multiplier × cycle_days)

例如：100,000 / (1.5 × 365) ≈ $182.65
```

## 📊 使用方法

### 查看状态

```bash
python3 ~/.openclaw/workspace/binance_auto_buy.py --status
```

### 模拟运行（测试）

```bash
python3 ~/.openclaw/workspace/binance_auto_buy.py --dry-run
```

### 实际买入

```bash
python3 ~/.openclaw/workspace/binance_auto_buy.py
```

## ⚙️ 两种模式

### 1. 固定预算模式 (fixed_budget)

- 设定总预算，投完就停
- 适合：有明确资金规划的用户
- 计算基础份额：`base_amount = total_budget / (expected_multiplier × cycle_days)`

### 2. 固定份额追加模式 (continuous)

- 使用固定基础份额，只要 z ≠ 0 就持续投入
- 适合：希望在低位买入更多筹码的用户
- 可能投入超过预算，但成本可控

## 🔧 获取 z 值的方法

### 方法1：手动设置（临时方案）

```json
{
  "manual_z_value": 1
}
```

每天根据看板 http://8.216.6.8/ 手动更新 z 值

### 方法2：API 自动获取（推荐）

如果看板提供 API，配置：

```json
{
  "z_api_url": "http://8.216.6.8/api/z_value"
}
```

### 方法3：自己计算（高级）

可以修改 `get_z_value()` 函数，集成多维度指标计算：
- 均线位置
- MVRV Z-Score
- RHODL Ratio
- 已实现盈亏比
- 成本结构

## 📁 数据文件

- **状态文件**：`~/.openclaw/workspace/data/binance_buy_state.json`
  - 记录总投入、总买入、上次 z 值等

- **历史记录**：`~/.openclaw/workspace/data/binance_buy_history.jsonl`
  - 每笔买入的详细记录

## ⏰ 定时任务

建议每天执行一次（或每周）：

```bash
# 编辑 crontab
crontab -e

# 每天早上 9:00 执行
0 9 * * * cd ~/.openclaw/workspace && python3 binance_auto_buy.py

# 或者每周一早上 9:00
0 9 * * 1 cd ~/.openclaw/workspace && python3 binance_auto_buy.py
```

## ⚠️ 安全建议

1. **API 权限**：只启用"现货交易"权限，禁用提现
2. **IP 白名单**：限制 API 只能从特定 IP 访问
3. **资金管理**：不要投入超过承受范围的资金
4. **测试先行**：先用 `--dry-run` 模拟运行
5. **备份配置**：妥善保管 API Key

## 📈 历史回测数据

根据文章回测（Cycle 2-4）：

- **熊市窗口**：一个周期约 17-20 个月可定投（占比 35-40%）
- **极端底部**：即使很短（如 Cycle 3 的 26 天），也能通过中等低估区间投出 55% 资金
- **收益对比**：相比等额定投提高约 20% 收益率

## 🛠️ 故障排查

### 问题1：无法下单

- 检查 API Key 权限
- 检查账户余额是否充足
- 检查交易对是否正确

### 问题2：API 签名错误

- 检查 API Secret 是否正确
- 检查服务器时间是否准确（`date`）

### 问题3：z 值获取失败

- 检查 `z_api_url` 是否可访问
- 或临时使用 `manual_z_value`

## 📚 参考资料

- 原文：《分区间定投完整指南》
- 看板：http://8.216.6.8/
- 币安 API 文档：https://binance-docs.github.io/apidocs/spot/cn/

---

**免责声明**：本工具仅供学习研究，投资有风险，使用需谨慎。
