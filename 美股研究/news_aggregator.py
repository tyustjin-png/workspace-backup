#!/usr/bin/env python3
"""
📰 新闻聚合器 - RSS 多源新闻抓取
用法: python3 news_aggregator.py [keywords]
"""

import json
import os
import sys
import feedparser
from datetime import datetime, timedelta
import time

WORKSPACE = os.path.expanduser("~/.openclaw/workspace/美股研究")
RSS_CONFIG = os.path.join(WORKSPACE, "rss_feeds.json")

def load_rss_feeds():
    """加载 RSS 源配置"""
    with open(RSS_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_rss_news(url, max_items=5, timeout=10):
    """抓取单个 RSS 源"""
    try:
        feed = feedparser.parse(url)
        news = []
        for entry in feed.entries[:max_items]:
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = time.strftime('%Y-%m-%d %H:%M', entry.published_parsed)
            elif hasattr(entry, 'published'):
                published = entry.published
            
            news.append({
                "title": entry.title,
                "link": entry.link,
                "published": published or "未知时间",
                "summary": entry.summary[:200] if hasattr(entry, 'summary') else ""
            })
        return news
    except Exception as e:
        print(f"  ⚠️ 抓取失败: {url} - {e}")
        return []

def filter_by_keywords(news_list, keywords):
    """根据关键词过滤新闻"""
    if not keywords:
        return news_list
    
    filtered = []
    keywords_lower = [k.lower() for k in keywords]
    
    for news in news_list:
        title_lower = news['title'].lower()
        summary_lower = news.get('summary', '').lower()
        
        if any(kw in title_lower or kw in summary_lower for kw in keywords_lower):
            filtered.append(news)
    
    return filtered

def aggregate_news(categories=None, keywords=None, max_per_source=3):
    """聚合多源新闻"""
    rss_feeds = load_rss_feeds()
    all_news = {}
    
    if categories:
        # 只抓取指定类别
        feeds_to_fetch = {cat: rss_feeds[cat] for cat in categories if cat in rss_feeds}
    else:
        feeds_to_fetch = rss_feeds
    
    print(f"📰 新闻聚合器运行中 [{datetime.now().strftime('%Y-%m-%d %H:%M')}]")
    print("=" * 60)
    
    for category, sources in feeds_to_fetch.items():
        print(f"\n📁 {category}")
        category_news = []
        
        for source_name, url in sources.items():
            print(f"  🔍 {source_name}...", end=" ")
            news = fetch_rss_news(url, max_items=max_per_source)
            
            if keywords:
                news = filter_by_keywords(news, keywords)
            
            if news:
                category_news.extend([{**item, "source": source_name} for item in news])
                print(f"✅ {len(news)} 条")
            else:
                print("⚠️ 无相关新闻")
        
        all_news[category] = category_news
    
    return all_news

def generate_news_report(keywords=None, hours=24):
    """生成新闻简报"""
    news_data = aggregate_news(keywords=keywords)
    
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "keywords": keywords or [],
        "news": news_data
    }
    
    # 保存报告
    report_dir = os.path.join(WORKSPACE, "投资日志")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"{report['date']}_新闻聚合.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: {report_file}")
    
    # 生成 Markdown 摘要
    md_lines = [f"# 📰 新闻聚合 [{report['date']} {report['time']}]", ""]
    
    if keywords:
        md_lines.append(f"**关键词**: {', '.join(keywords)}")
        md_lines.append("")
    
    total_count = sum(len(items) for items in news_data.values())
    md_lines.append(f"**共抓取**: {total_count} 条新闻")
    md_lines.append("")
    
    for category, news_list in news_data.items():
        if not news_list:
            continue
        
        md_lines.append(f"## {category}")
        md_lines.append("")
        
        for item in news_list[:10]:  # 每类最多显示10条
            md_lines.append(f"### [{item['source']}] {item['title']}")
            md_lines.append(f"🕒 {item['published']}")
            md_lines.append(f"🔗 {item['link']}")
            if item.get('summary'):
                md_lines.append(f"> {item['summary'][:150]}...")
            md_lines.append("")
    
    md_content = "\n".join(md_lines)
    
    md_file = os.path.join(report_dir, f"{report['date']}_新闻聚合.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"✅ Markdown 已保存: {md_file}")
    print(f"\n📊 共抓取 {total_count} 条新闻")
    
    return report

if __name__ == "__main__":
    # 从命令行参数获取关键词
    keywords = sys.argv[1:] if len(sys.argv) > 1 else None
    
    if keywords:
        print(f"🔍 关键词过滤: {', '.join(keywords)}")
    
    generate_news_report(keywords=keywords)
