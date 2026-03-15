#!/usr/bin/env python3
"""
日程汇报工具 - 按照金哥要求的格式输出完整日程
"""

import re
from datetime import datetime
from pathlib import Path

SCHEDULE_DIR = Path.home() / '.openclaw/workspace/memory/daily-schedule'

CATEGORY_EMOJI = {
    '运动': '⛹️',
    '投资': '💰',
    '写作': '✍️',
    '社交/人脉': '🤝',
    '家庭': '🏠'
}

def get_all_tasks(date=None):
    """获取所有任务（包括已完成和未完成）"""
    date = date or datetime.now().strftime('%Y-%m-%d')
    file_path = SCHEDULE_DIR / f"{date}.md"
    
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tasks = {
        '运动': {'completed': [], 'incomplete': []},
        '投资': {'completed': [], 'incomplete': []},
        '写作': {'completed': [], 'incomplete': []},
        '社交/人脉': {'completed': [], 'incomplete': []},
        '家庭': {'completed': [], 'incomplete': []}
    }
    
    for category in tasks.keys():
        # 匹配对应的章节
        pattern = f'## .*{category}([\\s\\S]*?)(?=##|---)'
        match = re.search(pattern, content)
        
        if match:
            section = match.group(1)
            for line in section.split('\n'):
                line = line.strip()
                if '- [x]' in line or '- [X]' in line:
                    # 已完成任务
                    task = re.sub(r'- \[[xX]\]\s*', '', line).strip()
                    # 移除已有的✅标记
                    task = task.replace('✅', '').strip()
                    if task:
                        tasks[category]['completed'].append(task)
                elif '- [ ]' in line:
                    # 未完成任务
                    task = re.sub(r'- \[ \]\s*', '', line).strip()
                    if task:
                        tasks[category]['incomplete'].append(task)
    
    return tasks

def generate_full_report(date=None):
    """生成完整日程汇报"""
    date = date or datetime.now().strftime('%Y-%m-%d')
    tasks = get_all_tasks(date)
    
    if tasks is None:
        return f"❌ {date} 的日程文件不存在"
    
    # 检查是否有任务
    has_tasks = any(
        len(cat['completed']) + len(cat['incomplete']) > 0
        for cat in tasks.values()
    )
    
    if not has_tasks:
        return f"📅 {date} 暂无日程安排"
    
    # 生成报告
    report_lines = [f"📋 **{date} 日程清单**\n"]
    
    for category, emoji in CATEGORY_EMOJI.items():
        category_tasks = tasks[category]
        completed = category_tasks['completed']
        incomplete = category_tasks['incomplete']
        
        # 如果该分类下有任务
        if completed or incomplete:
            report_lines.append(f"## {emoji} {category}")
            
            # 先列出已完成的
            for task in completed:
                report_lines.append(f"  • ✅ {task}")
            
            # 再列出未完成的
            for task in incomplete:
                report_lines.append(f"  • 🔸 {task}")
            
            report_lines.append("")  # 空行分隔
    
    # 添加统计
    total_completed = sum(len(cat['completed']) for cat in tasks.values())
    total_incomplete = sum(len(cat['incomplete']) for cat in tasks.values())
    total_tasks = total_completed + total_incomplete
    
    if total_tasks > 0:
        completion_rate = (total_completed / total_tasks) * 100
        report_lines.append("---")
        report_lines.append(f"**完成度**: {total_completed}/{total_tasks} ({completion_rate:.0f}%)")
    
    return '\n'.join(report_lines)

def save_report_to_file(output_path="/tmp/schedule_message.txt", date=None):
    """保存汇报到文件"""
    report = generate_full_report(date)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    return output_path

if __name__ == '__main__':
    import sys
    
    # 如果有参数，使用指定日期，否则使用今天
    date = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 生成并输出汇报
    report = generate_full_report(date)
    print(report)
    
    # 也保存到文件
    save_report_to_file(date=date)
