# API密钥管理机制

## 🎯 **核心目标**

**零明文密钥存储** - 所有API密钥通过1Password管理，配置文件只存储引用

---

## ⚠️ **当前风险评估**

### 明文密钥的4个泄露途径

| 途径 | 风险 | 示例 |
|------|------|------|
| **Telegram云端** | 🔴 高 | 在对话中发送API Key → 永久存储在云端 |
| **LLM上下文** | 🟡 中 | 密钥进入模型上下文 → 经过提供商服务器 |
| **本地日志** | 🟡 中 | 记录在 ~/.openclaw/logs/ 中 |
| **配置文件** | 🔴 高 | 明文存储在 openclaw.json 中 |

### 现有的明文密钥（需要迁移）

**模型提供商：**
- Anthropic API Key
- 其他模型提供商的密钥

**工具类：**
- Brave Search API Key
- Perplexity API Key
- Grok/Gemini/Kimi API Key（如果配置了）

**通信渠道：**
- Telegram Bot Token
- Gateway Auth Token

**其他：**
- 定投脚本可能用到的API密钥
- 邮件/日历集成的凭证

---

## ✅ **解决方案：OpenClaw SecretRef + 1Password**

### 工作原理

```
1Password Agent Vault（保险柜）
    ↓ (Service Account Token)
同步脚本（搬运工）
    ↓
~/.openclaw/secrets.json（本地缓存，600权限）
    ↓ (File Provider)
OpenClaw SecretRef（钥匙卡）
    ↓
应用读取密钥
```

### 迁移前后对比

**迁移前（openclaw.json）：**
```json
{
  "models": {
    "providers": {
      "anthropic": {
        "apiKey": "sk-ant-api03-xxx..."  ← 明文！
      }
    }
  },
  "channels": {
    "telegram": {
      "botToken": "123456:AAH..."  ← 明文！
    }
  }
}
```

**迁移后（openclaw.json）：**
```json
{
  "models": {
    "providers": {
      "anthropic": {
        "apiKey": {
          "source": "file",
          "provider": "op_file",
          "id": "/anthropic"  ← 引用！
        }
      }
    }
  },
  "channels": {
    "telegram": {
      "botToken": {
        "source": "file",
        "provider": "op_file",
        "id": "/telegram-bot"  ← 引用！
      }
    }
  }
}
```

---

## 🚀 **实施方案**

### 前置要求

**1. 1Password账户**
- 已有1Password账户（个人或家庭版）
- 可以创建Vault和Service Account

**2. 1Password CLI**
```bash
# macOS
brew install --cask 1password-cli

# 验证安装
op --version
```

---

### 步骤1：创建专属Vault

**在1Password中（手机或电脑App）：**
1. 点击左上角 "+" → New Vault
2. 名称：`Agent`（或 `OpenClaw`）
3. 用途：专门存储AI Agent的API密钥

**隔离原则：**
- 个人密码 → Personal Vault
- AI密钥 → Agent Vault
- 完全分离，互不干扰

---

### 步骤2：创建Service Account

