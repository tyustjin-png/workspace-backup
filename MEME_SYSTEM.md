# 🐉 Meme 币自动监控系统

## ✅ 阶段 1 完成（监控+通知）

### 已部署组件

#### 1. 钱包
- **路径：** `~/.config/solana/trading-bot.json`
- **地址：** `7tLcKDnqBwvs3ZSz99qU6PcWYqhq73N3tsCfv96kQvyB`
- **状态：** ✅ 已恢复（从 /home/memebot 备份）
- **余额：** 4.0 SOL ✅

#### 2. 监控脚本
- **文件：** `meme_monitor_simple.py`
- **功能：**
  - 每 5 分钟扫描 Moltbook 热门帖子
  - 提取 Solana 合约地址
  - 获取 DexScreener 代币数据
  - AI 评分（流动性+交易量+热度）
  - 发现新机会时写入通知文件

#### 3. Cron 定时任务
- **系统 crontab：** 每 5 分钟运行监控
- **OpenClaw cron：** 每 2 分钟检查通知文件

#### 4. 通知流程
```
监控脚本发现新币
    ↓
写入 /tmp/meme_notify_pending.json
    ↓
OpenClaw cron 检查文件
    ↓
发送 Telegram 通知
    ↓
删除通知文件
```

---

## 📊 当前状态

| 功能 | 状态 | 备注 |
|------|------|------|
| Moltbook 监控 | ✅ | 每 5 分钟 |
| 信号评分 | ✅ | 简化版 AI |
| Telegram 通知 | ✅ | 测试通过 |
| 钱包创建 | ✅ | 需充值 |
| 自动交易 | ⏳ | 待实现 |
| 持仓监控 | ⏳ | 待实现 |
| 止盈止损 | ⏳ | 待实现 |

---

## 🔧 测试

### 手动触发监控
```bash
cd /Users/qianzhao/.openclaw/workspace
./meme_monitor_env/bin/python meme_monitor_simple.py
```

### 查看日志
```bash
tail -f /tmp/meme_monitor.log
```

### 测试通知
创建文件 `/tmp/meme_notify_pending.json`，等待 OpenClaw 检查（每 2 分钟）

---

## 📈 下一步

### 阶段 2：交易执行
1. 完整实现 Jupiter Swap 交易
2. 测试小额交易（0.01 SOL）
3. 添加风控检查

### 阶段 3：持仓管理
1. 创建持仓数据库
2. 定时监控价格
3. 实现止盈止损

---

## ⚠️ 重要提示

1. ~~**充值钱包**~~ - ✅ 已充值 4 SOL
2. **测试模式** - 目前只监控+通知，不会自动交易
3. **API 密钥** - Moltbook API 已配置
4. **日志** - 所有运行记录在 `/tmp/meme_monitor.log`

---

Created: 2026-01-31 23:34 GMT+8
