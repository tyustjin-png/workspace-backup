#!/usr/bin/env python3
"""
📡 情报官 V3 - 美股市场情报收集（带中文翻译）
每日运行，抓取：
- 核心标的价格快照
- 财报日历
- 多源新闻聚合（RSS + 中文翻译）
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

# ============ 翻译功能 ============

def translate_text(text, max_retries=2):
    """翻译文本到中文（使用 googletrans）"""
    try:
        from googletrans import Translator
        translator = Translator()
        
        for attempt in range(max_retries):
            try:
                result = translator.translate(text, dest='zh-cn')
                return result.text
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return f"[翻译失败: {str(e)[:20]}]"
    except ImportError:
        return "[googletrans未安装]"

# ============ RSS 新闻聚合 ============

def load_rss_feeds():
    """加载 RSS 源配置"""
    try:
        with open(RSS_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def fetch_rss_news(url, max_items=8):
    """抓取单个 RSS 源"""
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

def aggregate_news_by_keywords(keywords, max_total=30):
    """按关键词聚合新闻并翻译"""
    rss_feeds = load_rss_feeds()
    relevant_news = []
    
    keywords_lower = [k.lower() for k in keywords]
    
    print("📰 聚合并翻译新闻...")
    
    for category, sources in rss_feeds.items():
        for source_name, url in sources.items():
            news_list = fetch_rss_news(url, max_items=8)
            
            for item in news_list:
                title_lower = item['title'].lower()
                if any(kw in title_lower for kw in keywords_lower):
                    # 翻译标题
                    title_zh = translate_text(item['title'])
                    
                    relevant_news.append({
                        **item,
                        "title_zh": title_zh,
                        "source": source_name,
                        "category": category
                    })
                    
                    print(f"  ✅ {source_name}: {item['title'][:50]}...")
                    
                    if len(relevant_news) >= max_total:
                        break
            
            if len(relevant_news) >= max_total:
                break
        
        if len(relevant_news) >= max_total:
            break
    
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
    
    print(f"📡 情报官 V3 运行中 [{today} {time_str}]")
    print("=" * 60)
    
    # 1. 价格快照
    print("📊 获取价格数据...")
    price_snapshots = []
    for ticker in core_tickers[:8]:
        data = get_price_change(ticker)
        if data:
            dist_52w = get_52w_position(ticker)
            price_snapshots.append({
                "ticker": ticker,
                "name": core_tickers_dict.get(ticker, ticker),
                **data,
                "dist_52w": dist_52w
            })
        time.sleep(1)  # 增加延迟避免限流
    
    # 2. 财报日历
    print("📅 检查财报日历...")
    earnings = get_earnings_calendar(core_tickers)
    
    # 3. 新闻聚合 + 翻译
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
    report_file = os.path.join(report_dir, f"{today}_情报V3.json")
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
    
    # 新闻摘要（带翻译）
    if news:
        msg_lines.append(f"**📰 重点新闻** ({len(news)} 条)")
        for idx, item in enumerate(news, 1):
            msg_lines.append(f"{idx}. [{item['category']}] {item['title'][:70]}...")
            msg_lines.append(f"   🇨🇳 {item.get('title_zh', '翻译中...')}")
            msg_lines.append(f"   `{item['source']}` | {item['published']}")
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
    print(f"📰 相关新闻: {len(news)} 条（含中文翻译）")
    
    return report

if __name__ == "__main__":
    try:
        generate_intelligence_report()
    except Exception as e:
        print(f"❌ 情报官运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
