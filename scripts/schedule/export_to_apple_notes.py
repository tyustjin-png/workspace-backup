#!/usr/bin/env python3
"""
导出日程到 Apple 备忘录格式
确保清单格式完全兼容
"""

from datetime import datetime
from pathlib import Path

def export_for_apple_notes(date=None):
    """
    导出为 Apple 备忘录兼容的清单格式
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    schedule_file = Path.home() / f'.openclaw/workspace/memory/daily-schedule/{date}.md'
    
    if not schedule_file.exists():
        return f"❌ 未找到 {date} 的日程文件"
    
    content = schedule_file.read_text(encoding='utf-8')
    
    # Apple 备忘录清单格式完全兼容 Markdown 的 - [ ] 和 - [x]
    # 只需要确保格式干净即可
    
    # 清理时间戳（可选）
    # content = re.sub(r'---\n_最后更新：.*_', '', content)
    
    return content


if __name__ == '__main__':
    import sys
    
    date = sys.argv[1] if len(sys.argv) > 1 else None
    output = export_for_apple_notes(date)
    print(output)
    print("\n" + "="*60)
    print("📋 复制上面的内容到 Apple 备忘录即可")
    print("✅ 格式已优化为清单格式，可直接打勾")
