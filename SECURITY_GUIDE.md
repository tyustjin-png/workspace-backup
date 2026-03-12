# 🛡️ 安全加固指南

## 最高优先级（立即执行）

### 1. 私钥加密存储
```bash
# 安装加密工具
sudo apt install age

# 加密私钥
age --encrypt --passphrase -o ~/.config/solana/trading-bot.json.age ~/.config/solana/trading-bot.json

# 删除明文私钥
shred -u ~/.config/solana/trading-bot.json

# 修改代码在启动时解密
```

### 2. 关闭腾讯云快照
```
1. 登录腾讯云控制台
2. 云硬盘 → 快照策略 → 禁用所有策略
3. 快照列表 → 删除所有现有快照
```

### 3. 限制 SSH 访问
```bash
# 只允许你的 IP
sudo ufw allow from YOUR_IP to any port 22
sudo ufw enable

# 禁用密码登录
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### 4. 使用独立用户运行
```bash
# 创建专用用户
sudo useradd -m -s /bin/bash memebot

# 转移文件
sudo cp -r /root/.openclaw/workspace /home/memebot/
sudo chown -R memebot:memebot /home/memebot/workspace

# 以 memebot 用户运行
sudo su - memebot
cd /home/memebot/workspace
./start_monitor.sh
```

---

## 中等优先级（本周完成）

### 5. 资金隔离
```
不要在交易钱包存放超过每日限额的资金
每天自动提现利润到冷钱包
```

### 6. 监控告警
```bash
# 设置余额告警
# 如果余额异常变动，立即通知你
```

### 7. 定期审计
```bash
# 每周检查交易记录
# 每月检查服务器安全
# 每季度更新依赖包
```

---

## 低优先级（有空再做）

### 8. 硬件钱包集成
```
使用 Ledger/Trezor 硬件钱包
私钥永不离开硬件设备
```

### 9. 多签钱包
```
需要 2/3 签名才能交易
即使服务器被黑也无法盗币
```

### 10. 冷热钱包分离
```
热钱包（服务器）：只放少量资金
冷钱包（离线）：存放大部分资产
```

---

## 检查清单

- [ ] 私钥已加密
- [ ] 腾讯云快照已关闭
- [ ] SSH 访问已限制
- [ ] 使用独立用户运行
- [ ] 资金控制在 5 SOL 以内
- [ ] 每日检查交易记录
- [ ] 定期转移利润

---

## 紧急响应

### 如果发现异常：

1. **立即停止监控**
```bash
pkill -f meme_monitor
```

2. **转移资金**
```bash
# 用 Phantom 紧急转走所有 SOL
```

3. **更换钱包**
```bash
# 生成新钱包
# 更新系统配置
```

4. **审查日志**
```bash
# 查找异常操作
sudo journalctl -u meme-monitor | grep -i "error\|fail"
```

---

## 风险评级

| 风险 | 等级 | 缓解后 |
|------|------|--------|
| 私钥泄露 | 🔴 严重 | 🟡 中等 |
| 腾讯云备份 | 🔴 严重 | 🟢 低 |
| SSH 入侵 | 🟠 高 | 🟢 低 |
| 依赖包后门 | 🟡 中等 | 🟡 中等 |
| 网络拦截 | 🟡 中等 | 🟢 低 |

---

**记住：完美的安全不存在，但分层防御可以大幅降低风险！**
