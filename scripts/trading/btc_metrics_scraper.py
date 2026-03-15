#!/usr/bin/env python3
"""
免费获取 Bitcoin 链上指标数据
- MVRV Z-Score（简化版）
- RHODL-like 指标（简化版）
"""

import requests
import json
from datetime import datetime, timedelta
import pandas as pd

# ==================== 数据源 ====================

def get_blockchain_info_data():
    """从 Blockchain.info 获取基础数据"""
    
    # 1. Market Cap（市值）
    market_cap_url = "https://api.blockchain.info/charts/market-cap"
    params = {"timespan": "365days", "format": "json"}
    
    try:
        resp = requests.get(market_cap_url, params=params, timeout=15)
        market_cap_data = resp.json()
        
        # 2. Total Bitcoins（流通量）
        total_btc_url = "https://api.blockchain.info/charts/total-bitcoins"
        resp2 = requests.get(total_btc_url, params=params, timeout=15)
        total_btc_data = resp2.json()
        
        # 3. Hash Rate（算力 - 可选）
        hash_rate_url = "https://api.blockchain.info/charts/hash-rate"
        resp3 = requests.get(hash_rate_url, params=params, timeout=15)
        hash_rate_data = resp3.json()
        
        return {
            "market_cap": market_cap_data['values'],
            "total_btc": total_btc_data['values'],
            "hash_rate": hash_rate_data['values']
        }
    except Exception as e:
        print(f"❌ 获取 Blockchain.info 数据失败: {e}")
        return None

def get_coingecko_price_history():
    """从 CoinGecko 获取价格历史（用于计算移动平均）"""
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "365",
        "interval": "daily"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        
        prices = []
        for item in data['prices']:
            timestamp_ms = item[0]
            price = item[1]
            date = datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d')
            prices.append({"date": date, "price": price})
        
        return prices
    except Exception as e:
        print(f"❌ 获取 CoinGecko 数据失败: {e}")
        return None

def get_alternative_me_fear_greed():
    """从 Alternative.me 获取 Fear & Greed Index（额外指标）"""
    url = "https://api.alternative.me/fng/?limit=365"
    
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        fng_data = []
        for item in data['data']:
            fng_data.append({
                "date": datetime.fromtimestamp(int(item['timestamp'])).strftime('%Y-%m-%d'),
                "value": int(item['value']),
                "classification": item['value_classification']
            })
        
        return fng_data
    except Exception as e:
        print(f"❌ 获取 Fear & Greed 数据失败: {e}")
        return None

# ==================== 指标计算 ====================

def calculate_simplified_mvrv_z(prices_df):
    """
    简化版 MVRV Z-Score
    
    用 200 日移动平均作为 Realized Price 的替代
    """
    df = prices_df.copy()
    
    # 计算 200 日移动平均
    df['ma_200'] = df['price'].rolling(window=200).mean()
    
    # 简化 MVRV = Price / MA200
    df['simplified_mvrv'] = df['price'] / df['ma_200']
    
    # 计算 Z-Score（标准化）
    mvrv_mean = df['simplified_mvrv'].mean()
    mvrv_std = df['simplified_mvrv'].std()
    df['mvrv_z_score'] = (df['simplified_mvrv'] - mvrv_mean) / mvrv_std
    
    return df

def calculate_rhodl_proxy(market_cap_data, hash_rate_data):
    """
    RHODL 替代指标
    
    使用算力变化作为"持币时间"的代理指标
    算力上升 = 长期持有者增加
    """
    
    # 将数据转换为 DataFrame
    df = pd.DataFrame(market_cap_data)
    df['timestamp'] = pd.to_datetime(df['x'], unit='s')
    df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    df['market_cap'] = df['y']
    
    # 算力数据
    hr_df = pd.DataFrame(hash_rate_data)
    hr_df['timestamp'] = pd.to_datetime(hr_df['x'], unit='s')
    hr_df['date'] = hr_df['timestamp'].dt.strftime('%Y-%m-%d')
    hr_df['hash_rate'] = hr_df['y']
    
    # 合并
    merged = pd.merge(df, hr_df[['date', 'hash_rate']], on='date', how='left')
    
    # 计算算力变化（7日 vs 365日）
    merged['hash_rate_7d'] = merged['hash_rate'].rolling(window=7).mean()
    merged['hash_rate_365d'] = merged['hash_rate'].rolling(window=365).mean()
    
    # RHODL Proxy = 短期算力 / 长期算力
    # 比值高 = 网络快速扩张 = 更多新参与者
    merged['rhodl_proxy'] = merged['hash_rate_7d'] / merged['hash_rate_365d']
    
    return merged

# ==================== 主函数 ====================

