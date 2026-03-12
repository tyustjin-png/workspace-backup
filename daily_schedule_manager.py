#!/usr/bin/env python3
"""
每日日程管理器
支持自动分类、任务追踪、提醒功能
"""

import json
import re
from datetime import datetime
from pathlib import Path

# 配置
SCHEDULE_DIR = Path.home() / '.openclaw/workspace/memory/daily-schedule'
SCHEDULE_DIR.mkdir(parents=True, exist_ok=True)

# 日程模板
SCHEDULE_TEMPLATE = """# 每日日程 {date}

## 💬 今日最感悟一句话
{quote}

## ⛹️ 运动
- [ ] 100仰卧起坐
- [ ] 50俯卧撑
- [ ] 20深蹲
- [ ] 100提臀
{extra_exercise}

## 💰 投资
- [ ] 定投相关
- [ ] 链上数据
{extra_investment}

## ✍️ 写作
- [ ] 邮件
- [ ] 公众号
- [ ] 推特
{extra_writing}

## 🤝 社交/人脉
- [ ] 行业交流
- [ ] 朋友聚会
{extra_social}

## 🏠 家庭
- [ ] 罗老师
- [ ] 父母
- [ ] 儿子
{extra_family}

---
_最后更新：{update_time}_
"""

# 分类关键词
CATEGORY_KEYWORDS = {
    '运动': [
        '跑步', '跑了', '健身', '仰卧起坐', '俯卧撑', '深蹲', '提臀',
        '游泳', '打球', '瑜伽', '骑车', '走路', '运动', 'km', '公里',
        '锻炼', '训练'
    ],
    '投资': [
        '定投', '买入', '卖出', '持仓', 'BTC', 'ETH', 'USDT', 'SOL',
        '链上', '钱包', 'meme', '币', '交易', 'Binance', '币安',
        '分析', '市场', '涨', '跌', 'K线', '止损', '止盈'
    ],
    '写作': [
        '邮件', 'email', '公众号', '推特', 'twitter', 'X',
        '写了', '发了', '推文', '文章', '博客', '笔记',
        '回复', '评论', '更新'
    ],
    '社交/人脉': [
        '午餐', '晚餐', '聚会', '见面', '拜访', '团队', '同学',
        '朋友', '合作', '商务', '会议', '交流', '分享', '社交',
        '人脉', '拓展', '行业', '活动', '峰会', 'coffee', '咖啡',
        '饭局', '应酬', '聊', '认识', '介绍'
    ],
    '家庭': [
        '罗老师', '老婆', '媳妇', '父母', '爸妈', '爸', '妈',
        '儿子', '孩子', '宝宝', '家人', '陪', '通话', '电话',
        '视频', '聊天'
    ]
}


