# 项目核心上下文

> 本文件在每次 AI 会话开始时自动加载，包含项目最核心的上下文信息

## 📋 项目概览

**项目名称**: OpenClaw 个人助手系统  
**主要用户**: 金哥  
**启动时间**: 2026-02-08  
**当前版本**: v2.0  

## 🖥️ 运行环境

### Mac mini
- **OS**: macOS (Darwin 25.2.0, arm64)
- **Node**: v25.3.0
- **OpenClaw**: 2026.3.13 (stable)
- **AI 模型**: Claude Opus 4.6（默认）
- **角色**: Gateway + 紫龙主会话 + 全部 cron 任务
- **Bot**: Telegram @紫龙
- **代理**: Surge（HTTP :6152）

## 🎯 核心目标

1. **日常管理**: 日程追踪、定投执行、汇报推送
2. **投资辅助**: 定投系统、链上监控、美股跟踪
3. **系统监控**: 服务器健康、安全审计
4. **智能助手**: 信息整理、任务提醒、深度分析
5. **内容创作**: 公众号写作（每周三篇）

## ⚙️ 四大核心系统

### 1. 📅 日程系统
- 07:30 `create_daily_schedule.sh` 生成当日日程
- 10:00 / 15:00 / 19:00 推送日程汇报
- 数据：`memory/daily-schedule/YYYY-MM-DD.md`

### 2. 💰 定投系统
- 08:00 `xiaoding/auto_dca.sh` 执行定投
- 结果写入 `/tmp/xiaoding_notify.txt`
- heartbeat 08:00-08:10 推送结果

### 3. 📊 汇报系统
- 08:00 昨日总结 + 今日计划
- 21:00 完整审计与反思
- 21:30（周日）每周总结

### 4. 🔍 监控系统
- healthcheck 安全审计（周一四 02:00）
- CRCL 链上监控（周二-六 04:30）
- Web3 早期项目雷达（每日 08:00）

## ⏰ 系统 Cron（crontab）

| 时间 | 任务 |
|-----|------|
| 03:00 | daily_backup.sh |
| 07:00 | scripts/notification/reset_heartbeat_state.sh |
| 07:30 | scripts/schedule/create_daily_schedule.sh |
| 08:00 | xiaoding/auto_dca.sh |

## 📍 活跃项目

| 项目 | 路径 | 进度 |
|-----|------|------|
| Meme 币交易系统 | `projects/meme-trading-system/` | 85% |
| 多 Agent 协作系统 | `projects/multi-agent-collaboration-system/` | 0%（规划中）|
| 雅萍合作计费 | `projects/yaping-cooperation-billing/` | 待确认 |

## 🚨 重要约束

1. **安全第一**: 不外泄私钥、API key、个人信息
2. **谨慎操作**: 删除前确认，交易前验证
3. **自动化边界**: 自动监控 + 人工决策（重大操作需金哥确认）
4. **成本控制**: Token 消耗优化，避免无意义的重复查询

## 📝 工作习惯

- 异常才通知，正常静默
- 简洁直接，不废话
- 给方案让金哥选，不问开放问题
- Done > Perfect

## 🔗 快速链接

- **系统架构速查**: `memory/SYSTEMS.md`
- **长期记忆**: `MEMORY.md`
- **每日日志**: `memory/YYYY-MM-DD.md`
- **规则库**: `memory/rules.md`
- **教训库**: `memory/lessons.md`

---

**最后更新**: 2026-03-15 12:00  
**更新人**: 紫龙
