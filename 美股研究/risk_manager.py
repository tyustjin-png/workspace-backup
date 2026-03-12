#!/usr/bin/env python3
"""
🛡️ 风控官 - 美股持仓风险管理
功能：持仓监控、风险评估、止损/止盈提醒
用法: python3 risk_manager.py check       # 检查所有持仓
      python3 risk_manager.py add         # 添加持仓（交互）
      python3 risk_manager.py summary     # 持仓总览
"""

import json
import os
import sys
import requests
from datetime import datetime
import yfinance as yf

WORKSPACE = os.path.expanduser("~/.openclaw/workspace/美股研究")
PORTFOLIO_FILE = os.path.join(WORKSPACE, "持仓追踪/portfolio.json")
NOTIFY_FILE = "/tmp/stock_risk_alert.json"

# 默认风控参数（可在持仓中覆盖）
DEFAULT_STOP_LOSS_PCT = -20.0     # 止损：-20%
DEFAULT_TAKE_PROFIT_PCT = 50.0    # 止盈提醒：+50%
MAX_SINGLE_POSITION_PCT = 25.0    # 单只最大仓位 25%

def load_portfolio():
    """加载持仓数据"""
    os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
    try:
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    except:
        default = {
            "positions": [],
            "total_capital": 0,
            "currency": "USD",
            "last_updated": ""
        }
        save_portfolio(default)
        return default

