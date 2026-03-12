#!/usr/bin/env python3
"""
工具函数模块
"""
import time
import hashlib


def generate_task_id() -> str:
    """生成唯一任务 ID"""
    timestamp = str(time.time())
    return f"task-{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"


def format_duration(seconds: float) -> str:
    """格式化时长"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        return f"{seconds/60:.1f}分钟"
    else:
        return f"{seconds/3600:.1f}小时"
