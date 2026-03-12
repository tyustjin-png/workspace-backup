#!/usr/bin/env python3
"""
📊 分析师 - 美股个股深度研究
用法: python3 stock_analyst.py NVDA
      python3 stock_analyst.py CEG --full
"""

import json
import os
import sys
import argparse
from datetime import datetime
import yfinance as yf

WORKSPACE = os.path.expanduser("~/.openclaw/workspace/美股研究")

def get_sector(ticker):
    """根据watchlist判断板块"""
    try:
        with open(os.path.join(WORKSPACE, "watchlist.json")) as f:
            wl = json.load(f)
        for sector, stocks in wl.items():
            if ticker.upper() in stocks:
                return sector
    except:
        pass
    return "未知"

def analyze_stock(ticker, full=False):
    """分析单个股票"""
    ticker = ticker.upper()
    print(f"\n📊 开始分析 {ticker}...")
    print("=" * 60)
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 基本信息
        name = info.get("longName", ticker)
        sector = info.get("sector", get_sector(ticker))
        industry = info.get("industry", "")
        
        # 财务数据
        market_cap = info.get("marketCap", 0)
        market_cap_b = round(market_cap / 1e9, 1) if market_cap else 0
        
        pe_ttm = info.get("trailingPE")
        pe_fwd = info.get("forwardPE")
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        target_price = info.get("targetMeanPrice")
        
        revenue_growth = info.get("revenueGrowth")
        profit_margin = info.get("profitMargins")
        
        week52_high = info.get("fiftyTwoWeekHigh")
        week52_low = info.get("fiftyTwoWeekLow")
        
        analyst_rating = info.get("recommendationKey", "").upper()
        num_analysts = info.get("numberOfAnalystOpinions", 0)
        
        # 计算距52周高点距离
        dist_from_high = None
        if price and week52_high:
            dist_from_high = round((price - week52_high) / week52_high * 100, 1)
        
        # 计算上行空间
        upside = None
        if price and target_price:
            upside = round((target_price - price) / price * 100, 1)
        
        # 获取历史价格
        hist = stock.history(period="1y")
        ytd_return = None
        if len(hist) > 0:
            year_ago_price = hist['Close'].iloc[0]
            current_price = hist['Close'].iloc[-1]
            ytd_return = round((current_price - year_ago_price) / year_ago_price * 100, 1)
        
        # 打印报告
        print(f"🏢 {name} ({ticker})")
        print(f"板块: {sector} | 行业: {industry}")
        print("-" * 60)
        
        print(f"\n💰 估值")
        print(f"  市值:       ${market_cap_b}B")
        if price:          print(f"  当前价格:   ${price}")
        if pe_ttm:         print(f"  PE (TTM):   {round(pe_ttm, 1)}x")
        if pe_fwd:         print(f"  PE (Fwd):   {round(pe_fwd, 1)}x")
        if target_price:   print(f"  分析师目标: ${target_price} (上行空间 {upside}%)")
        
        print(f"\n📈 表现")
        if week52_high:    print(f"  52周高:     ${week52_high} (当前距高点 {dist_from_high}%)")
        if week52_low:     print(f"  52周低:     ${week52_low}")
        if ytd_return is not None: print(f"  1年回报:    {'+' if ytd_return >= 0 else ''}{ytd_return}%")
        
        print(f"\n📊 基本面")
        if revenue_growth: print(f"  营收增速:   {round(revenue_growth*100, 1)}%")
        if profit_margin:  print(f"  净利润率:   {round(profit_margin*100, 1)}%")
        
        print(f"\n🎯 分析师评级")
        print(f"  评级: {analyst_rating} (基于{num_analysts}位分析师)")
        
        # 获取最新新闻
        if full:
            print(f"\n📰 最新新闻")
            try:
                news = stock.news[:5]
                for item in news:
                    pub_time = datetime.fromtimestamp(item.get("providerPublishTime", 0))
                    print(f"  [{pub_time.strftime('%m-%d')}] {item.get('title', '')}")
                    print(f"           来源: {item.get('publisher', '')} | {item.get('link', '')[:60]}...")
            except:
                print("  无法获取新闻")
        
        # 财报日历
        try:
            calendar = stock.calendar
            if calendar is not None and not calendar.empty:
                earnings_date = calendar.iloc[0].get("Earnings Date")
                if earnings_date:
                    print(f"\n📅 下次财报: {earnings_date}")
        except:
            pass
        
        # 生成结构化报告
        report = {
            "ticker": ticker,
            "name": name,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "price": price,
            "market_cap_b": market_cap_b,
            "pe_ttm": pe_ttm,
            "pe_fwd": pe_fwd,
            "target_price": target_price,
            "upside_pct": upside,
            "revenue_growth_pct": round(revenue_growth*100, 1) if revenue_growth else None,
            "profit_margin_pct": round(profit_margin*100, 1) if profit_margin else None,
            "week52_high": week52_high,
            "week52_low": week52_low,
            "dist_from_high_pct": dist_from_high,
            "ytd_return_pct": ytd_return,
            "analyst_rating": analyst_rating,
            "num_analysts": num_analysts
        }
        
        # 保存报告
        sector_dir_map = get_sector(ticker)
        report_dir = os.path.join(WORKSPACE, "标的研究", sector_dir_map if sector_dir_map != "未知" else "其他")
        os.makedirs(report_dir, exist_ok=True)
        report_file = os.path.join(report_dir, f"{ticker}_数据_{datetime.now().strftime('%Y%m%d')}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据已保存: {report_file}")
        return report
        
    except Exception as e:
        print(f"❌ 分析 {ticker} 出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_portfolio():
    """分析完整观察名单"""
    try:
        with open(os.path.join(WORKSPACE, "watchlist.json")) as f:
            watchlist = json.load(f)
    except:
        print("❌ 无法读取 watchlist.json")
        return
    
    print(f"\n📊 完整观察名单分析 [{datetime.now().strftime('%Y-%m-%d')}]")
    print("=" * 60)
    
    for sector, stocks in watchlist.items():
        if sector in ["ETF", "IPO跟踪"]:
            continue
        print(f"\n📁 {sector}")
        for ticker in stocks.keys():
            analyze_stock(ticker)
            print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="美股个股分析师")
    parser.add_argument("ticker", nargs="?", help="股票代码，如 NVDA")
    parser.add_argument("--full", action="store_true", help="完整分析（含新闻）")
    parser.add_argument("--all", action="store_true", help="分析全部观察名单")
    
    args = parser.parse_args()
    
    if args.all:
        analyze_portfolio()
    elif args.ticker:
        analyze_stock(args.ticker, full=args.full)
    else:
        print("用法:")
        print("  python3 stock_analyst.py NVDA          # 分析NVDA")
        print("  python3 stock_analyst.py CEG --full    # 完整分析CEG（含新闻）")
        print("  python3 stock_analyst.py --all         # 分析全部观察名单")
