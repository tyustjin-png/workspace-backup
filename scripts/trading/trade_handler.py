#!/usr/bin/env python3
"""
交易处理器 - 处理用户的买入指令
"""

import json
import sys
from datetime import datetime
from auto_trader import AutoTrader

PENDING_FILE = "/root/.openclaw/workspace/pending_trades.json"

def load_pending():
    """加载待处理交易"""
    try:
        with open(PENDING_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"pending": [], "history": []}

def save_pending(data):
    """保存待处理交易"""
    with open(PENDING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_pending_trade(contract, token_name, amount_sol, recommendation):
    """添加待处理交易"""
    data = load_pending()
    
    trade = {
        "id": len(data["pending"]) + 1,
        "contract": contract,
        "token_name": token_name,
        "amount_sol": amount_sol,
        "recommendation": recommendation,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }
    
    data["pending"].append(trade)
    save_pending(data)
    return trade["id"]

def execute_trade(trade_id, user_confirmed=True):
    """执行交易"""
    data = load_pending()
    
    # 查找交易
    trade = None
    for t in data["pending"]:
        if t["id"] == trade_id:
            trade = t
            break
    
    if not trade:
        return {"success": False, "error": "Trade not found"}
    
    if not user_confirmed:
        # 取消交易
        data["pending"].remove(trade)
        trade["status"] = "cancelled"
        data["history"].append(trade)
        save_pending(data)
        return {"success": True, "action": "cancelled"}
    
    # 执行买入
    trader = AutoTrader()
    result = trader.buy_token(trade["contract"], trade["amount_sol"])
    
    # 更新状态
    data["pending"].remove(trade)
    trade["status"] = "executed" if result.get("success") else "failed"
    trade["result"] = result
    trade["executed_at"] = datetime.now().isoformat()
    data["history"].append(trade)
    save_pending(data)
    
    return result

def get_pending_trades():
    """获取所有待处理交易"""
    data = load_pending()
    return data["pending"]

# 命令行接口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trade_handler.py <command> [args]")
        print("Commands:")
        print("  list              - 列出待处理交易")
        print("  execute <id>      - 执行交易")
        print("  cancel <id>       - 取消交易")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        trades = get_pending_trades()
        if not trades:
            print("暂无待处理交易")
        else:
            for t in trades:
                print(f"#{t['id']}: {t['token_name']} - {t['amount_sol']} SOL - {t['recommendation']}")
    
    elif command == "execute" and len(sys.argv) > 2:
        trade_id = int(sys.argv[2])
        result = execute_trade(trade_id, True)
        print(json.dumps(result, indent=2))
    
    elif command == "cancel" and len(sys.argv) > 2:
        trade_id = int(sys.argv[2])
        result = execute_trade(trade_id, False)
        print(json.dumps(result, indent=2))
