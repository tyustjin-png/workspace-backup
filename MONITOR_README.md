# 🐉 紫龙 Meme 币监控系统

## ✅ 安装完成！

系统已经自动安装并配置好了。

---

## 📁 文件说明

- `meme_monitor_mvp.py` - 主程序
- `meme_monitor_env/` - Python 虚拟环境
- `start_monitor.sh` - 启动脚本

---

## 🚀 使用方法

### 1. 立即测试运行（前台）

```bash
cd /Users/qianzhao/.openclaw/workspace
./start_monitor.sh
```

**说明：** 程序会每 5 分钟扫描一次，在控制台显示结果。
按 `Ctrl+C` 可以停止。

---

### 2. 后台运行（推荐）

```bash
cd /Users/qianzhao/.openclaw/workspace
nohup ./start_monitor.sh > monitor.log 2>&1 &
```

查看日志：
```bash
tail -f /Users/qianzhao/.openclaw/workspace/monitor.log
```

停止监控：
```bash
pkill -f meme_monitor_mvp
```

---

### 3. 使用 systemd（开机自启）

创建服务文件：
```bash
sudo tee /etc/systemd/system/meme-monitor.service << 'EOF'
[Unit]
Description=Meme Coin Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/Users/qianzhao/.openclaw/workspace
ExecStart=/Users/qianzhao/.openclaw/workspace/start_monitor.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable meme-monitor
sudo systemctl start meme-monitor
```

查看状态：
```bash
sudo systemctl status meme-monitor
```

查看日志：
```bash
sudo journalctl -u meme-monitor -f
```

---

## ⚙️ 配置 Telegram 通知（可选）

编辑 `meme_monitor_mvp.py`，修改这两行：

```python
TELEGRAM_BOT_TOKEN = "你的 Bot Token"  # 从 @BotFather 获取
TELEGRAM_CHAT_ID = "你的 Chat ID"      # 从 @userinfobot 获取
```

**获取步骤：**

1. **创建 Telegram Bot**
   - 在 Telegram 搜索 @BotFather
   - 发送 /newbot
   - 按提示创建，获得 Token

2. **获取 Chat ID**
   - 在 Telegram 搜索 @userinfobot
   - 发送 /start
   - 获得你的 Chat ID（数字）

3. **重启监控**
   ```bash
   pkill -f meme_monitor_mvp
   ./start_monitor.sh
   ```

---

## 📊 监控内容

系统会自动：
- ✅ 每 5 分钟扫描 Moltbook 新帖子
- ✅ 提取 Solana 合约地址
- ✅ 从 DEXScreener 获取代币数据
- ✅ 评分（0-100）
- ✅ 发送通知（评分 ≥ 50）

---

## 🎯 通知示例

```
🚨 发现新代币机会！

📝 信息
合约: D3RjWyMW3uoobJPGUY4HHjFeAduCPCvRUDtWzZ1b2EpE
帖子: The One True Currency: $SHELLRAISER...
作者: Shellraiser

📊 Moltbook 数据
点赞: 88289
评论: 23

💰 链上数据
价格: $0.002971
流动性: $173,000
交易量(24h): $5,200,000
市值: $2,900,000
年龄: 3.1 小时

🎯 分析
评分: 75/100
推荐: 🔥 强烈推荐
风险: 暂无
```

---

## 🛠️ 故障排查

### 问题：API 超时
```bash
# 检查网络
curl -s https://www.moltbook.com/api/v1/posts?limit=1
```

### 问题：Python 模块错误
```bash
# 重新安装依赖
cd /Users/qianzhao/.openclaw/workspace
./meme_monitor_env/bin/pip install --upgrade requests
```

### 问题：监控不运行
```bash
# 检查进程
ps aux | grep meme_monitor

# 查看错误
tail -100 monitor.log
```

---

## 📈 下一步

### 立即可用：
- [x] Moltbook 监控
- [x] 代币数据获取
- [x] 热度评分
- [x] 控制台/Telegram 通知

### 未来功能（需要进一步开发）：
- [ ] Pump.fun 实时监控
- [ ] 聪明钱地址追踪
- [ ] 自动交易
- [ ] 止盈止损

---

**需要帮助？** 直接问紫龙 🐉
