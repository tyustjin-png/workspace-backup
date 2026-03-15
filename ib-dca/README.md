# CRCL 条件定投系统

根据价格阶梯策略自动买入 CRCL 股票。

## 策略说明

| 价格区间 | 买入金额 |
|----------|----------|
| $80 - $90 | $300 |
| $70 - $80 | $700 |
| < $70 | $1,500 |
| > $90 | 不买入 |

## 安装

```bash
cd /Users/qianzhao/.openclaw/workspace/ib-dca
pip install -r requirements.txt
```

## 配置

编辑 `config.yaml`：

```yaml
# IB Gateway 连接
ib:
  host: "127.0.0.1"
  port: 4001          # Live: 4001, Paper: 4002
  client_id: 1
  readonly: false     # 设为 true 禁止下单

# 阶梯策略（可自定义）
tiers:
  - price_max: 90.0
    price_min: 80.0
    amount: 300
  # ... 更多层级
```

## 使用

### 前置条件

1. IB Gateway 或 TWS 正在运行
2. 已登录 IB 账户
3. API 连接已启用（File → Global Configuration → API → Settings）

### 运行

```bash
# 正常执行
python crcl_dca.py

# 模拟运行（不实际下单）
python crcl_dca.py --dry-run

# 指定配置文件
python crcl_dca.py --config /path/to/config.yaml
```

### 定时执行

每天美股开盘后运行（北京时间 21:30 夏令时 / 22:30 冬令时）：

```bash
# 使用 cron (示例：每天北京时间 21:35 执行)
35 21 * * 1-5 cd /Users/qianzhao/.openclaw/workspace/ib-dca && python crcl_dca.py >> logs/cron.log 2>&1
```

或使用 OpenClaw cron：

```bash
openclaw cron add "35 21 * * 1-5" "cd /Users/qianzhao/.openclaw/workspace/ib-dca && python crcl_dca.py"
```

## 日志

日志文件位于 `logs/crcl_dca.log`，自动轮转（默认 10MB × 5 个备份）。

示例日志：
```
2024-03-14 21:35:00 | INFO     | ================================================
2024-03-14 21:35:00 | INFO     | CRCL 条件定投开始执行
2024-03-14 21:35:00 | INFO     | 时间: 2024-03-14 21:35:00
2024-03-14 21:35:00 | INFO     | 模式: LIVE (实盘)
2024-03-14 21:35:00 | INFO     | ================================================
2024-03-14 21:35:01 | INFO     | 正在连接 IB Gateway (127.0.0.1:4001)...
2024-03-14 21:35:02 | INFO     | ✓ IB Gateway 连接成功
2024-03-14 21:35:02 | INFO     | 正在获取 CRCL 实时价格...
2024-03-14 21:35:03 | INFO     | ✓ CRCL 当前价格: $75.50
2024-03-14 21:35:03 | INFO     | 价格 $75.50 在区间 ($70.00, $80.00]，买入金额: $700
2024-03-14 21:35:03 | INFO     | 买入金额 $700 / 价格 $75.50 = 9 股
2024-03-14 21:35:03 | INFO     | 正在下单: 买入 9 股 CRCL...
2024-03-14 21:35:05 | INFO     | ✓ 订单成交: 成交 9 股 @ $75.52
```

## 通知

交易完成后通过 `openclaw message` 发送通知。

配置选项：
```yaml
notification:
  enabled: true
  on_success: true    # 成功时通知
  on_failure: true    # 失败时通知
  on_skip: false      # 跳过时通知
```

## 安全提示

1. **先用模拟盘测试**：设置 `ib.port: 4002` 连接 Paper Trading
2. **使用 dry-run**：首次运行加 `--dry-run` 参数
3. **设置 readonly**：配置 `ib.readonly: true` 禁止下单
4. **检查日志**：确认价格和股数计算正确

## 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 连接失败 | IB Gateway 未运行 | 启动 IB Gateway 并登录 |
| 连接失败 | API 未启用 | TWS/Gateway → Configure → API → Enable |
| 无法获取价格 | 市场未开盘 | 等待开盘后执行 |
| 无法获取价格 | 无市场数据订阅 | 订阅 US Securities Snapshot |
| 下单失败 | 资金不足 | 检查账户余额 |

## 文件结构

```
ib-dca/
├── crcl_dca.py      # 主脚本
├── config.yaml      # 配置文件
├── requirements.txt # Python 依赖
├── README.md        # 本文档
└── logs/            # 日志目录（自动创建）
    └── crcl_dca.log
```