**在网页端操作：**
1. 登录 [1password.com](https://start.1password.com)
2. 进入 Developer → Directory → Infrastructure Secrets Management
3. 点击 "Create a Service Account"
4. 配置：
   - Name: `openclaw-agent`
   - Create vaults: `No`（不需要创建权限）
   - Vault access: 选择 `Agent` vault，权限 `Read Items`（只读）
5. **重要！** 保存显示的 Service Account Token（只显示一次）

**保存Token：**
```bash
# 粘贴你的Service Account Token
echo "eyJhbGciOi...你的token..." > ~/.openclaw/.op-token

# 设置权限（只有你自己能读）
chmod 600 ~/.openclaw/.op-token
```

**验证：**
```bash
OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.openclaw/.op-token) op vault list
# 应该能看到 Agent vault
```

---

### 步骤3：在Agent Vault中创建密钥

**在1Password中（手机App最方便）：**

切换到 `Agent` vault，逐个创建：

| Item名称 | Password值 | 用途 |
|---------|-----------|------|
| `anthropic` | sk-ant-api03-xxx... | Anthropic API |
| `brave` | BSAxxxx... | Brave Search |
| `telegram-bot` | 123456:AAH... | Telegram Bot |
| `gateway` | xxx | Gateway Auth |
| `perplexity` | pplx-xxx | Perplexity搜索（如有） |
| `xiaoding-*` | xxx | 定投脚本密钥（如有） |

**命名规范：**
- 小写字母 + 中划线
- 语义化（看名字就知道是什么）
- 例如：`telegram-bot` 而不是 `bot1`

---

### 步骤4：创建同步脚本

**创建 `~/.openclaw/sync-secrets.sh`：**

```bash
#!/bin/bash
# 从1Password同步密钥到本地JSON

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

# 自动发现 Agent vault 中的所有 item
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
```

**设置权限：**
```bash
chmod +x ~/.openclaw/sync-secrets.sh
```

**首次同步：**
```bash
~/.openclaw/sync-secrets.sh
# 输出：✅ Synced 6 secrets
```

---

### 步骤5：注册File Provider

```bash
openclaw config set secrets.providers.op_file '{
  "source": "file",
  "path": "~/.openclaw/secrets.json",
  "mode": "json"
}'
```

---

### 步骤6：逐个迁移密钥

**策略：从非关键到关键，逐步验证**

#### 6.1 先迁Brave Search（非关键）

```bash
# 迁移配置
openclaw config set tools.web.search.apiKey '{
  "source": "file",
  "provider": "op_file",
  "id": "/brave"
}'

# 验证搜索功能
openclaw test search "test query"
```

#### 6.2 迁移模型提供商

```bash
# Anthropic
openclaw config set models.providers.anthropic.apiKey '{
  "source": "file",
  "provider": "op_file",
  "id": "/anthropic"
}'

# 验证模型调用
openclaw chat "测试一下"
```

#### 6.3 迁移Telegram Bot Token（核心）

⚠️ **重要：** 这是核心密钥，务必先备份！

```bash
# 备份当前配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup

# 迁移
openclaw config set channels.telegram.botToken '{
  "source": "file",
  "provider": "op_file",
  "id": "/telegram-bot"
}'

# 验证（发条测试消息给自己）
# 如果收到消息 = 成功
```

#### 6.4 迁移Gateway Auth Token

```bash
openclaw config set gateway.auth.token '{
  "source": "file",
  "provider": "op_file",
  "id": "/gateway"
}'

# 验证Gateway连接
openclaw gateway status
```

---

### 步骤7：验证零明文

```bash
# 检查配置文件
cat ~/.openclaw/openclaw.json | grep -i "sk-\|AAH\|api"

# 如果看不到明文密钥 = 成功 ✅
```

---

## 📋 **日常工作流**

### 新增API Key

**不再需要在终端或聊天中粘贴密钥！**

1. **手机上操作：**
   - 打开1Password → Agent vault
   - 新建Item → 填入密钥
   - 保存

2. **电脑上同步：**
   ```bash
   ~/.openclaw/sync-secrets.sh
   ```

3. **配置引用：**
   ```bash
   openclaw config set xxx.apiKey '{
     "source": "file",
     "provider": "op_file",
     "id": "/新密钥名"
   }'
   ```

### 更换API Key

1. 在1P中修改Item的password值
2. 运行同步脚本
3. OpenClaw自动热重载（无需重启）

### 新机器迁移

1. 拷贝 `openclaw.json`（全是引用，安全）
2. 拷贝 `.op-token`
3. 运行同步脚本
4. 完成！

---

## 🔒 **安全设计**

### OpenClaw的安全机制

| 机制 | 说明 |
|------|------|
| **Fail-fast启动** | 任何活跃密钥解析失败 → 拒绝启动 |
| **原子热重载** | 全部成功才切换，任何失败保持旧的 |
| **活跃表面过滤** | 只验证当前真正在用的密钥 |
| **自动Redact** | `openclaw config get` 显示 `__REDACTED__` |

### 文件权限

```bash
-rw------- (600) ~/.openclaw/.op-token        # Service Account Token
-rw------- (600) ~/.openclaw/secrets.json     # 同步的密钥缓存
-rwx------ (700) ~/.openclaw/sync-secrets.sh  # 同步脚本
```

---

## 🎯 **迁移检查清单**

### 迁移前

- [ ] 安装1Password CLI
- [ ] 创建Agent Vault
- [ ] 创建Service Account
- [ ] 保存Service Account Token到 `.op-token`
- [ ] 验证 `op vault list` 能正常工作

### 迁移中

- [ ] 在Agent Vault中创建所有密钥Item
- [ ] 创建并测试 `sync-secrets.sh`
- [ ] 注册File Provider
- [ ] 逐个迁移密钥（从非关键到关键）
- [ ] 每次迁移后验证功能

### 迁移后

- [ ] 验证 `openclaw.json` 中无明文密钥
- [ ] 测试所有功能正常
- [ ] 删除聊天记录中的历史密钥
- [ ] 删除本地日志中的敏感信息（可选）
- [ ] 备份配置文件

---

## ⚠️ **注意事项**

### 不适合迁移的密钥

以下密钥由系统自动管理，**不需要**也**不应该**手动迁移：

- OAuth刷新令牌（自动轮换）
- Matrix accessToken（自动生成）
- WhatsApp凭证文件（二进制）

### 环境变量（暂不处理）

`~/.zshrc` 中的环境变量（如 `ANTHROPIC_API_KEY`）供外部工具使用，需要用 `op run --` 包裹执行，改动面较大，后续再处理。

---

## 📚 **参考资料**

- [原文：还在把API Key发给你的龙虾么？](https://blog.yuanming.ai/posts/openclaw-1password-secrets/)
- [1Password CLI官方文档](https://developer.1password.com/docs/cli/)
- [OpenClaw SecretRef文档](https://docs.openclaw.ai)

---

**创建时间：** 2026-03-09  
**维护者：** 紫龙 🐉  
**状态：** 待实施
