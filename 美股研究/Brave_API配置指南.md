# Brave Search API 配置指南

## 步骤1：获取 API Key

1. 访问: https://brave.com/search/api/
2. 注册账号（免费）
3. 选择 **Data for Search** 套餐（**不是** Data for AI）
4. 生成 API 密钥

**免费额度**: 2,000 次/月

---

## 步骤2：配置到 OpenClaw

### 方法A：配置文件（推荐）

编辑 `~/.openclaw/openclaw.json`，添加：

```json
{
  ...
  "tools": {
    "web": {
      "search": {
        "provider": "brave",
        "apiKey": "你的_BRAVE_API_KEY",
        "maxResults": 5,
        "timeoutSeconds": 30
      }
    }
  },
  ...
}
```

### 方法B：环境变量

```bash
# 临时设置（当前会话）
export BRAVE_API_KEY="你的_BRAVE_API_KEY"

# 永久设置（推荐）
echo 'export BRAVE_API_KEY="你的_BRAVE_API_KEY"' >> ~/.bashrc
source ~/.bashrc
```

---

## 步骤3：验证

重启 OpenClaw Gateway：
```bash
pkill -f openclaw-gateway
sleep 2
nohup openclaw gateway start > /dev/null 2>&1 &
```

测试 web_search 是否可用（我会帮你测试）

---

## ⚠️ 注意事项

- ❌ **不要选择** "Data for AI" 套餐（与 web_search 不兼容）
- ✅ **必须选择** "Data for Search" 套餐
- 📊 免费额度：2,000 次/月（足够日常使用）

---

**获取 API Key 后告诉我，我来帮你配置！** 🐉
