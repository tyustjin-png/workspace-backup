#!/usr/bin/env python3
"""
审计修正Agent - 独立验证与自动修正
功能：
  - 读取规则（HEARTBEAT.md）
  - 检查今日执行情况
  - 自动修正低风险问题
  - 生成审计报告
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path("/Users/qianzhao/.openclaw/workspace")
AUDIT_LOG = WORKSPACE / "infra" / "audit_log.jsonl"
AUDIT_REPORT = WORKSPACE / "infra" / "audit_report.md"

# 导入基础设施
import sys
sys.path.insert(0, str(WORKSPACE / "infra"))
from state_center import get, get_pending_tasks, get_completed_tasks, mark_notification_sent
from notification_center import get_pending_notifications


class AuditAgent:
    """审计修正Agent"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.issues = []
        self.fixes = []
        self.report_lines = []
    
    def log(self, action: str, details: dict):
        """记录审计日志"""
        entry = {
            "ts": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def add_issue(self, level: str, category: str, description: str, fix_action: str = None):
        """
        添加问题
        level: green (自动修正), yellow (建议修正), red (人工处理)
        """
        issue = {
            "level": level,
            "category": category,
            "description": description,
            "fix_action": fix_action
        }
        self.issues.append(issue)
        self.log("issue_found", issue)
    
    def add_fix(self, category: str, action: str, result: str):
        """记录修正操作"""
        fix = {
            "category": category,
            "action": action,
            "result": result,
            "ts": datetime.now().isoformat()
        }
        self.fixes.append(fix)
        self.log("fix_applied", fix)
    
    # ===== 检查项 =====
    
    def check_xiaoding(self):
        """检查定投执行情况"""
        xiaoding_state = get("daily_tasks.xiaoding")
        
        if xiaoding_state is None:
            self.add_issue("yellow", "xiaoding", "无法获取定投状态", None)
            return
        
        status = xiaoding_state.get("status")
        
        if status == "completed":
            # 检查是否同步到日程
            schedule_file = WORKSPACE / "memory" / "daily-schedule" / f"{self.today}.md"
            if schedule_file.exists():
                content = schedule_file.read_text()
                if "定投" in content and "[x]" in content.lower():
                    self.report_lines.append("✅ 定投：已执行并同步日程")
                else:
                    self.add_issue("green", "xiaoding", "定投已执行但日程未同步", "sync_schedule")
            else:
                self.add_issue("yellow", "xiaoding", "日程文件不存在", None)
        elif status == "pending":
            # 今天没执行定投，检查是否应该执行
            now_hour = datetime.now().hour
            if now_hour >= 9:  # 8点后还没执行
                self.add_issue("yellow", "xiaoding", "定投未执行（应在08:00）", None)
            else:
                self.report_lines.append("⏳ 定投：待执行")
        else:
            self.add_issue("yellow", "xiaoding", f"定投状态异常: {status}", None)
    
    def check_schedule_reports(self):
        """检查日程汇报推送情况"""
        now_hour = datetime.now().hour
        
        checks = [
            ("schedule_10", 10, "10:00日程汇报"),
            ("schedule_15", 15, "15:00日程汇报"),
            ("schedule_19", 19, "19:00日程汇报"),
        ]
        
        for task_name, hour, desc in checks:
            if now_hour < hour:
                self.report_lines.append(f"⏳ {desc}：待执行")
                continue
            
            task_state = get(f"daily_tasks.{task_name}")
            if task_state is None:
                self.add_issue("green", task_name, f"{desc}状态未记录", "mark_pending")
                continue
            
            status = task_state.get("status")
            if status in ["completed", "sent"]:
                self.report_lines.append(f"✅ {desc}：已发送")
            else:
                self.add_issue("green", task_name, f"{desc}未发送", "resend_schedule")
    
    def check_notification_delivery(self):
        """检查通知送达情况"""
        pending = get_pending_notifications()
        
        if not pending:
            self.report_lines.append("✅ 通知：无待处理通知")
            return
        
        for notif in pending:
            category = notif.get("category")
            self.add_issue("green", "notification", f"通知未确认送达: {category}", "verify_delivery")
    
    # ===== 修正操作 =====
    
    def fix_sync_schedule(self):
        """修正：同步日程"""
        try:
            import subprocess
            result = subprocess.run(
                ["python3", str(WORKSPACE / "daily_schedule_manager.py"), "定投相关完成"],
                capture_output=True,
                text=True,
                cwd=str(WORKSPACE)
            )
            if result.returncode == 0:
                self.add_fix("xiaoding", "sync_schedule", "success")
                return True
            else:
                self.add_fix("xiaoding", "sync_schedule", f"failed: {result.stderr}")
                return False
        except Exception as e:
            self.add_fix("xiaoding", "sync_schedule", f"error: {str(e)}")
            return False
    
    def fix_mark_pending(self, task_name: str):
        """修正：标记任务状态"""
        try:
            from state_center import update
            update(f"daily_tasks.{task_name}.status", "pending", "audit_agent")
            self.add_fix(task_name, "mark_pending", "success")
            return True
        except Exception as e:
            self.add_fix(task_name, "mark_pending", f"error: {str(e)}")
            return False
    
    def fix_resend_schedule(self, task_name: str):
        """
        修正：重发日程汇报
        注意：这里只是标记需要重发，实际发送由主Agent完成
        """
        try:
            # 生成日程汇报内容
            import subprocess
            result = subprocess.run(
                ["python3", str(WORKSPACE / "schedule_report.py")],
                capture_output=True,
                text=True,
                cwd=str(WORKSPACE)
            )
            
            if result.returncode == 0:
                # 写入待发送文件
                resend_file = WORKSPACE / "infra" / "pending_notifications.json"
                pending = []
                if resend_file.exists():
                    pending = json.loads(resend_file.read_text())
                
                pending.append({
                    "ts": datetime.now().isoformat(),
                    "category": "schedule",
                    "task_name": task_name,
                    "message": result.stdout,
                    "status": "pending"
                })
                
                resend_file.write_text(json.dumps(pending, ensure_ascii=False, indent=2))
                self.add_fix(task_name, "resend_schedule", "queued")
                return True
            else:
                self.add_fix(task_name, "resend_schedule", f"failed: {result.stderr}")
                return False
        except Exception as e:
            self.add_fix(task_name, "resend_schedule", f"error: {str(e)}")
            return False
    
    def apply_fixes(self):
        """应用所有自动修正"""
        for issue in self.issues:
            if issue["level"] != "green":
                continue  # 只自动修正 green 级别
            
            fix_action = issue.get("fix_action")
            if not fix_action:
                continue
            
            if fix_action == "sync_schedule":
                self.fix_sync_schedule()
            elif fix_action == "mark_pending":
                self.fix_mark_pending(issue["category"])
            elif fix_action == "resend_schedule":
                self.fix_resend_schedule(issue["category"])
    
    # ===== 报告生成 =====
    
    def generate_report(self) -> str:
        """生成审计报告"""
        lines = [
            f"# 📊 每日审计报告 {self.today}",
            "",
            f"**审计时间：** {datetime.now().strftime('%H:%M:%S')}",
            "",
        ]
        
        # 正常项
        if self.report_lines:
            lines.append("## ✅ 正常执行")
            lines.extend(self.report_lines)
            lines.append("")
        
        # 问题统计
        green_issues = [i for i in self.issues if i["level"] == "green"]
        yellow_issues = [i for i in self.issues if i["level"] == "yellow"]
        red_issues = [i for i in self.issues if i["level"] == "red"]
        
        # 自动修正的问题
        if green_issues:
            lines.append("## 🟢 已自动修正")
            for issue in green_issues:
                fix_result = next((f for f in self.fixes if f["category"] == issue["category"]), None)
                result_str = f"→ {fix_result['result']}" if fix_result else ""
                lines.append(f"- {issue['description']} {result_str}")
            lines.append("")
        
        # 建议修正的问题
        if yellow_issues:
            lines.append("## 🟡 建议修正（需确认）")
            for issue in yellow_issues:
                lines.append(f"- {issue['description']}")
            lines.append("")
        
        # 需人工处理的问题
        if red_issues:
            lines.append("## 🔴 需人工处理")
            for issue in red_issues:
                lines.append(f"- {issue['description']}")
            lines.append("")
        
        # 待发送通知
        resend_file = WORKSPACE / "infra" / "pending_notifications.json"
        if resend_file.exists():
            pending = json.loads(resend_file.read_text())
            pending_count = len([p for p in pending if p.get("status") == "pending"])
            if pending_count > 0:
                lines.append(f"## 📤 待发送通知：{pending_count}条")
                lines.append("主Agent下次运行时会自动发送")
                lines.append("")
        
        # 总结
        total_issues = len(self.issues)
        auto_fixed = len([f for f in self.fixes if f["result"] == "success"])
        
        lines.append("---")
        lines.append(f"**总结：** 发现 {total_issues} 个问题，自动修正 {auto_fixed} 个")
        
        if not self.issues:
            lines.append("✨ 今日所有任务正常执行，无需修正")
        
        report = "\n".join(lines)
        
        # 保存报告
        AUDIT_REPORT.write_text(report)
        
        return report
    
    # ===== 反思功能 =====
    
    def reflect_on_today(self) -> dict:
        """
        每日反思 - 从今日经历中提取知识
        """
        from learning_engine import (
            get_unprocessed_triggers,
            mark_trigger_processed,
            detect_patterns,
            calculate_growth_metrics
        )
        
        reflection = {
            "triggers_processed": 0,
            "patterns_detected": 0,
            "lessons_created": 0,
            "metrics": {}
        }
        
        # 1. 处理学习触发器
        triggers = get_unprocessed_triggers()
        for trigger in triggers:
            outcome = self.process_trigger(trigger)
            mark_trigger_processed(trigger["id"], outcome)
            reflection["triggers_processed"] += 1
            if outcome == "lesson":
                reflection["lessons_created"] += 1
        
        # 2. 检测重复模式
        patterns = detect_patterns(days=30)
        reflection["patterns_detected"] = len(patterns)
        
        if patterns:
            self.suggest_patterns(patterns)
        
        # 3. 审计规则效用
        self.audit_rule_utility()
        
        # 4. 计算成长指标
        reflection["metrics"] = calculate_growth_metrics()
        
        self.log("reflection_complete", reflection)
        
        return reflection
    
    def process_trigger(self, trigger: dict) -> str:
        """处理单个学习触发器"""
        # 高严重度 → 教训
        if trigger.get("severity") == "high":
            return "lesson"
        
        # 被纠正 → 教训
        if trigger.get("type") == "correction":
            return "lesson"
        
        # 新发现 → 待观察
        if trigger.get("type") == "discovery":
            return "pattern_candidate"
        
        # 普通错误 → 记录但不升级
        return "logged"
    
    def suggest_patterns(self, patterns: list):
        """将检测到的模式写入待确认列表"""
        suggestions_file = WORKSPACE / "infra" / "pattern_suggestions.json"
        
        existing = []
        if suggestions_file.exists():
            existing = json.loads(suggestions_file.read_text())
        
        for p in patterns:
            suggestion = {
                "ts": datetime.now().isoformat(),
                "key": p["key"],
                "count": p["count"],
                "description": p["suggested_pattern"],
                "status": "pending_review"
            }
            existing.append(suggestion)
        
        suggestions_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    
    def audit_rule_utility(self):
        """审计规则效用评分"""
        utility_file = WORKSPACE / "infra" / "rule_utility.json"
        if not utility_file.exists():
            return
        
        utility = json.loads(utility_file.read_text())
        
        low_utility_rules = []
        for rule_id, data in utility.items():
            if data.get("avg", 5.0) < 3.0:
                low_utility_rules.append({
                    "rule_id": rule_id,
                    "avg_score": data["avg"],
                    "recommendation": "待修订"
                })
        
        if low_utility_rules:
            # 写入待修订列表
            revision_file = WORKSPACE / "infra" / "rules_pending_revision.json"
            revision_file.write_text(json.dumps(low_utility_rules, ensure_ascii=False, indent=2))
            self.report_lines.append(f"⚠️ {len(low_utility_rules)} 条规则效用偏低，待修订")
    
    def generate_reflection_report(self, reflection: dict) -> str:
        """生成反思报告"""
        lines = [
            "",
            "---",
            "",
            "## 🧠 每日反思",
            "",
        ]
        
        if reflection["triggers_processed"] > 0:
            lines.append(f"- 处理学习触发：{reflection['triggers_processed']} 条")
        
        if reflection["lessons_created"] > 0:
            lines.append(f"- 新增教训：{reflection['lessons_created']} 条")
        
        if reflection["patterns_detected"] > 0:
            lines.append(f"- 检测到重复模式：{reflection['patterns_detected']} 个（待确认）")
        
        metrics = reflection.get("metrics", {})
        if metrics:
            lines.append("")
            lines.append("### 📊 成长指标")
            lines.append(f"- 教训转化率：{metrics.get('lesson_conversion_rate', 0):.0%}")
            lines.append(f"- 错误重复率：{metrics.get('error_repeat_rate', 0):.0%}")
            lines.append(f"- 规则平均效用：{metrics.get('avg_rule_utility', 5.0):.1f}/10")
            lines.append(f"- 知识连接密度：{metrics.get('connection_density', 0):.2f}")
        
        return "\n".join(lines)
    
    def run(self) -> str:
        """执行完整审计+反思流程"""
        self.log("audit_start", {"date": self.today})
        
        # 1. 执行检查
        self.check_xiaoding()
        self.check_schedule_reports()
        self.check_notification_delivery()
        
        # 2. 应用自动修正
        self.apply_fixes()
        
        # 3. 每日反思
        reflection = self.reflect_on_today()
        
        # 4. 生成报告
        report = self.generate_report()
        
        # 5. 追加反思报告
        reflection_report = self.generate_reflection_report(reflection)
        report += reflection_report
        
        # 更新保存的报告
        AUDIT_REPORT.write_text(report)
        
        self.log("audit_complete", {
            "issues": len(self.issues),
            "fixes": len(self.fixes),
            "reflection": reflection
        })
        
        return report


def get_pending_notifications_for_main_agent() -> list:
    """供主Agent调用：获取待发送的通知"""
    resend_file = WORKSPACE / "infra" / "pending_notifications.json"
    if not resend_file.exists():
        return []
    
    pending = json.loads(resend_file.read_text())
    return [p for p in pending if p.get("status") == "pending"]


def mark_notification_delivered(task_name: str):
    """供主Agent调用：标记通知已发送"""
    resend_file = WORKSPACE / "infra" / "pending_notifications.json"
    if not resend_file.exists():
        return
    
    pending = json.loads(resend_file.read_text())
    for p in pending:
        if p.get("task_name") == task_name and p.get("status") == "pending":
            p["status"] = "delivered"
            p["delivered_at"] = datetime.now().isoformat()
    
    resend_file.write_text(json.dumps(pending, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    agent = AuditAgent()
    report = agent.run()
    print(report)
