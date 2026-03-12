#!/usr/bin/env python3
"""
自动技能提取器
从每日日志中提取可复用的技能
"""

import json
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"

def extract_skills_from_daily_log(date: str = None) -> str:
    """
    分析每日日志，提取潜在技能
    返回提取提示（供 LLM 处理）
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    log_file = MEMORY_DIR / f"{date}.md"
    
    if not log_file.exists():
        return f"❌ 日志文件不存在: {log_file}"
    
    # 读取日志内容
    with open(log_file, "r", encoding="utf-8") as f:
        log_content = f.read()
    
    # 生成提取提示
    prompt = f"""# 技能提取任务

分析以下每日日志，识别可复用的技能（Reusable Skills）。

## 识别标准
1. **可复用性**: 这个解决方案以后可能再次使用
2. **明确步骤**: 操作步骤清晰，可以标准化
3. **价值性**: 节省时间或避免错误

## 日志内容
```markdown
{log_content}
```

## 提取格式
对于每个识别到的技能，输出 JSON：

```json
{{
  "name": "技能名称",
  "description": "简短描述这个技能是做什么的",
  "category": "工具使用|问题诊断|数据处理|通信协作|系统维护",
  "trigger_conditions": [
    "什么时候应该用这个技能？（至少3个场景）"
  ],
  "execution_steps": [
    "具体步骤1",
    "具体步骤2",
    "..."
  ],
  "examples": [
    {{
      "scenario": "具体场景",
      "command": "执行的命令或操作",
      "result": "预期结果"
    }}
  ],
  "notes": "补充说明"
}}
```

## 输出
如果没有识别到新技能，输出：
```
NO_SKILLS_FOUND
```

如果识别到技能，输出每个技能的 JSON（一行一个）。
"""
    
    return prompt


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "prompt":
            # 只输出提取提示
            print(extract_skills_from_daily_log())
        else:
            # 指定日期
            print(extract_skills_from_daily_log(sys.argv[1]))
    else:
        print(extract_skills_from_daily_log())


if __name__ == "__main__":
    main()
