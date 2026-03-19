#!/usr/bin/env python3
"""简易计算器 - 支持加减乘除和历史记录"""

import json
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / "calc_history.json"

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def calculate(expression):
    """解析并计算表达式，如 '3 + 5' """
    parts = expression.strip().split()
    if len(parts) != 3:
        raise ValueError("格式错误，请输入如: 3 + 5")
    
    a, op, b = parts
    a = float(a)
    b = float(b)
    
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    else:
        raise ValueError(f"不支持的运算符: {op}")

def show_stats(history):
    """显示历史统计"""
    if not history:
        print("暂无历史记录")
        return
    
    results = [h['result'] for h in history if h['result'] is not None]
    if not results:
        print("暂无有效计算结果")
        return
    print(f"计算次数: {len(results)}")
    print(f"最大结果: {max(results)}")
    print(f"最小结果: {min(results)}")
    print(f"平均结果: {sum(results) / len(results)}")

def main():
    history = load_history()
    print("简易计算器 (输入 q 退出, stats 查看统计)")
    
    while True:
        expr = input("\n> ")
        if expr.lower() == 'q':
            save_history(history)
            break
        elif expr.lower() == 'stats':
            show_stats(history)
            continue
        
        try:
            result = calculate(expr)
            print(f"= {result}")
            history.append({"expression": expr, "result": result})
        except Exception as e:
            print(f"错误: {e}")
            history.append({"expression": expr, "result": None})

if __name__ == "__main__":
    main()
