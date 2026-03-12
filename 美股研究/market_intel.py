#!/usr/bin/env python3
"""
📡 情报官 - 美股市场情报收集
每日运行，抓取关键标的新闻和财报日历
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta
import yfinance as yf

WORKSPACE = os.path.expanduser("~/.openclaw/workspace/美股研究")
WATCHLIST_FILE = os.path.join(WORKSPACE, "watchlist.json")
NOTIFY_FILE = "/tmp/stock_intel_pending.json"

def load_watchlist():
    with open(WATCHLIST_FILE, "r") as f:
        return json.load(f)

def get_stock_news(ticker, max_news=3):
    """获取股票最新新闻"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:max_news] if stock.news else []
        result = []
        for item in news:
            result.append({
                "title": item.get("title", ""),
                "publisher": item.get("publisher", ""),
                "link": item.get("link", ""),
                "time": datetime.fromtimestamp(item.get("providerPublishTime", 0)).strftime("%m-%d %H:%M")
            })
        return result
    except Exception as e:
        return []

def get_earnings_calendar(tickers, days_ahead=7):
    """获取未来N天内的财报日期"""
    upcoming = []
    today = datetime.now().date()
    deadline = today + timedelta(days=days_ahead)
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            calendar = stock.calendar
            if calendar is not None and not calendar.empty:
                earnings_date = calendar.iloc[0].get("Earnings Date")
                if earnings_date:
                    ed = earnings_date.date() if hasattr(earnings_date, 'date') else earnings_date
                    if today <= ed <= deadline:
                        upcoming.append({
                            "ticker": ticker,
                            "date": str(ed),
                            "days_away": (ed - today).days
                        })
        except Exception:
            pass
    return upcoming

def get_price_snapshot(tickers):
    """获取价格快照"""
    snapshots = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                today_close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = (today_close - prev_close) / prev_close * 100
                snapshots.append({
                    "ticker": ticker,
                    "price": round(today_close, 2),
                    "change_pct": round(change_pct, 2),
                    "emoji": "🟢" if change_pct >= 0 else "🔴"
                })
        except Exception:
            pass
    return snapshots

def generate_report():
    """生成每日情报简报"""
    watchlist = load_watchlist()
    today = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M")
    
    # 核心标的列表
    core_tickers = list(watchlist.get("芯链", {}).keys()) + list(watchlist.get("能量", {}).keys())
    
    report = {
        "date": today,
        "time": time_str,
        "price_snapshots": [],
        "earnings": [],
        "highlights": []
    }
    
    print(f"🔍 情报官运行中 [{today} {time_str}]")
    print("=" * 50)
    
    # 价格快照
    print("📊 获取价格数据...")
    prices = get_price_snapshot(core_tickers[:6])  # 前6个核心标的
    report["price_snapshots"] = prices
    
    # 财报日历
    print("📅 检查财报日历...")
    earnings = get_earnings_calendar(core_tickers)
    report["earnings"] = earnings
    
    # 写入报告文件
    report_dir = os.path.join(WORKSPACE, "投资日志")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"{today}_情报.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 生成 Telegram 消息
    msg_lines = [f"📡 **美股情报简报** [{today}]", "━━━━━━━━━━━━━━━━━━━━"]
    
    if prices:
        msg_lines.append("**📊 价格快照**")
        for p in prices:
            sign = "+" if p["change_pct"] >= 0 else ""
            msg_lines.append(f"{p['emoji']} `{p['ticker']}` ${p['price']}  ({sign}{p['change_pct']}%)")
    
    if earnings:
        msg_lines.append("\n**📅 即将财报**")
        for e in earnings:
            msg_lines.append(f"⚠️ `{e['ticker']}` 财报在 {e['days_away']} 天后 ({e['date']})")
    
    if not earnings:
        msg_lines.append("\n✅ 未来7天内无财报")
    
    msg_lines.append("━━━━━━━━━━━━━━━━━━━━")
    
    telegram_msg = "\n".join(msg_lines)
    
    # 写入通知文件
    notify_data = {"message": telegram_msg, "time": time_str}
    with open(NOTIFY_FILE, "w", encoding="utf-8") as f:
        json.dump(notify_data, f, ensure_ascii=False)
    
    print(telegram_msg)
    print(f"\n✅ 报告已保存: {report_file}")
    print(f"📨 通知文件: {NOTIFY_FILE}")
    return telegram_msg

if __name__ == "__main__":
    try:
        generate_report()
    except Exception as e:
        print(f"❌ 情报官运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
