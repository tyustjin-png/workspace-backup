# API密钥迁移 - 快速实施指南

## ⏱️ **总耗时：约30分钟**

---

## 🎯 **5步完成零明文迁移**

### Step 1: 安装1Password CLI（5分钟）

```bash
# macOS
brew install --cask 1password-cli

# 验证
op --version
```

✅ **检查点：** 能看到版本号

---

### Step 2: 1Password配置（10分钟）

**2.1 创建Agent Vault**
- 打开1Password App
- 点击 "+" → New Vault
- 名称：`Agent`

**2.2 创建Service Account**
- 登录 https://start.1password.com
- Developer → Service Account → Create
- Name: `openclaw-agent`
- Vault access: `Agent`（Read Items only）
- **重要：** 保存显示的Token

**2.3 保存Token到本地**
```bash
echo "你的Service Account Token" > ~/.openclaw/.op-token
chmod 600 ~/.openclaw/.op-token
```

✅ **检查点：**
```bash
OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.openclaw/.op-token) op vault list
# 能看到 Agent vault
```

---

### Step 3: 在Agent Vault中创建密钥（5分钟）

**在1Password中（手机App最快）：**

切换到 `Agent` vault，创建以下Item：

| Item名称 | Password值来源 |
|---------|---------------|
| `anthropic` | 从 openclaw.json 拷贝 |
| `brave` | 从 openclaw.json 拷贝 |
| `telegram-bot` | 从 openclaw.json 拷贝 |
| `gateway` | 从 openclaw.json 拷贝 |

**如何找到当前密钥：**
```bash
# 查看当前配置（不会显示在终端历史中）
openclaw config get models.providers.anthropic.apiKey
openclaw config get tools.web.search.apiKey
openclaw config get channels.telegram.botToken
openclaw config get gateway.auth.token
```

✅ **检查点：** Agent vault中有4个Item

---

### Step 4: 同步脚本（5分钟）

**4.1 创建同步脚本**
```bash
cat > ~/.openclaw/sync-secrets.sh << 'SCRIPT'
#!/bin/bash
export OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.openclaw/.op-token)

python3 -c "
import json, subprocess, os

def op_read(ref):
    try:
        result = subprocess.run(['op', 'read', ref],
            capture_output=True, text=True, timeout=10,
            env={**os.environ})
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

result = subprocess.run(
    ['op', 'item', 'list', '--vault', 'Agent', '--format=json'],
    capture_output=True, text=True, timeout=15, env={**os.environ})
items = json.loads(result.stdout) if result.returncode == 0 else []

secrets = {}
for item in items:
    title = item.get('title', '')
    val = op_read(f'op://Agent/{title}/password')
    if val:
        secrets[title] = val

with open(os.path.expanduser('~/.openclaw/secrets.json'), 'w') as f:
    json.dump(secrets, f, indent=2)
os.chmod(os.path.expanduser('~/.openclaw/secrets.json'), 0o600)
print(f'✅ Synced {len(secrets)} secrets')
"
SCRIPT

chmod +x ~/.openclaw/sync-secrets.sh
```

**4.2 首次同步**
```bash
~/.openclaw/sync-secrets.sh
# 输出：✅ Synced 4 secrets
```

**4.3 注册File Provider**
```bash
openclaw config set secrets.providers.op_file '{
  "source": "file",
  "path": "~/.openclaw/secrets.json",
  "mode": "json"
}'
```

✅ **检查点：**
```bash
ls -lh ~/.openclaw/secrets.json
# 应该看到文件，权限600
```

---

### Step 5: 迁移配置（5分钟）

**⚠️ 重要：先备份！**
```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup
```

**5.1 迁移Brave Search（先测试非关键）**
```bash
openclaw config set tools.web.search.apiKey '{
  "source": "file",
  "provider": "op_file",
  "id": "/brave"
}'

# 测试搜索
# 如果正常 = 配置成功
```

**5.2 迁移Anthropic API**
```bash
openclaw config set models.providers.anthropic.apiKey '{
  "source": "file",
  "provider": "op_file",
  "id": "/anthropic"
}'

# 测试对话
# 如果正常 = 配置成功
```

**5.3 迁移Telegram Bot（核心密钥）**
```bash
openclaw config set channels.telegram.botToken '{
  "source": "file",
  "provider": "op_file",
  "id": "/telegram-bot"
}'

# 给自己发条测试消息
# 如果收到 = 配置成功
```

**5.4 迁移Gateway Auth**
```bash
openclaw config set gateway.auth.token '{
  "source": "file",
  "provider": "op_file",
  "id": "/gateway"
}'

# 测试Gateway连接
openclaw gateway status
```

✅ **检查点：** 所有功能正常

---

## 🎉 **验证成功**

```bash
# 查看配置文件
cat ~/.openclaw/openclaw.json | grep -E "sk-|AAH|api.*:"

# 如果看不到明文密钥 = 迁移成功！✅
```

---

## 📋 **后续清理（可选）**

### 清理聊天记录中的历史密钥

如果之前在Telegram中发送过API Key：
1. 搜索包含 `sk-`、`AAH` 等关键词的消息
2. 逐条删除
3. 记住：Telegram删除不保证从所有备份中彻底删除

### 定期同步

**建议：** 每天早上同步一次（防止1P中更新了密钥但本地未同步）

**方式1：手动**
```bash
~/.openclaw/sync-secrets.sh
```

**方式2：添加到系统cron**
```bash
# 每天早上7:00自动同步
0 7 * * * /root/.openclaw/sync-secrets.sh >> /tmp/secrets-sync.log 2>&1
```

**方式3：添加到OpenClaw cron**
```bash
openclaw cron add \
  --name "同步1Password密钥" \
  --cron "0 7 * * *" \
  --session isolated \
  --message "运行密钥同步脚本：~/.openclaw/sync-secrets.sh，确保本地密钥与1Password保持同步" \
  --announce \
  --channel last
```

---

## 🆘 **故障排查**

### 问题1：sync脚本报错 "op: command not found"

**原因：** 1Password CLI未正确安装

**解决：**
```bash
which op
# 如果没有输出，重新安装
brew install --cask 1password-cli
```

### 问题2：同步后OpenClaw启动失败

**原因：** 某个密钥解析失败

**排查：**
```bash
# 查看详细错误
openclaw gateway start --verbose

# 检查secrets.json
cat ~/.openclaw/secrets.json
```

**解决：** 检查1P中对应Item的password字段是否填写正确

### 问题3：迁移后Telegram消息收不到

**原因：** botToken配置错误

**恢复：**
```bash
# 恢复备份
cp ~/.openclaw/openclaw.json.backup ~/.openclaw/openclaw.json

# 重启Gateway
openclaw gateway restart
```

---

## 📚 **相关文档**

- 完整指南：`infra/API_MANAGEMENT.md`
- 原文：https://blog.yuanming.ai/posts/openclaw-1password-secrets/

---

**创建时间：** 2026-03-09  
**预计耗时：** 30分钟  
**难度：** ⭐⭐☆☆☆（中低）
