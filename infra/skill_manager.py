#!/usr/bin/env python3
"""
技能记忆管理器
- 提取新技能
- 检索相关技能
- 更新技能效用评分
- 归档低效用技能
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

WORKSPACE = Path("/Users/qianzhao/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "memory" / "skills"
EXPERIENCE_DIR = WORKSPACE / "memory" / "experience"

class SkillManager:
    def __init__(self):
        self.skills_dir = SKILLS_DIR
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
    def list_skills(self, category: Optional[str] = None) -> List[Dict]:
        """列出所有技能"""
        skills = []
        for skill_file in self.skills_dir.glob("skill_*.json"):
            try:
                with open(skill_file, "r", encoding="utf-8") as f:
                    skill = json.load(f)
                    if category is None or skill.get("category") == category:
                        skills.append(skill)
            except Exception as e:
                print(f"❌ 读取技能文件失败: {skill_file.name} - {e}")
        
        # 按效用评分排序
        skills.sort(key=lambda s: s.get("utility_score", 0), reverse=True)
        return skills
    
    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """获取指定技能"""
        for skill in self.list_skills():
            if skill.get("id") == skill_id:
                return skill
        return None
    
    def search_skills(self, query: str, top_k: int = 5) -> List[Dict]:
        """语义搜索相关技能"""
        skills = self.list_skills()
        results = []
        
        query_lower = query.lower()
        
        for skill in skills:
            score = 0.0
            
            # 匹配触发条件
            for condition in skill.get("trigger_conditions", []):
                if query_lower in condition.lower():
                    score += 3.0
            
            # 匹配描述
            if query_lower in skill.get("description", "").lower():
                score += 2.0
            
            # 匹配名称
            if query_lower in skill.get("name", "").lower():
                score += 1.5
            
            # 考虑效用评分
            score += skill.get("utility_score", 0) * 0.1
            
            if score > 0:
                results.append({"skill": skill, "score": score})
        
        # 按匹配度排序
        results.sort(key=lambda r: r["score"], reverse=True)
        return [r["skill"] for r in results[:top_k]]
    
    def create_skill(self, name: str, description: str, category: str,
                     trigger_conditions: List[str], execution_steps: List[str],
                     examples: List[Dict] = None, notes: str = "") -> Dict:
        """创建新技能"""
        # 生成技能ID
        existing_ids = [int(s["id"].split("_")[1]) for s in self.list_skills() 
                        if s["id"].startswith("skill_")]
        next_id = max(existing_ids) + 1 if existing_ids else 1
        skill_id = f"skill_{next_id:03d}"
        
        # 生成文件名（从名称转换）
        safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
        filename = f"{skill_id}_{safe_name}.json"
        
        skill = {
            "id": skill_id,
            "name": name,
            "description": description,
            "category": category,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "last_used": datetime.now().strftime("%Y-%m-%d"),
            "trigger_conditions": trigger_conditions,
            "execution_steps": execution_steps,
            "examples": examples or [],
            "utility_score": 5.0,  # 初始中等评分
            "usage_count": 0,
            "application_history": [],
            "related_skills": [],
            "related_lessons": [],
            "related_patterns": [],
            "notes": notes
        }
        
        # 保存文件
        skill_path = self.skills_dir / filename
        with open(skill_path, "w", encoding="utf-8") as f:
            json.dump(skill, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 创建技能: {skill_id} - {name}")
        return skill
    
    def record_application(self, skill_id: str, scenario: str, 
                          success: bool, feedback: str = "") -> bool:
        """记录技能应用"""
        skill = self.get_skill(skill_id)
        if not skill:
            print(f"❌ 技能不存在: {skill_id}")
            return False
        
        # 更新应用记录
        application = {
            "applied_at": datetime.now().isoformat(),
            "scenario": scenario,
            "success": success,
            "feedback": feedback
        }
        
        if "application_history" not in skill:
            skill["application_history"] = []
        
        skill["application_history"].append(application)
        
        # 更新使用计数
        skill["usage_count"] = skill.get("usage_count", 0) + 1
        skill["last_used"] = datetime.now().strftime("%Y-%m-%d")
        
        # 更新效用评分
        if success:
            skill["utility_score"] = min(10.0, skill.get("utility_score", 5.0) + 0.1)
        else:
            skill["utility_score"] = max(0.0, skill.get("utility_score", 5.0) - 0.2)
        
        # 保存更新
        self._save_skill(skill)
        
        print(f"✅ 记录应用: {skill_id} - {'成功' if success else '失败'} - 评分: {skill['utility_score']:.1f}")
        return True
    
    def decay_unused_skills(self, days: int = 90):
        """衰减长期未使用的技能"""
        threshold = datetime.now() - timedelta(days=days)
        
        for skill in self.list_skills():
            last_used = datetime.strptime(skill.get("last_used", "2020-01-01"), "%Y-%m-%d")
            
            if last_used < threshold:
                # 降低效用评分
                old_score = skill.get("utility_score", 5.0)
                new_score = max(0.0, old_score - 1.0)
                skill["utility_score"] = new_score
                
                self._save_skill(skill)
                print(f"⚠️ 技能衰减: {skill['id']} ({old_score:.1f} → {new_score:.1f})")
    
    def archive_low_utility_skills(self, threshold: float = 3.0):
        """归档低效用技能"""
        archive_dir = self.skills_dir / "archived"
        archive_dir.mkdir(exist_ok=True)
        
        archived_count = 0
        for skill in self.list_skills():
            if skill.get("utility_score", 5.0) < threshold:
                skill_file = self._get_skill_file(skill["id"])
                if skill_file:
                    skill_file.rename(archive_dir / skill_file.name)
                    archived_count += 1
                    print(f"📦 归档技能: {skill['id']} - {skill['name']}")
        
        return archived_count
    
    def generate_report(self) -> str:
        """生成技能统计报告"""
        skills = self.list_skills()
        
        if not skills:
            return "📊 **技能报告**: 暂无技能记录"
        
        # 统计
        total = len(skills)
        by_category = {}
        by_utility = {"核心(9-10)": 0, "常用(7-8)": 0, "偶尔(5-6)": 0, "冷门(3-4)": 0, "淘汰(0-2)": 0}
        
        for skill in skills:
            category = skill.get("category", "未分类")
            by_category[category] = by_category.get(category, 0) + 1
            
            score = skill.get("utility_score", 5.0)
            if score >= 9:
                by_utility["核心(9-10)"] += 1
            elif score >= 7:
                by_utility["常用(7-8)"] += 1
            elif score >= 5:
                by_utility["偶尔(5-6)"] += 1
            elif score >= 3:
                by_utility["冷门(3-4)"] += 1
            else:
                by_utility["淘汰(0-2)"] += 1
        
        # 生成报告
        report = f"""📊 **技能记忆统计报告**

