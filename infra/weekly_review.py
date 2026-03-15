#!/usr/bin/env python3
"""
每周总结 - 知识沉淀与清理
功能：
  - 模式库清理（置信度衰减）
  - 规则库优化（低效删除）
  - 知识图谱梳理
  - MEMORY.md 策展
  - 生成周报
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path("/Users/qianzhao/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
INFRA_DIR = WORKSPACE / "infra"

# 衰减配置
DECAY_WARN_DAYS = 60   # 60天未验证 → 降级
DECAY_ARCHIVE_DAYS = 90  # 90天未验证 → 归档


class WeeklyReview:
    """每周总结"""
    
    def __init__(self):
        self.today = datetime.now()
        self.report_lines = []
        self.actions = []
    
    def run(self) -> str:
        """执行完整每周总结"""
        self.report_lines = [
            f"# 📊 每周总结 {self.today.strftime('%Y-%m-%d')}",
            "",
            f"**生成时间：** {self.today.strftime('%H:%M:%S')}",
            "",
        ]
        
        # 1. 模式库清理
        self.cleanup_patterns()
        
        # 2. 规则库优化
        self.optimize_rules()
        
        # 3. 技能库维护（新增）
        self.maintain_skills()
        
        # 4. 知识图谱分析
        self.analyze_knowledge_graph()
        
        # 5. 本周成长回顾
        self.review_weekly_growth()
        
        # 6. 生成周报
        report = self.generate_report()
        
        # 保存周报
        report_file = INFRA_DIR / f"weekly_report_{self.today.strftime('%Y-%m-%d')}.md"
        report_file.write_text(report)
        
        return report
    
    def cleanup_patterns(self):
        """清理过期模式"""
        patterns_file = MEMORY_DIR / "patterns.md"
        if not patterns_file.exists():
            self.report_lines.append("## 📋 模式库清理")
            self.report_lines.append("- patterns.md 不存在")
            self.report_lines.append("")
            return
        
        content = patterns_file.read_text()
        
        # 解析最近验证日期
        # 格式：- **最近验证：** 2026-03-08
        pattern = r'\*\*最近验证：\*\*\s*(\d{4}-\d{2}-\d{2})'
        matches = re.findall(pattern, content)
        
        warn_count = 0
        archive_count = 0
        
        for date_str in matches:
            try:
                last_verified = datetime.strptime(date_str, "%Y-%m-%d")
                days_since = (self.today - last_verified).days
                
                if days_since >= DECAY_ARCHIVE_DAYS:
                    archive_count += 1
                elif days_since >= DECAY_WARN_DAYS:
                    warn_count += 1
            except:
                continue
        
        self.report_lines.append("## 📋 模式库清理")
        self.report_lines.append(f"- 总模式数：{len(matches)}")
        
        if warn_count > 0:
            self.report_lines.append(f"- ⚠️ {warn_count} 个模式超过60天未验证，建议确认或降级")
            self.actions.append({"type": "pattern_warn", "count": warn_count})
        
        if archive_count > 0:
            self.report_lines.append(f"- 🗑️ {archive_count} 个模式超过90天未验证，建议归档")
            self.actions.append({"type": "pattern_archive", "count": archive_count})
        
        if warn_count == 0 and archive_count == 0:
            self.report_lines.append("- ✅ 所有模式状态正常")
        
        self.report_lines.append("")
    
    def maintain_skills(self):
        """技能库维护（新增）"""
        import subprocess
        
        self.report_lines.append("## 🛠️ 技能库维护")
        
        # 执行技能衰减
        try:
            result = subprocess.run(
                ["python3", str(INFRA_DIR / "skill_manager.py"), "decay"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                self.report_lines.append("- ✅ 技能衰减检查完成")
            else:
                self.report_lines.append(f"- ⚠️ 技能衰减检查失败: {result.stderr}")
        except Exception as e:
            self.report_lines.append(f"- ❌ 技能衰减检查异常: {e}")
        
        # 归档低效用技能
        try:
            result = subprocess.run(
                ["python3", str(INFRA_DIR / "skill_manager.py"), "archive"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                self.report_lines.append(f"- {output}")
            else:
                self.report_lines.append(f"- ⚠️ 技能归档失败: {result.stderr}")
        except Exception as e:
            self.report_lines.append(f"- ❌ 技能归档异常: {e}")
        
        # 生成技能报告
        try:
            result = subprocess.run(
                ["python3", str(INFRA_DIR / "skill_manager.py"), "report"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                # 添加报告内容（缩进）
                report_lines = result.stdout.strip().split("\n")
                for line in report_lines:
                    self.report_lines.append(f"  {line}")
            else:
                self.report_lines.append(f"- ⚠️ 技能报告生成失败: {result.stderr}")
        except Exception as e:
            self.report_lines.append(f"- ❌ 技能报告异常: {e}")
        
        self.report_lines.append("")
    
    def optimize_rules(self):
        """优化规则库"""
        utility_file = INFRA_DIR / "rule_utility.json"
        
        self.report_lines.append("## 📜 规则库优化")
        
        if not utility_file.exists():
            self.report_lines.append("- 暂无规则效用数据")
            self.report_lines.append("")
            return
        
        utility = json.loads(utility_file.read_text())
        
        if not utility:
            self.report_lines.append("- 暂无规则应用记录")
            self.report_lines.append("")
            return
        
        # 统计
        high_utility = [r for r, d in utility.items() if d.get("avg", 5) >= 8]
        medium_utility = [r for r, d in utility.items() if 3 <= d.get("avg", 5) < 8]
        low_utility = [r for r, d in utility.items() if d.get("avg", 5) < 3]
        
        self.report_lines.append(f"- 高效规则（≥8分）：{len(high_utility)} 条")
        self.report_lines.append(f"- 中等规则（3-8分）：{len(medium_utility)} 条")
        
        if low_utility:
            self.report_lines.append(f"- ⚠️ 低效规则（<3分）：{len(low_utility)} 条，建议修订")
            for r in low_utility:
                self.report_lines.append(f"  - {r}: {utility[r]['avg']:.1f}分")
            self.actions.append({"type": "rule_revision", "rules": low_utility})
        else:
            self.report_lines.append("- ✅ 无低效规则")
        
        self.report_lines.append("")
    
    def analyze_knowledge_graph(self):
        """分析知识图谱"""
        links_file = INFRA_DIR / "kg_links.json"
        
        self.report_lines.append("## 🕸️ 知识图谱分析")
        
        if not links_file.exists():
            self.report_lines.append("- 暂无知识关联数据")
            self.report_lines.append("")
            return
        
        links = json.loads(links_file.read_text())
        
        # 统计节点和边
        nodes = set()
        for link in links:
            nodes.add(link["source"])
            nodes.add(link["target"])
        
        density = len(links) / len(nodes) if nodes else 0
        
        self.report_lines.append(f"- 知识节点：{len(nodes)}")
        self.report_lines.append(f"- 知识关联：{len(links)}")
        self.report_lines.append(f"- 连接密度：{density:.2f}")
        
        # 找出孤立节点（简化：这里只是示例）
        # 实际需要更复杂的图分析
        
        self.report_lines.append("")
    
    def review_weekly_growth(self):
        """回顾本周成长"""
        self.report_lines.append("## 📈 本周成长回顾")
        
        # 读取本周的daily logs
        week_start = self.today - timedelta(days=7)
        daily_files = list(MEMORY_DIR.glob("202*.md"))
        
        weekly_logs = []
        for f in daily_files:
            try:
                date_str = f.stem  # 2026-03-08
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date >= week_start:
                    weekly_logs.append(f)
            except:
                continue
        
        self.report_lines.append(f"- 本周日志：{len(weekly_logs)} 篇")
        
        # 读取学习触发器
        triggers_file = INFRA_DIR / "learning_triggers.json"
        if triggers_file.exists():
            triggers = json.loads(triggers_file.read_text())
            weekly_triggers = [
                t for t in triggers
                if datetime.fromisoformat(t["ts"]) >= week_start
            ]
            
            mistakes = len([t for t in weekly_triggers if t["type"] == "mistake"])
            corrections = len([t for t in weekly_triggers if t["type"] == "correction"])
            discoveries = len([t for t in weekly_triggers if t["type"] == "discovery"])
            
            self.report_lines.append(f"- 本周错误：{mistakes} 次")
            self.report_lines.append(f"- 本周纠正：{corrections} 次")
            self.report_lines.append(f"- 本周发现：{discoveries} 次")
        
        # 读取成长指标
        metrics_file = INFRA_DIR / "growth_metrics.json"
        if metrics_file.exists():
            metrics = json.loads(metrics_file.read_text())
            self.report_lines.append("")
            self.report_lines.append("### 当前成长指标")
            self.report_lines.append(f"- 教训转化率：{metrics.get('lesson_conversion_rate', 0):.0%}")
            self.report_lines.append(f"- 错误重复率：{metrics.get('error_repeat_rate', 0):.0%}")
            self.report_lines.append(f"- 规则平均效用：{metrics.get('avg_rule_utility', 5):.1f}/10")
            self.report_lines.append(f"- 知识连接密度：{metrics.get('connection_density', 0):.2f}")
        
        self.report_lines.append("")
    
    def generate_report(self) -> str:
        """生成完整周报"""
        # 添加行动建议
        if self.actions:
            self.report_lines.append("## 🎯 本周行动建议")
            for action in self.actions:
                if action["type"] == "pattern_warn":
                    self.report_lines.append(f"- [ ] 确认或降级 {action['count']} 个过期模式")
                elif action["type"] == "pattern_archive":
                    self.report_lines.append(f"- [ ] 归档 {action['count']} 个长期未验证模式")
                elif action["type"] == "rule_revision":
                    self.report_lines.append(f"- [ ] 修订 {len(action['rules'])} 条低效规则")
            self.report_lines.append("")
        
        # 添加结尾
        self.report_lines.append("---")
        self.report_lines.append(f"_生成时间：{self.today.isoformat()}_")
        
        return "\n".join(self.report_lines)


if __name__ == "__main__":
    review = WeeklyReview()
    report = review.run()
    print(report)
