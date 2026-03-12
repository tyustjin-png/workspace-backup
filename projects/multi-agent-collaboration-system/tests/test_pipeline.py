#!/usr/bin/env python3
"""
端到端测试脚本
测试 3-Agent 流水线
"""
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from master_agent import MasterAgent


def test_basic_pipeline():
    """测试基本流水线"""
    print("="*70)
    print("测试用例: 基本 3-Agent 流水线")
    print("="*70 + "\n")
    
    task = "什么是 OpenClaw"
    master = MasterAgent(task)
    
    # 运行规划
    execution_plan = master.run()
    
    # 验证
    assert execution_plan["task_id"].startswith("task-")
    assert len(execution_plan["steps"]) == 3
    assert execution_plan["steps"][0]["worker_type"] == "search"
    assert execution_plan["steps"][1]["worker_type"] == "rewrite"
    assert execution_plan["steps"][2]["worker_type"] == "review"
    
    print("\n✅ 测试通过")
    

if __name__ == "__main__":
    test_basic_pipeline()
