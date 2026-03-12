#!/usr/bin/env python3
"""
状态中心 - 共享状态管理
功能：
  - 统一状态存储
  - 状态变更自动联动
  - 状态查询接口
"""

import json
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
STATE_FILE = WORKSPACE / "infra" / "system_state.json"
CHANGE_LOG = WORKSPACE / "infra" / "state_changes.jsonl"

STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def get_default_state():
    """默认状态结构"""
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "date": today,
        "daily_tasks": {
            "xiaoding": {"status": "pending", "completed_at": None, "details": {}},
            "schedule_10": {"status": "pending", "sent_at": None},
            "schedule_15": {"status": "pending", "sent_at": None},
            "schedule_19": {"status": "pending", "sent_at": None},
            "daily_summary": {"status": "pending", "sent_at": None},
            "audit": {"status": "pending", "completed_at": None}
        },
        "schedule": {
            "completed": [],
            "pending": []
        },
        "notifications": {
            "sent_count": 0,
            "last_sent_at": None
        },
        "last_updated": datetime.now().isoformat()
    }


def load_state():
    """加载状态"""
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
        # 如果是新的一天，重置状态
        today = datetime.now().strftime("%Y-%m-%d")
        if state.get("date") != today:
            state = get_default_state()
            save_state(state)
        return state
    return get_default_state()


def save_state(state):
    """保存状态"""
    state["last_updated"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def log_change(path: str, old_value, new_value, trigger: str):
    """记录状态变更"""
    entry = {
        "ts": datetime.now().isoformat(),
        "path": path,
        "old": old_value,
        "new": new_value,
        "trigger": trigger
    }
    with open(CHANGE_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_nested(state: dict, path: str):
    """获取嵌套路径的值"""
    keys = path.split(".")
    value = state
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value


def set_nested(state: dict, path: str, value):
    """设置嵌套路径的值"""
    keys = path.split(".")
    current = state
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def update(path: str, value, trigger: str = "unknown") -> dict:
    """
    更新状态
    
    Args:
        path: 状态路径，如 "daily_tasks.xiaoding.status"
        value: 新值
        trigger: 触发者标识
    
    Returns:
        {"success": bool, "old": any, "new": any}
    """
    state = load_state()
    old_value = get_nested(state, path)
    set_nested(state, path, value)
    save_state(state)
    log_change(path, old_value, value, trigger)
    
    # 触发联动（如果需要）
    handle_side_effects(path, value, trigger)
    
    return {"success": True, "old": old_value, "new": value}


def get(path: str = None):
    """
    获取状态
    
    Args:
        path: 状态路径，None则返回全部
    """
    state = load_state()
    if path is None:
        return state
    return get_nested(state, path)


def handle_side_effects(path: str, value, trigger: str):
    """
    处理状态变更的联动效果
    """
    # 定投完成 → 更新日程
    if path == "daily_tasks.xiaoding.status" and value == "completed":
        sync_schedule_from_xiaoding(trigger)


def sync_schedule_from_xiaoding(trigger: str):
    """
    定投完成后同步日程
    """
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "/root/.openclaw/workspace/daily_schedule_manager.py", "定投相关完成"],
            capture_output=True,
            text=True,
            cwd="/root/.openclaw/workspace"
        )
        log_change(
            "schedule.sync_from_xiaoding", 
            "pending", 
            "synced" if result.returncode == 0 else "failed",
            trigger
        )
    except Exception as e:
        log_change("schedule.sync_from_xiaoding", "pending", f"error:{str(e)}", trigger)


def mark_task_completed(task_name: str, details: dict = None, trigger: str = "unknown"):
    """
    标记任务完成的便捷方法
    """
    now = datetime.now().isoformat()
    update(f"daily_tasks.{task_name}.status", "completed", trigger)
    update(f"daily_tasks.{task_name}.completed_at", now, trigger)
    if details:
        update(f"daily_tasks.{task_name}.details", details, trigger)


def mark_notification_sent(task_name: str, trigger: str = "unknown"):
    """
    标记通知已发送
    """
    now = datetime.now().isoformat()
    update(f"daily_tasks.{task_name}.status", "sent", trigger)
    update(f"daily_tasks.{task_name}.sent_at", now, trigger)
    
    # 更新通知统计
    state = load_state()
    count = state.get("notifications", {}).get("sent_count", 0) + 1
    update("notifications.sent_count", count, trigger)
    update("notifications.last_sent_at", now, trigger)


def get_pending_tasks() -> list:
    """获取待完成任务列表"""
    state = load_state()
    pending = []
    for task_name, task_data in state.get("daily_tasks", {}).items():
        if task_data.get("status") == "pending":
            pending.append(task_name)
    return pending


def get_completed_tasks() -> list:
    """获取已完成任务列表"""
    state = load_state()
    completed = []
    for task_name, task_data in state.get("daily_tasks", {}).items():
        if task_data.get("status") in ["completed", "sent"]:
            completed.append(task_name)
    return completed


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 state_center.py get [path]")
        print("  python3 state_center.py update <path> <value> [trigger]")
        print("  python3 state_center.py pending")
        print("  python3 state_center.py completed")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "get":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        result = get(path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "update":
        if len(sys.argv) < 4:
            print("错误: update 需要 path 和 value 参数")
            sys.exit(1)
        path = sys.argv[2]
        value = sys.argv[3]
        trigger = sys.argv[4] if len(sys.argv) > 4 else "cli"
        result = update(path, value, trigger)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "pending":
        print(json.dumps(get_pending_tasks(), ensure_ascii=False))
    
    elif cmd == "completed":
        print(json.dumps(get_completed_tasks(), ensure_ascii=False))
    
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
