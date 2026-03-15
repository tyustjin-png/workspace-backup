#!/usr/bin/env python3
"""测试币安API连接"""
import json
import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode

def test_binance_api():
    # 读取配置
    with open('/Users/qianzhao/.openclaw/workspace/xiaoding/config/binance_auto_buy.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['api_key']
    api_secret = config['api_secret']
    
    base_url = 'https://api.binance.com'
    
    print("🔍 测试币安API连接...")
    print(f"📌 API Key: {api_key[:8]}...{api_key[-8:]}")
    print()
    
    # 测试1: 检查服务器时间
    print("1️⃣ 测试服务器连接...")
    try:
        response = requests.get(f'{base_url}/api/v3/time')
        if response.status_code == 200:
            print(f"   ✅ 服务器连接正常")
            server_time = response.json()['serverTime']
            print(f"   📅 服务器时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(server_time/1000))}")
        else:
            print(f"   ❌ 连接失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return
    
    print()
    
    # 测试2: 检查账户信息（需要签名）
    print("2️⃣ 测试API认证...")
    try:
        timestamp = int(time.time() * 1000)
        params = {'timestamp': timestamp}
        query_string = urlencode(params)
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {'X-MBX-APIKEY': api_key}
        url = f'{base_url}/api/v3/account?{query_string}&signature={signature}'
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            account = response.json()
            print(f"   ✅ API认证成功")
            print(f"   📊 账户类型: SPOT")
            print(f"   💰 资产统计:")
            
            # 显示非零余额
            non_zero_balances = [b for b in account['balances'] 
                               if float(b['free']) > 0 or float(b['locked']) > 0]
            
            if non_zero_balances:
                for balance in non_zero_balances[:5]:  # 最多显示5个
                    asset = balance['asset']
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    if free > 0 or locked > 0:
                        print(f"      • {asset}: {free:.8f} (可用) + {locked:.8f} (冻结)")
            else:
                print(f"      • 暂无资产")
                
        elif response.status_code == 401:
            print(f"   ❌ API认证失败")
            print(f"   💡 可能原因:")
            print(f"      1. API Key或Secret错误")
            print(f"      2. IP白名单未配置或配置错误")
            print(f"      3. API权限不足")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 认证失败: {e}")
        return
    
    print()
    
    # 测试3: 检查交易对信息
    print("3️⃣ 测试交易对信息...")
    try:
        symbol = config.get('symbol', 'BTCUSDT')
        response = requests.get(f'{base_url}/api/v3/ticker/price?symbol={symbol}')
        
        if response.status_code == 200:
            price_info = response.json()
            print(f"   ✅ 交易对 {symbol} 可用")
            print(f"   💵 当前价格: ${float(price_info['price']):,.2f}")
        else:
            print(f"   ❌ 交易对查询失败")
            
    except Exception as e:
        print(f"   ❌ 查询失败: {e}")
    
    print()
    print("=" * 50)
    print("✅ 测试完成！")

if __name__ == '__main__':
    test_binance_api()
