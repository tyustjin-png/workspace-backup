#!/usr/bin/env python3
"""
每日日程管理器 v2
格式：[ ] 未完成 / [✓] 已完成（纯文本，兼容备忘录）
"""

import re
import sys
from datetime import datetime
from pathlib import Path

SCHEDULE_DIR = Path.home() / '.openclaw/workspace/memory/daily-schedule'
SCHEDULE_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE = """# 📋 {date} 日程清单

今日最感悟一句话：（待填）

⛹️ 运动
[ ] 100仰卧起坐
[ ] 50俯卧撑
[ ] 20深蹲
[ ] 100提臀

💰 投资
[ ] 定投相关
[ ] 链上数据

✍️ 写作
[ ] 邮件
[ ] 公众号
[ ] 推特

🏠 家庭
[ ] 罗老师
[ ] 父母
[ ] 儿子

完成度: 0/13 (0%)
"""

CATEGORIES = {
    '运动': ['跑步', '健身', '仰卧起坐', '俯卧撑', '深蹲', '提臀', '游泳', '打球', '运动', '锻炼'],
    '投资': ['定投', '买入', '卖出', 'BTC', 'ETH', '链上', '币', '交易', '币安', '充值', '硬盘'],
    '写作': ['邮件', 'email', '公众号', '推特', 'twitter', '文章', '博客'],
    '家庭': ['罗老师', '老婆', '父母', '爸妈', '儿子', '孩子', '家人', '陪'],
}


def get_schedule_path(date=None):
    date = date or datetime.now().strftime('%Y-%m-%d')
    return SCHEDULE_DIR / f"{date}.md"


def create_schedule(date=None):
    date = date or datetime.now().strftime('%Y-%m-%d')
    path = get_schedule_path(date)
    if not path.exists():
        path.write_text(TEMPLATE.format(date=date), encoding='utf-8')
        print(f"已创建日程: {date}")
    else:
        print(f"日程已存在: {date}")
    return path


def read_schedule(date=None):
    path = get_schedule_path(date)
    if not path.exists():
        path = create_schedule(date)
    return path.read_text(encoding='utf-8')


def complete_task(keyword, date=None):
    """标记任务完成：[ ] → [✓]"""
    path = get_schedule_path(date)
    if not path.exists():
        print(f"日程文件不存在")
        return False
    
    content = path.read_text(encoding='utf-8')
    lines = content.split('\n')
    found = False
    
    for i, line in enumerate(lines):
        if '[ ]' in line and keyword.lower() in line.lower():
            lines[i] = line.replace('[ ]', '[✓]')
            found = True
            print(f"已完成: {lines[i].strip()}")
            break
    
    if not found:
        for i, line in enumerate(lines):
            if '[ ]' in line:
                if any(k in line.lower() for k in keyword.lower().split()):
                    lines[i] = line.replace('[ ]', '[✓]')
                    found = True
                    print(f"已完成: {lines[i].strip()}")
                    break
    
    if found:
        content = '\n'.join(lines)
        content = update_completion_rate(content)
        path.write_text(content, encoding='utf-8')
    else:
        print(f"未找到匹配任务: {keyword}")
    
    return found


def add_task(category, task_text, date=None):
    path = get_schedule_path(date)
    if not path.exists():
        create_schedule(date)
    
    content = path.read_text(encoding='utf-8')
    cat_emoji = {'运动': '⛹️', '投资': '💰', '写作': '✍️', '家庭': '🏠'}
    emoji = cat_emoji.get(category, '📌')
    header = f'{emoji} {category}'
    
    if header in content:
        lines = content.split('\n')
        insert_idx = None
        in_section = False
        for i, line in enumerate(lines):
            if header in line:
                in_section = True
            elif in_section:
                if line.strip() and not line.startswith('['):
                    insert_idx = i
                    break
                if line.startswith('['):
                    insert_idx = i + 1
        
        if insert_idx:
            while insert_idx > 0 and lines[insert_idx - 1].strip() == '':
                insert_idx -= 1
            lines.insert(insert_idx, f'[ ] {task_text}')
            content = '\n'.join(lines)
            content = update_completion_rate(content)
            path.write_text(content, encoding='utf-8')
            print(f"已添加到【{category}】: {task_text}")
            return True
    
    print(f"未找到分类: {category}")
    return False


def update_completion_rate(content):
    done = len(re.findall(r'\[·\]', content))
    todo = len(re.findall(r'\[ \]', content))
    total = done + todo
    rate = int(done / total * 100) if total > 0 else 0
    content = re.sub(r'完成度:.*', f'完成度: {done}/{total} ({rate}%)', content)
    return content


def get_summary(date=None):
    content = read_schedule(date)
    done = len(re.findall(r'\[·\]', content))
    todo = len(re.findall(r'\[ \]', content))
    total = done + todo
    rate = int(done / total * 100) if total > 0 else 0
    return {'done': done, 'todo': todo, 'total': total, 'rate': rate}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  create          创建今日日程")
        print("  complete '定投'  标记完成")
        print("  add '投资' 'xx'  添加任务")
        print("  summary         摘要")
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'create':
        create_schedule()
    elif cmd == 'complete':
        complete_task(sys.argv[2] if len(sys.argv) > 2 else '')
    elif cmd == 'add':
        add_task(sys.argv[2] if len(sys.argv) > 2 else '', sys.argv[3] if len(sys.argv) > 3 else '')
    elif cmd == 'summary':
        s = get_summary()
        print(f"完成 {s['done']}/{s['total']} ({s['rate']}%)")
    else:
        complete_task(cmd)