**总计**: {total} 个技能

**按类别分布**:
"""
        for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            report += f"  • {cat}: {count}\n"
        
        report += "\n**按效用等级**:\n"
        for level, count in by_utility.items():
            if count > 0:
                report += f"  • {level}: {count}\n"
        
        # Top 5 技能
        report += "\n**Top 5 核心技能**:\n"
        for i, skill in enumerate(skills[:5], 1):
            report += f"  {i}. {skill['name']} (评分: {skill.get('utility_score', 0):.1f}, 使用: {skill.get('usage_count', 0)}次)\n"
        
        return report
    
    def _get_skill_file(self, skill_id: str) -> Optional[Path]:
        """获取技能文件路径"""
        for skill_file in self.skills_dir.glob(f"{skill_id}_*.json"):
            return skill_file
        return None
    
    def _save_skill(self, skill: Dict):
        """保存技能到文件"""
        skill_file = self._get_skill_file(skill["id"])
        if skill_file:
            with open(skill_file, "w", encoding="utf-8") as f:
                json.dump(skill, f, indent=2, ensure_ascii=False)


def main():
    import sys
    
    manager = SkillManager()
    
    if len(sys.argv) < 2:
        print("用法: python3 skill_manager.py [list|search|create|apply|report|decay|archive]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        skills = manager.list_skills(category)
        for skill in skills:
            print(f"{skill['id']}: {skill['name']} (类别: {skill['category']}, 评分: {skill.get('utility_score', 0):.1f})")
    
    elif command == "search":
        query = " ".join(sys.argv[2:])
        skills = manager.search_skills(query)
        print(f"搜索结果: {query}\n")
        for skill in skills:
            print(f"• {skill['id']}: {skill['name']} (评分: {skill.get('utility_score', 0):.1f})")
            print(f"  描述: {skill['description']}")
            print()
    
    elif command == "report":
        print(manager.generate_report())
    
    elif command == "decay":
        manager.decay_unused_skills(days=90)
    
    elif command == "archive":
        count = manager.archive_low_utility_skills(threshold=3.0)
        print(f"✅ 归档了 {count} 个低效用技能")
    
    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()
