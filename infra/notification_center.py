#!/usr/bin/env python3
"""
通知中心 - 统一推送出口
功能：
  - 统一推送接口
  - 防重复推送
  - 推送日志记录
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
STATE_FILE = WORKSPACE / "infra" / "notification_state.json"
LOG_FILE = WORKSPACE / "infra" / "notification_log.jsonl"

STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_state():
    """加载通知状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"sent_today": [], "date": ""}


def save_state(state):
    """保存通知状态"""
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def reset_if_new_day(state):
    """如果是新的一天，重置状态"""
    today = datetime.now().strftime("%Y-%m-%d")
    if state.get("date") != today:
        state = {"sent_today": [], "date": today}
        save_state(state)
    return state


def get_message_hash(message: str, category: str) -> str:
    """生成消息哈希，用于去重"""
    content = f"{category}:{message[:100]}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def log_notification(category: str, message: str, status: str, dedupe_key: str = None):
    """记录通知日志"""
    log_entry = {
        "ts": datetime.now().isoformat(),
        "category": category,
        "message_preview": message[:100],
        "status": status,
        "dedupe_key": dedupe_key
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def should_send(category: str, message: str, force: bool = False) -> tuple:
    """
    判断是否应该发送
    返回: (should_send: bool, reason: str, dedupe_key: str)
    """
    if force:
        return True, "forced", None
    
    state = load_state()
    state = reset_if_new_day(state)
    
    dedupe_key = get_message_hash(message, category)
    
    if dedupe_key in state["sent_today"]:
        return False, "duplicate", dedupe_key
    
    return True, "new", dedupe_key


def mark_sent(dedupe_key: str):
    """标记消息已发送"""
    state = load_state()
    state = reset_if_new_day(state)
    if dedupe_key not in state["sent_today"]:
        state["sent_today"].append(dedupe_key)
        save_state(state)


def notify(category: str, message: str, force: bool = False) -> dict:
    """
    统一通知接口
    
    Args:
        category: 通知类别 (xiaoding, schedule, alert, audit, etc.)
        message: 通知内容
        force: 强制发送（忽略去重）
    
    Returns:
        {"success": bool, "reason": str}
    """
    # 检查是否应该发送
    should, reason, dedupe_key = should_send(category, message, force)
    
    if not should:
        log_notification(category, message, f"skipped:{reason}", dedupe_key)
        return {"success": False, "reason": reason}
    
    # 这里返回消息内容，由调用者（主Agent）实际发送
    # 通知中心只负责去重和日志，不负责实际推送
    # 实际推送由主Agent通过message工具完成
    
    if dedupe_key:
        mark_sent(dedupe_key)
    
    log_notification(category, message, "prepared", dedupe_key)
    
    return {
        "success": True, 
        "reason": "prepared",
        "message": message,
        "category": category,
        "dedupe_key": dedupe_key
    }


def get_pending_notifications() -> list:
    """获取今日已准备但可能未送达的通知（用于审计）"""
    if not LOG_FILE.exists():
        return []
    
    today = datetime.now().strftime("%Y-%m-%d")
    pending = []
    
    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry["ts"].startswith(today) and entry["status"] == "prepared":
                    pending.append(entry)
            except:
                continue
    
    return pending


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python3 notification_center.py <category> <message>")
        print("示例: python3 notification_center.py schedule '📋 日程汇报...'")
        sys.exit(1)
    
    category = sys.argv[1]
    message = sys.argv[2]
    
    result = notify(category, message)
    print(json.dumps(result, ensure_ascii=False, indent=2))