def fetch_all_data():
    """获取所有数据并保存为 CSV"""
    
    print("🔍 开始获取数据...")
    print("="*60)
    
    # 1. 获取价格历史
    print("\n📊 获取价格历史（CoinGecko）...")
    prices = get_coingecko_price_history()
    if not prices:
        print("❌ 价格数据获取失败")
        return
    
    prices_df = pd.DataFrame(prices)
    print(f"✅ 获取 {len(prices_df)} 天的价格数据")
    
    # 2. 计算简化 MVRV Z-Score
    print("\n📈 计算 MVRV Z-Score（简化版）...")
    mvrv_df = calculate_simplified_mvrv_z(prices_df)
    print(f"✅ 计算完成")
    
    # 3. 获取 Blockchain.info 数据
    print("\n📊 获取 Blockchain.info 数据...")
    blockchain_data = get_blockchain_info_data()
    if not blockchain_data:
        print("❌ Blockchain.info 数据获取失败")
        return
    
    print(f"✅ 获取市值、流通量、算力数据")
    
    # 4. 计算 RHODL Proxy
    print("\n📈 计算 RHODL Proxy...")
    rhodl_df = calculate_rhodl_proxy(
        blockchain_data['market_cap'],
        blockchain_data['hash_rate']
    )
    print(f"✅ 计算完成")
    
    # 5. 获取 Fear & Greed Index
    print("\n😱 获取 Fear & Greed Index...")
    fng_data = get_alternative_me_fear_greed()
    if fng_data:
        fng_df = pd.DataFrame(fng_data)
        print(f"✅ 获取 {len(fng_df)} 天的 F&G 数据")
    else:
        fng_df = None
    
    # 6. 合并所有数据
    print("\n🔗 合并所有数据...")
    
    # 准备最终数据集
    final_df = mvrv_df[['date', 'price', 'ma_200', 'simplified_mvrv', 'mvrv_z_score']].copy()
    
    # 合并 RHODL Proxy
    rhodl_subset = rhodl_df[['date', 'market_cap', 'hash_rate', 'rhodl_proxy']]
    final_df = pd.merge(final_df, rhodl_subset, on='date', how='left')
    
    # 合并 Fear & Greed
    if fng_df is not None:
        fng_subset = fng_df[['date', 'value']].rename(columns={'value': 'fear_greed_index'})
        final_df = pd.merge(final_df, fng_subset, on='date', how='left')
    
    # 7. 保存为 CSV
    output_file = "/Users/qianzhao/.openclaw/workspace/btc_metrics_history.csv"
    final_df.to_csv(output_file, index=False)
    
    print(f"\n✅ 数据已保存到: {output_file}")
    print(f"   总行数: {len(final_df)}")
    print(f"   日期范围: {final_df['date'].min()} 至 {final_df['date'].max()}")
    
    # 8. 显示最近数据
    print(f"\n📊 最近 5 天的数据：")
    print("="*60)
    latest = final_df.tail(5)
    for _, row in latest.iterrows():
        print(f"日期: {row['date']}")
        print(f"  价格: ${row['price']:,.2f}")
        print(f"  MVRV Z-Score: {row['mvrv_z_score']:.2f}")
        print(f"  RHODL Proxy: {row['rhodl_proxy']:.2f}" if pd.notna(row['rhodl_proxy']) else "  RHODL Proxy: N/A")
        if 'fear_greed_index' in row and pd.notna(row['fear_greed_index']):
            print(f"  Fear & Greed: {row['fear_greed_index']:.0f}")
        print("")
    
    # 9. 生成信号
    latest_row = final_df.iloc[-1]
    print("🎯 当前市场信号：")
    print("="*60)
    
    mvrv_z = latest_row['mvrv_z_score']
    if mvrv_z > 7:
        signal = "🔴 极度过热（历史顶部区域）"
    elif mvrv_z > 4:
        signal = "🟠 过热（考虑获利）"
    elif mvrv_z > 2:
        signal = "🟡 偏热（谨慎）"
    elif mvrv_z < 0:
        signal = "🟢 低估（买入机会）"
    else:
        signal = "⚪ 中性"
    
    print(f"MVRV Z-Score: {mvrv_z:.2f} - {signal}")
    
    if pd.notna(latest_row.get('rhodl_proxy')):
        rhodl = latest_row['rhodl_proxy']
        if rhodl > 1.2:
            rhodl_signal = "⬆️ 网络快速扩张（新参与者增加）"
        elif rhodl < 0.8:
            rhodl_signal = "⬇️ 网络收缩（长期持有增加）"
        else:
            rhodl_signal = "➡️ 平稳"
        
        print(f"RHODL Proxy: {rhodl:.2f} - {rhodl_signal}")
    
    print("\n✅ 完成！")
    
    return final_df

if __name__ == "__main__":
    try:
        df = fetch_all_data()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
