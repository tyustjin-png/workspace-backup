#!/usr/bin/env python3
"""
📡 情报官 V2 - 美股市场情报收集（升级版）
每日运行，抓取：
- 核心标的价格快照
- 财报日历
- 多源新闻聚合（RSS）
- 市场热点（关键词）
"""

import json
import os
import sys
import feedparser
from datetime import datetime, timedelta
import time
import yfinance as yf

WORKSPACE = os.path.expanduser("~/.openclaw/workspace/美股研究")
WATCHLIST_FILE = os.path.join(WORKSPACE, "watchlist.json")
RSS_CONFIG = os.path.join(WORKSPACE, "rss_feeds.json")
NOTIFY_FILE = "/tmp/stock_intel_pending.json"

# ============ RSS 新闻聚合 ============

def load_rss_feeds():
    """加载 RSS 源配置"""
    try:
        with open(RSS_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def fetch_rss_news(url, max_items=3):
    """抓取单个 RSS 源（简化版）"""
    try:
        feed = feedparser.parse(url)
        news = []
        for entry in feed.entries[:max_items]:
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = time.strftime('%m-%d %H:%M', entry.published_parsed)
            
            news.append({
                "title": entry.title,
                "link": entry.link,
                "published": published or "未知",
            })
        return news
    except:
        return []

def translate_title(title):
    """简易标题翻译（关键词替换）"""
    # 常见金融/科技词汇映射
    translations = {
        "stock": "股票", "price": "价格", "market": "市场",
        "AI": "人工智能", "chip": "芯片", "nuclear": "核能",
        "energy": "能源", "earnings": "财报", "revenue": "营收",
        "profit": "利润", "shares": "股价", "investors": "投资者",
        "CEO": "首席执行官", "IPO": "首次公开募股", 
        "merger": "合并", "acquisition": "收购",
        "billion": "十亿美元", "million": "百万美元",
        "drug": "药物", "weight loss": "减肥",
        "uranium": "铀", "reactor": "反应堆",
        "funding": "融资", "launches": "推出",
        "secures": "获得", "challenge": "挑战",
        "fails": "失败", "sinks": "暴跌", "gains": "上涨"
    }
    
    # 简单关键词替换（仅用于辅助理解，不是完整翻译）
    translated = title
    for en, zh in translations.items():
        if en.lower() in title.lower():
            # 保持原标题，只在括号中添加关键词提示
            pass
    
    # 返回原标题（完整翻译需要调用翻译API）
    return title

def aggregate_news_by_keywords(keywords, max_total=30):
    """按关键词聚合新闻"""
    rss_feeds = load_rss_feeds()
    relevant_news = []
    
    keywords_lower = [k.lower() for k in keywords]
    
    for category, sources in rss_feeds.items():
        for source_name, url in sources.items():
            news_list = fetch_rss_news(url, max_items=10)  # 每源增加到10条
            
            for item in news_list:
                title_lower = item['title'].lower()
                if any(kw in title_lower for kw in keywords_lower):
                    relevant_news.append({
                        **item,
                        "source": source_name,
                        "category": category
                    })
                    if len(relevant_news) >= max_total:
                        return relevant_news
    
    return relevant_news

# ============ 原有功能 ============

def load_watchlist():
    with open(WATCHLIST_FILE, "r") as f:
        return json.load(f)

def get_current_price(ticker):
    """获取当前价格"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return round(hist['Close'].iloc[-1], 2)
    except:
        pass
    return None

def get_price_change(ticker):
    """获取价格变动"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) >= 2:
            today = hist['Close'].iloc[-1]
            yesterday = hist['Close'].iloc[-2]
            change_pct = (today - yesterday) / yesterday * 100
            return {
                "price": round(today, 2),
                "change_pct": round(change_pct, 2),
                "emoji": "🟢" if change_pct >= 0 else "🔴"
            }
    except:
        pass
    return None

def get_52w_position(ticker):
    """计算距52周高点的距离"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current = info.get("currentPrice") or info.get("regularMarketPrice")
        high52w = info.get("fiftyTwoWeekHigh")
        
        if current and high52w:
            dist = round((current - high52w) / high52w * 100, 1)
            return dist
    except:
        pass
    return None

def get_earnings_calendar(tickers, days_ahead=14):
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
        except:
            pass
    
    return sorted(upcoming, key=lambda x: x['days_away'])

# ============ 主报告生成 ============

def generate_intelligence_report():
    """生成完整情报简报"""
    watchlist = load_watchlist()
    today = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M")
    
    # 核心标的列表
    core_tickers_dict = {**watchlist.get("芯链", {}), **watchlist.get("能量", {})}
    core_tickers = list(core_tickers_dict.keys())
    
    print(f"📡 情报官 V2 运行中 [{today} {time_str}]")
    print("=" * 60)
    
    # 1. 价格快照
    print("📊 获取价格数据...")
    price_snapshots = []
    for ticker in core_tickers[:8]:  # 前8个核心标的
        data = get_price_change(ticker)
        if data:
            dist_52w = get_52w_position(ticker)
            price_snapshots.append({
                "ticker": ticker,
                "name": core_tickers_dict.get(ticker, ticker),
                **data,
                "dist_52w": dist_52w
            })
        time.sleep(0.2)  # 避免API限流
    
    # 2. 财报日历
    print("📅 检查财报日历...")
    earnings = get_earnings_calendar(core_tickers)
    
    # 3. 新闻聚合（基于观察名单关键词）
    print("📰 聚合相关新闻...")
    keywords = list(core_tickers) + ["AI", "芯片", "核能", "uranium", "nuclear", "chip"]
    news = aggregate_news_by_keywords(keywords, max_total=30)
    
    # 生成报告数据
    report = {
        "date": today,
        "time": time_str,
        "price_snapshots": price_snapshots,
        "earnings": earnings,
        "news": news
    }
    
    # 保存JSON
    report_dir = os.path.join(WORKSPACE, "投资日志")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"{today}_情报V2.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 生成 Telegram 消息
    msg_lines = [
        f"📡 **美股情报简报** `[{today} {time_str}]`",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]
    
    # 价格快照
    if price_snapshots:
        msg_lines.append("**📊 核心标的**")
        for p in price_snapshots:
            sign = "+" if p["change_pct"] >= 0 else ""
            w52_info = f"  52W: {p['dist_52w']:+.0f}%" if p.get('dist_52w') else ""
            msg_lines.append(f"{p['emoji']} `{p['ticker']:5}` ${p['price']:7.2f}  ({sign}{p['change_pct']:.1f}%){w52_info}")
        msg_lines.append("")
    
    # 财报日历
    if earnings:
        msg_lines.append("**📅 即将财报**")
        for e in earnings:
            emoji = "🚨" if e['days_away'] <= 3 else "⚠️"
            msg_lines.append(f"{emoji} `{e['ticker']:5}` {e['days_away']} 天后  ({e['date']})")
        msg_lines.append("")
    else:
        msg_lines.append("**📅 财报日历**: 未来14天无财报")
        msg_lines.append("")
    
    # 新闻摘要
    if news:
        msg_lines.append(f"**📰 重点新闻** ({len(news)} 条)")
        for idx, item in enumerate(news, 1):
            title_short = item['title'][:80] if len(item['title']) > 80 else item['title']
            msg_lines.append(f"{idx}. [{item['category']}] {title_short}")
            msg_lines.append(f"   `{item['source']}` | {item['published']}")
            # 翻译占位符（需要后处理）
            msg_lines.append(f"   🇨🇳 [待翻译]")
        msg_lines.append("")
    
    msg_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    telegram_msg = "\n".join(msg_lines)
    
    # 写入通知文件
    notify_data = {
        "message": telegram_msg,
        "time": time_str,
        "report_file": report_file
    }
    with open(NOTIFY_FILE, "w", encoding="utf-8") as f:
        json.dump(notify_data, f, ensure_ascii=False)
    
    print(telegram_msg)
    print(f"\n✅ 报告已保存: {report_file}")
    print(f"📨 通知文件: {NOTIFY_FILE}")
    print(f"📊 价格快照: {len(price_snapshots)} 个")
    print(f"📅 即将财报: {len(earnings)} 个")
    print(f"📰 相关新闻: {len(news)} 条")
    
    return report

if __name__ == "__main__":
    try:
        generate_intelligence_report()
    except Exception as e:
        print(f"❌ 情报官运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
