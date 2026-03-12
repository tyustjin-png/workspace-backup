#!/usr/bin/env python3
"""
周记忆压缩器
自动压缩一周的每日日志，生成周摘要
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SUMMARIES_DIR = MEMORY_DIR / "summaries"

def get_week_files(week_offset: int = 0) -> list:
    """
    获取指定周的日志文件
    week_offset: 0 = 本周, 1 = 上周, ...
    """
    today = datetime.now() - timedelta(weeks=week_offset)
    
    # 找到本周一
    monday = today - timedelta(days=today.weekday())
    
    week_files = []
    for i in range(7):
        day = monday + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        log_file = MEMORY_DIR / f"{date_str}.md"
        
        if log_file.exists():
            week_files.append({
                "date": date_str,
                "path": str(log_file),
                "day_name": day.strftime("%A")
            })
    
    return week_files


def generate_compression_prompt(week_offset: int = 0) -> str:
    """
    生成周压缩提示（供 LLM 处理）
    """
    week_files = get_week_files(week_offset)
    
    if not week_files:
        return "❌ 本周没有日志文件"
    
    # 读取所有文件内容
    week_content = ""
    for file_info in week_files:
        with open(file_info["path"], "r", encoding="utf-8") as f:
            content = f.read()
            week_content += f"\n## {file_info['day_name']} ({file_info['date']})\n\n{content}\n\n---\n"
    
    # 计算周编号
    first_date = datetime.strptime(week_files[0]["date"], "%Y-%m-%d")
    week_num = first_date.isocalendar()[1]
    year = first_date.year
    
    prompt = f"""# 周记忆压缩任务

分析这一周({year}年第{week_num}周)的每日日志，压缩为周摘要。

## 目标
- **减少 token 消耗**: 保留关键信息，删除重复/冗余内容
- **提取核心认知**: 重要决策、新学到的东西、值得记住的人/事/物
- **保持可检索性**: 压缩后仍能快速定位关键信息

## 压缩标准
1. **保留**:
   - 重要决策及其理由
   - 新学到的技能/知识
   - 待跟进事项
   - 值得长期记住的人/事/物
   - 教训和模式（已提炼到 lessons/patterns 的可简略）

2. **删除**:
   - 重复的日常汇报
   - 已完成的临时任务
   - 冗余的执行细节
   - 已归档到其他文件的内容

3. **合并**:
   - 相似的事件（如"连续3天都做了X"）
   - 同主题的讨论（如"Web3 雷达扫描"）

## 本周日志
{week_content}

## 输出格式
```markdown
# {year}年第{week_num}周 ({week_files[0]['date']} ~ {week_files[-1]['date']})

## 📌 核心事件
（最多5个重要事件，按重要性排序）

## 🎯 关键决策
（重要决策及理由，最多3个）

## 🧠 新学认知
（新学到的技能/知识/模式，最多5个）

## ✅ 完成事项
（值得记录的成就，最多5个）

## 📝 待跟进
（下周需要处理的事项）

## 💡 反思与教训
（值得记住的教训或启发）
```

## 压缩率目标
- 原始: ~{len(week_content)} 字符
- 目标: < {int(len(week_content) * 0.2)} 字符（压缩率 80%+）
"""
    
    return prompt


def save_summary(content: str, week_offset: int = 0):
    """保存周摘要"""
    week_files = get_week_files(week_offset)
    if not week_files:
        print("❌ 无法保存，没有日志文件")
        return
    
    SUMMARIES_DIR.mkdir(exist_ok=True)
    
    first_date = datetime.strptime(week_files[0]["date"], "%Y-%m-%d")
    year, week_num, _ = first_date.isocalendar()
    
    summary_file = SUMMARIES_DIR / f"{year}-W{week_num:02d}.md"
    
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ 周摘要已保存: {summary_file}")
    print(f"📊 压缩前: {sum(Path(f['path']).stat().st_size for f in week_files)} bytes")
    print(f"📊 压缩后: {summary_file.stat().st_size} bytes")
    print(f"📊 压缩率: {(1 - summary_file.stat().st_size / sum(Path(f['path']).stat().st_size for f in week_files)) * 100:.1f}%")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "prompt":
            # 只输出压缩提示
            week_offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            print(generate_compression_prompt(week_offset))
        elif sys.argv[1] == "save":
            # 保存摘要（从 stdin 读取）
            content = sys.stdin.read()
            week_offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            save_summary(content, week_offset)
        else:
            print("用法: python3 weekly_compression.py [prompt|save] [week_offset]")
    else:
        print(generate_compression_prompt())


if __name__ == "__main__":
    main()