class DailyScheduleManager:
    """每日日程管理器"""
    
    def __init__(self, date=None):
        self.date = date or datetime.now().strftime('%Y-%m-%d')
        self.file_path = SCHEDULE_DIR / f"{self.date}.md"
        self.schedule = self.load_schedule()
    
    def load_schedule(self):
        """加载日程"""
        if not self.file_path.exists():
            # 创建新日程
            content = SCHEDULE_TEMPLATE.format(
                date=self.date,
                quote='',
                extra_exercise='',
                extra_investment='',
                extra_writing='',
                extra_social='',
                extra_family='',
                update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            self.file_path.write_text(content, encoding='utf-8')
            return content
        
        return self.file_path.read_text(encoding='utf-8')
    
    def save_schedule(self):
        """保存日程"""
        # 更新时间戳
        self.schedule = re.sub(
            r'_最后更新：.*_',
            f'_最后更新：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}_',
            self.schedule
        )
        self.file_path.write_text(self.schedule, encoding='utf-8')
    
    def classify_input(self, text):
        """
        分类用户输入
        返回：(category, subcategory, is_completion)
        """
        text_lower = text.lower()
        
        # 检测是否是完成任务
        is_completion = any(word in text for word in [
            '完成', '做了', '跑了', '写了', '买了', '定投了',
            '打了', '发了', '回复了', '陪了', '通话了'
        ])
        
        # 按分数匹配最佳分类
        scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return None, None, is_completion
        
        # 返回得分最高的分类
        best_category = max(scores, key=scores.get)
        
        return best_category, None, is_completion
    
    def add_task(self, category, task_text):
        """添加任务到指定分类"""
        # 找到分类section
        category_emoji = {
            '运动': '⛹️',
            '投资': '💰',
            '写作': '✍️',
            '社交/人脉': '🤝',
            '家庭': '🏠'
        }
        
        emoji = category_emoji.get(category, '📌')
        pattern = f'## {emoji} {category}([\\s\\S]*?)(?=##|---)'
        
        match = re.search(pattern, self.schedule)
        if match:
            section = match.group(1)
            # 在section末尾添加新任务
            new_task = f"- [ ] {task_text}\n"
            updated_section = section.rstrip() + '\n' + new_task
            self.schedule = self.schedule.replace(match.group(0), f'## {emoji} {category}{updated_section}')
            self.save_schedule()
            return True
        return False
    
    def complete_task(self, category, task_keyword):
        """
        标记任务为完成
        task_keyword: 任务关键词，用于匹配
        """
        category_emoji = {
            '运动': '⛹️',
            '投资': '💰',
            '写作': '✍️',
            '社交/人脉': '🤝',
            '家庭': '🏠'
        }
        
        # 提取纯任务名（去掉"完成了"、"做了"等前缀）
        clean_keyword = task_keyword
        for prefix in ['完成了', '做了', '跑了', '写了', '买了', '定投了', '打了', '发了', '回复了', '陪了', '通话了']:
            clean_keyword = clean_keyword.replace(prefix, '').strip()
        
        emoji = category_emoji.get(category, '📌')
        pattern = f'## {emoji} {category}([\\s\\S]*?)(?=##|---)'
        
        match = re.search(pattern, self.schedule)
        if not match:
            return False, None
        
        section = match.group(1)
        lines = section.split('\n')
        updated_lines = []
        completed_task = None
        
        for line in lines:
            # 查找匹配的未完成任务（模糊匹配）
            if '- [ ]' in line:
                line_text = line.replace('- [ ]', '').strip()
                # 检查关键词是否在任务中（双向匹配）
                if (clean_keyword.lower() in line_text.lower() or 
                    line_text.lower() in clean_keyword.lower()):
                    # 标记为完成
                    updated_line = line.replace('- [ ]', '- [x]')
                    updated_lines.append(updated_line)
                    completed_task = line_text
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        if completed_task:
            updated_section = '\n'.join(updated_lines)
            self.schedule = self.schedule.replace(match.group(0), f'## {emoji} {category}{updated_section}')
            self.save_schedule()
            return True, completed_task
        
        # 如果没找到匹配的任务，添加新任务并标记完成
        new_task = f"- [x] {clean_keyword}\n"
        updated_section = section.rstrip() + '\n' + new_task
        self.schedule = self.schedule.replace(match.group(0), f'## {emoji} {category}{updated_section}')
        self.save_schedule()
        return True, task_keyword
    
    def set_quote(self, quote):
        """设置今日感悟"""
        self.schedule = re.sub(
            r'## 💬 今日最感悟一句话\n.*\n',
            f'## 💬 今日最感悟一句话\n{quote}\n',
            self.schedule
        )
        self.save_schedule()
    
    def get_incomplete_tasks(self):
        """获取未完成任务列表"""
        incomplete = {
            '运动': [],
            '投资': [],
            '写作': [],
            '社交/人脉': [],
            '家庭': []
        }
        
        for category in incomplete.keys():
            pattern = f'## .*{category}([\\s\\S]*?)(?=##|---)'
            match = re.search(pattern, self.schedule)
            if match:
                section = match.group(1)
                for line in section.split('\n'):
                    if '- [ ]' in line:
                        task = line.replace('- [ ]', '').strip()
                        if task:
                            incomplete[category].append(task)
        
        return incomplete
    
    def get_completed_tasks(self):
        """获取已完成任务列表"""
        completed = {
            '运动': [],
            '投资': [],
            '写作': [],
            '社交/人脉': [],
            '家庭': []
        }
        
        for category in completed.keys():
            pattern = f'## .*{category}([\\s\\S]*?)(?=##|---)'
            match = re.search(pattern, self.schedule)
            if match:
                section = match.group(1)
                for line in section.split('\n'):
                    if '- [x]' in line:
                        task = line.replace('- [x]', '').strip()
                        if task:
                            completed[category].append(task)
        
        return completed
    
    def get_summary(self):
        """获取日程摘要"""
        incomplete = self.get_incomplete_tasks()
        completed = self.get_completed_tasks()
        
        # 统计
        total_incomplete = sum(len(tasks) for tasks in incomplete.values())
        total_completed = sum(len(tasks) for tasks in completed.values())
        total_tasks = total_incomplete + total_completed
        
        if total_tasks == 0:
            completion_rate = 0
        else:
            completion_rate = (total_completed / total_tasks) * 100
        
        summary = {
            'date': self.date,
            'total_tasks': total_tasks,
            'completed': total_completed,
            'incomplete': total_incomplete,
            'completion_rate': completion_rate,
            'completed_by_category': completed,
            'incomplete_by_category': incomplete
        }
        
        return summary


def format_reminder(incomplete_tasks):
    """格式化提醒消息"""
    if not any(incomplete_tasks.values()):
        return "🎉 太棒了！今天所有任务都完成了！"
    
    msg = "📋 **今日待办提醒**\n\n"
    
    emoji_map = {
        '运动': '⛹️',
        '投资': '💰',
        '写作': '✍️',
        '社交/人脉': '🤝',
        '家庭': '🏠'
    }
    
    for category, tasks in incomplete_tasks.items():
        if tasks:
            msg += f"{emoji_map.get(category, '📌')} **{category}**（{len(tasks)}项）\n"
            for task in tasks:
                msg += f"  • {task}\n"
            msg += "\n"
    
    return msg.rstrip()


def format_daily_summary(summary):
    """格式化每日总结"""
    msg = f"📊 **每日总结 {summary['date']}**\n\n"
    msg += f"✅ 完成：{summary['completed']}项\n"
    msg += f"⏳ 未完成：{summary['incomplete']}项\n"
    msg += f"📈 完成率：{summary['completion_rate']:.1f}%\n\n"
    
    if summary['completed'] > 0:
        msg += "**✨ 今日成就**\n"
        for category, tasks in summary['completed_by_category'].items():
            if tasks:
                msg += f"• {category}：{', '.join(tasks)}\n"
        msg += "\n"
    
    if summary['incomplete'] > 0:
        msg += "**💪 明日继续**\n"
        for category, tasks in summary['incomplete_by_category'].items():
            if tasks:
                msg += f"• {category}：{len(tasks)}项待办\n"
    
    return msg


def process_user_input(text):
    """
    处理用户输入
    返回：(success, message, category)
    """
    manager = DailyScheduleManager()
    
    # 特殊处理：感悟
    if any(keyword in text for keyword in ['感悟', '今日一句', '名言']):
        # 提取引号内容
        quote_match = re.search(r'[「『""](.+?)[」』""]', text)
        if quote_match:
            quote = quote_match.group(1)
        else:
            # 去除关键词后的内容
            quote = re.sub(r'(感悟|今日一句|名言)[：:]*', '', text).strip()
        
        manager.set_quote(quote)
        return True, f"✅ 已记录今日感悟：\n_{quote}_", '感悟'
    
    # 分类识别
    category, subcategory, is_completion = manager.classify_input(text)
    
    if not category:
        return False, "❓ 我没能识别这条内容的分类，可以明确告诉我是【运动/投资/写作/家庭】吗？", None
    
    if is_completion:
        # 标记任务完成
        success, task = manager.complete_task(category, text)
        if success:
            return True, f"✅ 已记录到【{category}】并标记完成：\n{task}", category
        else:
            return False, f"⚠️ 未找到匹配的{category}任务，已添加为新任务", category
    else:
        # 添加新任务
        success = manager.add_task(category, text)
        if success:
            return True, f"📝 已添加到【{category}】待办", category
        else:
            return False, f"❌ 添加失败", category


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法：")
        print("  python3 daily_schedule_manager.py 'input text'  # 处理输入")
        print("  python3 daily_schedule_manager.py --summary     # 查看摘要")
        print("  python3 daily_schedule_manager.py --reminder    # 查看提醒")
        sys.exit(1)
    
    if sys.argv[1] == '--summary':
        manager = DailyScheduleManager()
        summary = manager.get_summary()
        print(format_daily_summary(summary))
    
    elif sys.argv[1] == '--reminder':
        manager = DailyScheduleManager()
        incomplete = manager.get_incomplete_tasks()
        print(format_reminder(incomplete))
    
    else:
        text = ' '.join(sys.argv[1:])
        success, message, category = process_user_input(text)
        print(message)
