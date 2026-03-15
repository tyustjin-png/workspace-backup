# SYSTEMS.md - 运行中的系统架构

> 出问题时先读这个文件，了解系统全貌

---

## 📅 日程系统

**数据流：**
```
create_daily_schedule.sh (07:30)
    ↓
memory/daily-schedule/YYYY-MM-DD.md
    ↓
schedule_report.py (生成汇报)
    ↓
OpenClaw cron (10/15/19点推送)
```

**关键文件：**
- 日程数据：`memory/daily-schedule/YYYY-MM-DD.md`
- 创建脚本：`scripts/schedule/create_daily_schedule.sh`
- 汇报脚本：`scripts/schedule/schedule_report.py`
- 管理工具：`scripts/schedule/daily_schedule_manager.py`

**修复记录（2026-03-15）：**
- ✅ 已将 10/15/19 点汇报改为 `sessionTarget: main` + `systemEvent`
- 原因：isolated 模式的 delivery 机制失效

---

## 💰 定投系统

**数据流：**
```
auto_dca.sh (08:00 系统cron)
    ↓
小定 API 执行定投
    ↓
/tmp/xiaoding_notify.txt
    ↓
heartbeat 推送结果
```

**关键文件：**
- 主脚本：`xiaoding/auto_dca.sh`
- 结果文件：`/tmp/xiaoding_notify.txt`
- 日志：`xiaoding/logs/`

---

## 📊 汇报系统

| 时间 | 任务 | 目标 |
|-----|------|------|
| 08:00 | 每日总结（昨日回顾） | main session |
| 10:00/15:00/19:00 | 日程汇报 | Telegram |
| 21:00 | 完整审计与反思 | isolated |
| 21:30 周日 | 每周总结 | isolated |

---

## 🔍 监控系统

| 名称 | 频率 | 说明 |
|-----|------|------|
| healthcheck:security | 周一四 02:00 | 安全审计 |
| healthcheck:update | 周一四 02:05 | 更新状态 |
| CRCL每日监控 | 周二-六 04:30 | 链上数据 |
| Web3早期项目雷达 | 每日 08:00 | 项目扫描（有error） |

---

## ⏰ 系统 Cron（crontab -l）

| 时间 | 任务 |
|-----|------|
| 07:00 | scripts/notification/reset_heartbeat_state.sh |
| 07:30 | scripts/schedule/create_daily_schedule.sh |
| 08:00 | xiaoding/auto_dca.sh |
| 03:00 | daily_backup.sh |

> ⚠️ 注意：以上为 OpenClaw cron 任务，非系统 crontab。系统 crontab 仅有流动性监控。

---

## 🚨 故障排查清单

1. **日程没推送？**
   - 检查 `memory/daily-schedule/YYYY-MM-DD.md` 是否存在
   - 手动运行 `python3 schedule_report.py` 测试
   - 检查 OpenClaw cron 状态：`openclaw cron list`

2. **定投没执行？**
   - 检查 `/tmp/xiaoding_notify.txt`
   - 查看日志 `xiaoding/logs/`

3. **heartbeat 状态异常？**
   - 检查 `heartbeat_state.json`
   - 手动重置：`./reset_heartbeat_state.sh`

---

_最后更新：2026-03-15 10:16_
