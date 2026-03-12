# Obsidian + OpenClaw 整合方案

> **目标：** 让 Obsidian 通过 OpenClaw 调用云服务器的 Claude Max  
> **版本：** v1.0 | **日期：** 2026-02-15

---

## 🎯 核心需求

- ✅ Obsidian 需要 AI 辅助（整理笔记、写作、总结）
- ✅ 已有云服务器的 OpenClaw + Claude Max
- ✅ 工作电脑（MBP）保持轻量，不装大模型
- ✅ 复用现有订阅，零额外成本

---

## 🏗️ 架构图

```
MBP Obsidian
  ↓ Tailscale VPN
云服务器
  ├─ OpenClaw Gateway (:18789)
  └─ Claude Max (登录方式)
```

---

## 🔧 配置步骤

### 1️⃣ 安装 Obsidian 插件

**推荐插件（三选一）：**

**选项 A：Text Generator（推荐）**
- 功能全面，支持自定义 endpoint
- Settings → Community plugins → 搜索 "Text Generator"

**选项 B：Copilot**
- 类似 GitHub Copilot 体验
- Settings → Community plugins → 搜索 "Copilot"

**选项 C：Smart Connections**
- 侧重笔记关联和检索
- Settings → Community plugins → 搜索 "Smart Connections"

---

### 2️⃣ 配置插件参数

**打开插件设置，填入以下三个参数：**

```yaml
Provider: Custom (OpenAI-compatible)
API Base URL: http://[云服务器Tailscale IP]:18789/v1
API Key: fdefab2e7ed757595b49de9fd04625af275c0b05ccadd69f
Model: openclaw:main
```

**替换说明：**
- `[云服务器Tailscale IP]` → 你的云服务器 Tailscale 内网 IP（形如 `100.x.x.x`）
- 或使用 Tailscale 机器名（形如 `vm-xxx.tail-xxxx.ts.net`）

---

### 3️⃣ 测试连接

**在 Obsidian 里：**
1. 打开任意笔记
2. 选中一段文字
3. 右键 → 插件菜单 → "Generate"
4. 如果能生成内容，说明配置成功！

---

## 💡 使用场景

### 场景 1：整理笔记

```
选中凌乱的笔记 → 调用插件 → 提示词：
"帮我整理成结构化的 Markdown，分成要点和总结"
```

### 场景 2：扩写内容

```
写了个标题 → 调用插件 → 提示词：
"根据这个标题，帮我写一段 200 字的介绍"
```

### 场景 3：总结文档

```
选中长文 → 调用插件 → 提示词：
"提炼核心观点，3-5 条要点"
```

### 场景 4：问答式写作

```
在笔记里写问题 → 调用插件 → 自动回答
或者用聊天模式直接对话
```

---

## 🔗 与其他工具的关系

### VS Code（已有方案）
- MBP VS Code → SSH → Mac mini
- Mac mini 上已登录 Claude（本地）
- 保持现有配置，不需要改动

### Telegram（已配置）
- 直接通过 OpenClaw
- 与 Obsidian 共用同一个 Claude Max

### 优势
- 一个 Claude Max 订阅，三个入口
- Obsidian、Telegram 通过 OpenClaw（云端）
- VS Code 通过 Mac mini（本地）
- 成本 $20/月，全搞定

---

## ⚡ 工作流示例

```mermaid
sequenceDiagram
    participant U as 你（MBP）
    participant OB as Obsidian
    participant OC as OpenClaw
    participant CM as Claude Max
    
    U->>OB: 编辑笔记
    U->>OB: 选中文字，调用插件
    OB->>OC: HTTP 请求（Tailscale）
    OC->>CM: 转发到 Claude Max
    CM-->>OC: 生成内容
    OC-->>OB: 返回结果
    OB->>U: 插入笔记
```

---

## 📋 检查清单

**配置前：**
- [ ] 确认 MBP 已安装 Tailscale
- [ ] 确认能 ping 通云服务器（`ping [Tailscale IP]`）
- [ ] 确认 OpenClaw HTTP API 已启用（已完成 ✅）

**配置中：**
- [ ] 在 Obsidian 安装 AI 插件
- [ ] 填入 API Base URL、API Key、Model
- [ ] 测试生成内容

**配置后：**
- [ ] 保存插件设置
- [ ] 设置常用快捷键
- [ ] 收藏常用 prompts

---

## 🛠️ 故障排查

### 问题 1：插件连接失败

**检查：**
```bash
# 在 MBP 上测试
curl http://[云服务器IP]:18789/v1/chat/completions \
  -H 'Authorization: Bearer fdefab2e7ed757595b49de9fd04625af275c0b05ccadd69f' \
  -H 'Content-Type: application/json' \
  -d '{"model":"openclaw:main","messages":[{"role":"user","content":"hi"}]}'
```

**如果失败：**
- 检查 Tailscale 连接状态（`tailscale status`）
- 检查 OpenClaw 服务运行状态
- 检查防火墙设置

---

### 问题 2：返回错误或超时

**检查：**
- OpenClaw Gateway 日志（`openclaw logs`）
- Claude Max Proxy 是否保持登录
- 网络延迟是否过高

---

### 问题 3：生成内容质量差

**优化：**
- 写更清晰的 prompt
- 使用插件的 "System Prompt" 功能
- 调整 temperature 参数（如果插件支持）

---

## 💰 成本对比

| 方案 | 月费 | 说明 |
|------|------|------|
| **之前** | $20 + ? | Claude Max + Obsidian 单独订阅/API |
| **现在** | $20 | 复用 Claude Max，零额外成本 |
| **节省** | 可能 >$10/月 | 如果之前用 API 按量计费 |

---

## 📚 推荐 Prompts

**保存到 Obsidian 模板：**

```markdown
## AI 常用指令

### 整理笔记
帮我整理成结构化的 Markdown，包含：
- 核心观点（3-5 条）
- 详细说明
- 总结

### 扩写内容
根据以下标题/要点，写一段 [字数] 字的内容，风格：[正式/轻松/技术]

### 提炼要点
从以下内容中提取核心信息，用 3-5 条要点总结

### 翻译润色
将以下内容翻译成 [语言]，要求：
- 保持原意
- 符合目标语言习惯
- 专业术语准确

### 问答
Q: [你的问题]
请用简洁的语言回答，如需举例请说明
```

---

## 🎉 总结

**已实现：**
- ✅ Obsidian 通过 OpenClaw 调用 Claude Max
- ✅ 零额外成本，复用现有订阅
- ✅ MBP 保持轻量，无需本地大模型

**工作流：**
- Obsidian：整理笔记、写作 → 云端 OpenClaw
- VS Code：写代码 → Mac mini 本地 Claude
- Telegram：日常聊天 → 云端 OpenClaw

**一个订阅，三个入口，全搞定！** 🚀

---

**文档维护：** 金哥 + 紫龙 🐉  
**最后更新：** 2026-02-15