def save_portfolio(data):
    """保存持仓数据"""
    data["last_updated"] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_current_price(ticker):
    """获取当前价格"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return round(hist['Close'].iloc[-1], 4)
    except:
        pass
    return None

def check_positions():
    """检查所有持仓，评估风险"""
    portfolio = load_portfolio()
    positions = portfolio.get("positions", [])
    total_capital = portfolio.get("total_capital", 0)
    
    if not positions:
        print("📭 当前无美股持仓")
        return []
    
    alerts = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"\n🛡️ 风控检查 [{now}]")
    print("=" * 60)
    
    total_value = 0
    total_pnl = 0
    
    for pos in positions:
        if pos.get("status") != "holding":
            continue
        
        ticker = pos["ticker"]
        shares = pos["shares"]
        buy_price = pos["buy_price"]
        stop_loss = pos.get("stop_loss_pct", DEFAULT_STOP_LOSS_PCT)
        take_profit = pos.get("take_profit_pct", DEFAULT_TAKE_PROFIT_PCT)
        
        current_price = get_current_price(ticker)
        
        if current_price is None:
            print(f"⚠️ {ticker}: 无法获取价格")
            continue
        
        cost = buy_price * shares
        current_value = current_price * shares
        pnl = current_value - cost
        pnl_pct = (current_price - buy_price) / buy_price * 100
        
        total_value += current_value
        total_pnl += pnl
        
        # 仓位占比
        position_pct = (current_value / total_capital * 100) if total_capital > 0 else 0
        
        status_emoji = "🟢" if pnl_pct >= 0 else "🔴"
        print(f"\n{status_emoji} {ticker}")
        print(f"   买入: ${buy_price} × {shares}股 = ${cost:.0f}")
        print(f"   现价: ${current_price} | 盈亏: {'+' if pnl_pct >= 0 else ''}{pnl_pct:.1f}% (${pnl:+.0f})")
        print(f"   仓位: {position_pct:.1f}% | 止损: {stop_loss}% | 止盈提醒: +{take_profit}%")
        
        # 风险警报
        if pnl_pct <= stop_loss:
            alert = {
                "level": "CRITICAL",
                "ticker": ticker,
                "type": "STOP_LOSS",
                "message": f"🚨 {ticker} 触发止损！当前亏损 {pnl_pct:.1f}% (止损线 {stop_loss}%)",
                "current_price": current_price,
                "pnl_pct": pnl_pct
            }
            alerts.append(alert)
            print(f"   🚨 止损触发！建议立即处理")
        
        elif pnl_pct >= take_profit:
            alert = {
                "level": "WARNING",
                "ticker": ticker,
                "type": "TAKE_PROFIT",
                "message": f"💰 {ticker} 达到止盈提醒！当前盈利 {pnl_pct:.1f}% (目标 +{take_profit}%)",
                "current_price": current_price,
                "pnl_pct": pnl_pct
            }
            alerts.append(alert)
            print(f"   💰 止盈提醒！考虑部分获利了结")
        
        # 仓位过重警告
        if position_pct > MAX_SINGLE_POSITION_PCT:
            alert = {
                "level": "WARNING",
                "ticker": ticker,
                "type": "OVERWEIGHT",
                "message": f"⚖️ {ticker} 仓位过重！当前 {position_pct:.1f}% (上限 {MAX_SINGLE_POSITION_PCT}%)",
                "position_pct": position_pct
            }
            alerts.append(alert)
            print(f"   ⚖️ 仓位过重警告！")
    
    # 汇总
    print(f"\n{'='*60}")
    print(f"💼 持仓汇总")
    print(f"   总市值: ${total_value:.0f}")
    print(f"   总盈亏: ${total_pnl:+.0f} ({'+' if total_pnl >= 0 else ''}{total_pnl/total_capital*100:.1f}%)" if total_capital > 0 else f"   总盈亏: ${total_pnl:+.0f}")
    print(f"   警报数: {len(alerts)}")
    
    # 写入警报文件
    if alerts:
        notify_data = {
            "time": datetime.now().isoformat(),
            "alerts": alerts,
            "summary": f"共 {len(alerts)} 条风险警报"
        }
        with open(NOTIFY_FILE, "w") as f:
            json.dump(notify_data, f, ensure_ascii=False, indent=2)
        print(f"\n⚠️ 风险警报已写入: {NOTIFY_FILE}")
    else:
        print(f"\n✅ 所有持仓正常，无风险警报")
        # 清理旧警报文件
        if os.path.exists(NOTIFY_FILE):
            os.remove(NOTIFY_FILE)
    
    return alerts

def add_position_interactive():
    """交互式添加持仓"""
    print("📥 添加美股持仓")
    print("-" * 40)
    
    ticker = input("股票代码 (如 NVDA): ").strip().upper()
    shares = float(input("购买股数: ").strip())
    buy_price = float(input("买入均价 ($): ").strip())
    stop_loss = float(input(f"止损线 (默认 {DEFAULT_STOP_LOSS_PCT}%，直接回车用默认): ").strip() or DEFAULT_STOP_LOSS_PCT)
    take_profit = float(input(f"止盈提醒 (默认 +{DEFAULT_TAKE_PROFIT_PCT}%，直接回车用默认): ").strip() or DEFAULT_TAKE_PROFIT_PCT)
    
    portfolio = load_portfolio()
    
    position = {
        "ticker": ticker,
        "shares": shares,
        "buy_price": buy_price,
        "buy_date": datetime.now().strftime("%Y-%m-%d"),
        "stop_loss_pct": stop_loss,
        "take_profit_pct": take_profit,
        "status": "holding",
        "notes": ""
    }
    
    # 更新总资金
    cost = shares * buy_price
    portfolio["total_capital"] = portfolio.get("total_capital", 0) + cost
    portfolio["positions"].append(position)
    
    save_portfolio(portfolio)
    print(f"\n✅ 已添加持仓: {ticker} {shares}股 @ ${buy_price} (总成本 ${cost:.0f})")

def portfolio_summary():
    """持仓总览"""
    portfolio = load_portfolio()
    positions = [p for p in portfolio.get("positions", []) if p.get("status") == "holding"]
    
    if not positions:
        print("📭 当前无持仓")
        return
    
    print(f"\n💼 持仓总览 [{datetime.now().strftime('%Y-%m-%d')}]")
    print(f"{'标的':8} {'股数':6} {'买入价':8} {'现价':8} {'盈亏%':8} {'仓位':6}")
    print("-" * 55)
    
    total_cost = sum(p["shares"] * p["buy_price"] for p in positions)
    total_value = 0
    
    for pos in positions:
        ticker = pos["ticker"]
        shares = pos["shares"]
        buy_price = pos["buy_price"]
        current_price = get_current_price(ticker) or buy_price
        cost = shares * buy_price
        value = shares * current_price
        total_value += value
        pnl_pct = (current_price - buy_price) / buy_price * 100
        position_pct = value / total_cost * 100 if total_cost > 0 else 0
        
        emoji = "🟢" if pnl_pct >= 0 else "🔴"
        print(f"{emoji}{ticker:7} {shares:6.1f} ${buy_price:7.2f} ${current_price:7.2f} {pnl_pct:+7.1f}% {position_pct:5.1f}%")
    
    print("-" * 55)
    total_pnl_pct = (total_value - total_cost) / total_cost * 100 if total_cost > 0 else 0
    print(f"{'合计':8} {'':6} {'':8} ${total_value:7.0f} {total_pnl_pct:+7.1f}%  100%")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    
    if cmd == "check":
        check_positions()
    elif cmd == "add":
        add_position_interactive()
    elif cmd == "summary":
        portfolio_summary()
    else:
        print("用法:")
        print("  python3 risk_manager.py check    # 检查所有持仓")
        print("  python3 risk_manager.py add      # 添加持仓")
        print("  python3 risk_manager.py summary  # 持仓总览")
