#!/usr/bin/env python3
"""
Master Agent - 任务编排和调度
运行在 OpenClaw 环境中，通过 sessions_spawn 和 sessions_send 控制 Worker
"""
import json
import sys
from typing import List, Dict, Any
from task_state import TaskState
from utils import generate_task_id, format_duration
import time


class MasterAgent:
    """Master Agent 负责任务编排"""
    
    def __init__(self, task_description: str):
        self.task_id = generate_task_id()
        self.task_description = task_description
        self.state = TaskState(self.task_id, task_description)
        self.workers = []
        
    def plan(self) -> List[Dict[str, Any]]:
        """任务规划：分解成子任务
        
        Returns:
            子任务列表，格式: [{"worker_type": "search", "input": {...}}, ...]
        """
        print(f"📋 规划任务: {self.task_description}")
        self.state.set_status("planning")
        
        # MVP: 固定的 3 步流水线
        # TODO: 后续可以用 LLM 动态规划
        plan = [
            {
                "worker_type": "search",
                "task": f"搜索问题: {self.task_description}",
                "input": {"query": self.task_description}
            },
            {
                "worker_type": "rewrite",
                "task": "将搜索结果改写成推文",
                "input": {}  # 从上一步获取
            },
            {
                "worker_type": "review",
                "task": "审核推文质量并打分",
                "input": {}  # 从上一步获取
            }
        ]
        
        print(f"✅ 规划完成，共 {len(plan)} 个步骤")
        for i, step in enumerate(plan, 1):
            print(f"  {i}. {step['worker_type']}: {step['task']}")
            
        return plan
        
    def execute_pipeline(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行流水线任务
        
        这个方法会输出 JSON 格式的指令，供外部脚本解析和执行
        因为在 Python 脚本中无法直接调用 OpenClaw 工具
        """
        self.state.set_status("executing")
        
        print("\n" + "="*60)
        print("🚀 开始执行任务流水线")
        print("="*60 + "\n")
        
        # 输出执行计划（JSON 格式）
        execution_plan = {
            "task_id": self.task_id,
            "description": self.task_description,
            "steps": []
        }
        
        for i, step in enumerate(plan, 1):
            step_data = {
                "step": i,
                "worker_type": step["worker_type"],
                "task": step["task"],
                "input": step["input"],
                "depends_on": i - 1 if i > 1 else None  # 依赖上一步
            }
            execution_plan["steps"].append(step_data)
            
        return execution_plan
        
    def generate_worker_prompt(self, worker_type: str, task: str, input_data: Dict[str, Any]) -> str:
        """生成 Worker Agent 的提示词"""
        
        prompts = {
            "search": f"""你是一个专业的搜索助手。

任务: {task}

请使用 web_search 工具搜索相关信息，然后用 web_fetch 获取详细内容。

输出格式（JSON）:
{{
  "status": "success",
  "output": {{
    "answer": "搜索到的答案（200-300字）",
    "sources": ["来源1", "来源2"]
  }}
}}

只输出 JSON，不要额外的解释。""",
            
            "rewrite": f"""你是一个专业的文案撰写助手。

任务: {task}

输入内容将在下一条消息中提供。

请将内容改写成一条吸引人的推文（Twitter/X 风格）：
- 长度 150-280 字符
- 使用 emoji
- 突出关键信息
- 有吸引力

输出格式（JSON）:
{{
  "status": "success",
  "output": {{
    "tweet": "改写后的推文内容"
  }}
}}

只输出 JSON，不要额外的解释。""",
            
            "review": f"""你是一个专业的内容审核助手。

任务: {task}

输入内容将在下一条消息中提供。

请从以下维度评审：
1. 吸引力 (1-10)
2. 准确性 (1-10)
3. 简洁性 (1-10)

输出格式（JSON）:
{{
  "status": "success",
  "output": {{
    "score": 8,
    "feedback": "评审意见（50字以内）",
    "dimensions": {{
      "attraction": 8,
      "accuracy": 9,
      "clarity": 7
    }}
  }}
}}

只输出 JSON，不要额外的解释。"""
        }
        
        return prompts.get(worker_type, "未知任务类型")
        
    def run(self):
        """运行完整流程"""
        start_time = time.time()
        
        # 1. 规划
        plan = self.plan()
        
        # 2. 生成执行计划
        execution_plan = self.execute_pipeline(plan)
        
        # 3. 输出执行计划（供外部脚本使用）
        print("\n📤 执行计划 (JSON):")
        print("="*60)
        print(json.dumps(execution_plan, indent=2, ensure_ascii=False))
        print("="*60)
        
        # 4. 输出 Worker 提示词
        print("\n📝 Worker 提示词:")
        print("="*60)
        for step in plan:
            prompt = self.generate_worker_prompt(
                step["worker_type"],
                step["task"],
                step["input"]
            )
            print(f"\n--- {step['worker_type'].upper()} WORKER ---")
            print(prompt)
            print()
        print("="*60)
        
        duration = time.time() - start_time
        print(f"\n⏱️  规划耗时: {format_duration(duration)}")
        print(f"💾 任务状态已保存: {self.state.state_file}")
        
        return execution_plan


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python master_agent.py <任务描述>")
        print("示例: python master_agent.py '什么是 OpenClaw'")
        sys.exit(1)
        
    task_description = " ".join(sys.argv[1:])
    
    print("╔════════════════════════════════════════════════════════╗")
    print("║         多 Agent 协作系统 - Master Agent v0.1         ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    master = MasterAgent(task_description)
    execution_plan = master.run()
    
    print("\n✅ Master Agent 规划完成")
    print("💡 下一步: 使用 OpenClaw 执行任务（需要在 AI 会话中手动执行）")


if __name__ == "__main__":
    main()
