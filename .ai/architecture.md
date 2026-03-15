# 系统架构设计

## 📐 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Telegram   │  │  AI Agent    │  │   Cron Jobs  │  │
│  │   Channel    │  │  (Claude)    │  │   Scheduler  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
└─────────┼──────────────────┼──────────────────┼──────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                    核心服务层                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Meme Monitor │  │   Position   │  │   Memory     │  │
│  │   (Python)   │  │   Manager    │  │   Monitor    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
└─────────┼──────────────────┼──────────────────┼──────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                    数据层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  DexScreener │  │  Positions   │  │   Memory     │  │
│  │     API      │  │   JSON       │  │   Files      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 🔄 工作流程

### Meme 币监控流程

```
1. Cron 每 30 分钟触发
2. meme_monitor_simple.py 运行
3. 调用 DexScreener API 获取新币数据
4. 评分筛选（流动性、价格、持有人等）
5. 发现高分币 → 写入 /tmp/meme_notify_pending.json
6. AI 读取通知文件 → 发送 Telegram 消息
7. 删除通知文件
```

### 持仓监控流程

```
1. Cron 每 30 分钟触发
2. position_manager.py 运行
3. 读取 positions.json
4. 对每个持仓：
   - 获取当前价格
   - 计算盈亏比例
   - 检查止损/止盈条件
5. 触发条件 → 执行卖出 → 写入通知
6. AI 读取 → 通知金哥
```

## 📁 目录结构

```
~/.openclaw/workspace/
├── .ai/                      # AI 助手专用目录 ⭐ NEW
│   ├── context.md            # 核心上下文（每次必加载）
│   ├── architecture.md       # 本文件：架构设计
│   ├── coding-rules.md       # 编码规范
│   ├── decisions.md          # 重要决策日志
│   └── memory.md             # 工作记忆（自动更新）
│
├── memory/                   # 记忆系统
│   ├── YYYY-MM-DD.md         # 每日工作日志
│   └── session-archive-*.md  # 会话归档
│
├── research/                 # 调研报告
│   └── claude-code-context-loss-analysis.md
│
├── meme_monitor_simple.py    # Meme 币监控脚本
├── position_manager.py       # 持仓管理脚本
├── memory_monitor.sh         # 内存监控脚本
├── positions.json            # 持仓数据
│
├── AGENTS.md                 # AI 行为准则
├── SOUL.md                   # AI 性格定义
├── USER.md                   # 用户信息
├── MEMORY.md                 # 长期记忆（主会话）
└── HEARTBEAT.md              # 心跳检查配置
```

## 🔌 关键集成点

### 1. Telegram 通道
- **插件**: openclaw-channel-telegram
- **配置**: `openclaw.json` → channels.telegram
- **功能**: 
  - 接收金哥消息
  - 发送通知和回复
  - 支持文件传输

### 2. Cron 调度器
- **管理**: OpenClaw 内置 cron 系统
- **任务列表**: 使用 `cron list` 查看
- **功能**:
  - 定时执行监控脚本
  - Heartbeat 触发
  - 定时提醒

### 3. 文件系统
- **工作目录**: `/Users/qianzhao/.openclaw/workspace`
- **临时文件**: `/tmp/meme_notify_pending.json` 等
- **权限**: root 用户权限

## 🧠 AI 上下文管理

### 三层记忆体系

**1. 热数据（对话上下文）**
- 最近 10-20 轮对话原文
- 当前任务相关代码片段
- **容量**: ~20K tokens

**2. 温数据（文件系统）**
- `.ai/context.md` - 每次必加载
- `.ai/architecture.md` - 按需加载
- `memory/YYYY-MM-DD.md` - 当日日志
- **容量**: ~15K tokens

**3. 冷数据（语义检索）**
- `MEMORY.md` - 长期记忆
- `memory/*.md` - 历史日志
- 向量数据库 (TODO)
- **容量**: 按需检索

### 自动加载策略

**每次会话开始**:
1. 自动加载 `.ai/context.md`（3K）
2. 检查 `memory/YYYY-MM-DD.md`（今日日志，5K）

**按需加载**:
- 需要架构信息 → 读取 `.ai/architecture.md`
- 需要编码规范 → 读取 `.ai/coding-rules.md`
- 需要历史决策 → 搜索 `.ai/decisions.md`

## 🔐 安全设计

**敏感信息保护**:
- API Keys 存储在环境变量或加密文件
- 私钥永不写入日志
- 钱包地址脱敏显示

**操作权限**:
- 自动监控: ✅ 无需确认
- 自动卖出: ✅ 仅止损/止盈
- 手动交易: ❌ 需金哥确认
- 系统配置: ❌ 需金哥确认

## 📊 监控指标

**系统健康**:
- 内存使用率 (告警阈值: 80%)
- CPU 使用率
- 磁盘空间
- 关键服务状态

**业务指标**:
- Meme 币发现数量 / 日
- 持仓数量和总市值
- 止损/止盈执行次数
- AI Token 消耗

---

**架构版本**: v1.0  
**最后更新**: 2026-02-08 20:19  
**维护者**: 紫龙
