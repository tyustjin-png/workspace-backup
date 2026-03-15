#!/usr/bin/env python3
"""
日程推送脚本 - 由 cron 直接调用，不依赖 heartbeat
"""
import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
MESSAGE_FILE = Path("/tmp/schedule_message.txt")
STATE_FILE = WORKSPACE / "heartbeat_state.json"

def main():
    # 检查消息文件是否存在
    if not MESSAGE_FILE.exists() or MESSAGE_FILE.stat().st_size == 0:
        print("❌ 消息文件不存在或为空")
        sys.exit(1)
    
    # 读取消息内容
    message = MESSAGE_FILE.read_text(encoding="utf-8").strip()
    
    # 获取当前小时
    hour = datetime.now().hour
    hour_key = f"schedule_{hour:02d}"
    
    # 检查状态文件，避免重复推送
    try:
        state = json.loads(STATE_FILE.read_text())
        if state.get("sent", {}).get(hour_key, False):
            print(f"✅ {hour_key} 已推送过，跳过")
            sys.exit(0)
    except:
        state = {"date": datetime.now().strftime("%Y-%m-%d"), "sent": {}}
    
    # 推送消息（写入待推送队列，让主 session 发送）
    queue_file = Path("/tmp/message_queue.jsonl")
    queue_item = {
        "type": "schedule_reminder",
        "hour": hour,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    with queue_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(queue_item, ensure_ascii=False) + "\n")
    
    # 更新状态
    state["sent"][hour_key] = True
    state[f"{hour_key}_pushed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    
    print(f"✅ {hour_key} 已加入推送队列")

if __name__ == "__main__":
    main()
