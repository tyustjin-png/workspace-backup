#!/usr/bin/env python3
"""
任务状态管理模块
"""
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path


class TaskState:
    """任务状态管理"""
    
    def __init__(self, task_id: str, description: str):
        self.task_id = task_id
        self.description = description
        self.status = "idle"  # idle/planning/executing/aggregating/done/error
        self.created_at = time.time()
        self.updated_at = time.time()
        self.steps: List[Dict[str, Any]] = []
        self.error_message: Optional[str] = None
        
        # 文件路径
        self.state_dir = Path(__file__).parent.parent / "states"
        self.state_dir.mkdir(exist_ok=True)
        self.state_file = self.state_dir / f"{task_id}.json"
        
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "event_log.jsonl"
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "steps": self.steps,
            "error_message": self.error_message
        }
        
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.task_id = data["task_id"]
        self.description = data["description"]
        self.status = data["status"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.steps = data["steps"]
        self.error_message = data.get("error_message")
        
    def save(self):
        """保存状态到文件"""
        self.updated_at = time.time()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
    def load(self) -> bool:
        """从文件加载状态"""
        if not self.state_file.exists():
            return False
        with open(self.state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.from_dict(data)
        return True
        
    def log_event(self, event: str, data: Dict[str, Any]):
        """记录事件到日志"""
        event_data = {
            "timestamp": time.time(),
            "task_id": self.task_id,
            "event": event,
            "data": data
        }
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event_data, ensure_ascii=False) + '\n')
            
    def add_step(self, step_num: int, worker_type: str, session_key: str):
        """添加步骤"""
        step = {
            "step": step_num,
            "worker_type": worker_type,
            "session_key": session_key,
            "status": "pending",
            "output": None,
            "error": None,
            "started_at": time.time(),
            "completed_at": None
        }
        self.steps.append(step)
        self.save()
        self.log_event("step_added", step)
        
    def update_step(self, step_num: int, status: str, output: Any = None, error: str = None):
        """更新步骤状态"""
        for step in self.steps:
            if step["step"] == step_num:
                step["status"] = status
                step["output"] = output
                step["error"] = error
                if status in ["done", "error"]:
                    step["completed_at"] = time.time()
                break
        self.save()
        self.log_event("step_updated", {
            "step": step_num,
            "status": status,
            "has_output": output is not None,
            "has_error": error is not None
        })
        
    def set_status(self, status: str, error_message: str = None):
        """设置任务状态"""
        self.status = status
        if error_message:
            self.error_message = error_message
        self.save()
        self.log_event("status_changed", {
            "status": status,
            "error_message": error_message
        })
        
    def get_step_output(self, step_num: int) -> Optional[Any]:
        """获取步骤输出"""
        for step in self.steps:
            if step["step"] == step_num:
                return step.get("output")
        return None
