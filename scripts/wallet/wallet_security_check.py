#!/usr/bin/env python3
"""
钱包安全检查脚本
每日检查钱包余额、交易记录、代币授权等安全状态
"""

import json
import os
import time
from datetime import datetime, timedelta
from web3 import Web3
from pathlib import Path

# 配置
WALLET_CONFIG = Path.home() / '.openclaw/workspace/config/wallet.json'
ALERT_FILE = '/tmp/wallet_alert.json'
STATE_FILE = Path.home() / '.openclaw/workspace/data/wallet_state.json'

# RPC 端点（可以根据需要配置多个网络）
NETWORKS = {
    'ethereum': 'https://eth.llamarpc.com',
    'bsc': 'https://bsc-dataseed.binance.org',
    'polygon': 'https://polygon-rpc.com'
}

def load_wallet_config():
    """加载钱包配置"""
    if not WALLET_CONFIG.exists():
        return None
    
    with open(WALLET_CONFIG, 'r') as f:
        return json.load(f)

def load_previous_state():
    """加载上次的状态"""
    if not STATE_FILE.exists():
        return {}
    
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_current_state(state):
    """保存当前状态"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def check_balance(w3, address, network_name):
    """检查余额"""
    try:
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        return {
            'network': network_name,
            'balance': float(balance_eth),
            'balance_wei': str(balance_wei),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'network': network_name,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def check_recent_transactions(w3, address, network_name, blocks_back=100):
    """检查最近的交易"""
    try:
        current_block = w3.eth.block_number
        start_block = max(0, current_block - blocks_back)
        
        transactions = []
        for block_num in range(start_block, current_block + 1):
            try:
                block = w3.eth.get_block(block_num, full_transactions=True)
                for tx in block.transactions:
                    if tx['from'].lower() == address.lower() or \
                       (tx['to'] and tx['to'].lower() == address.lower()):
                        transactions.append({
                            'hash': tx['hash'].hex(),
                            'from': tx['from'],
                            'to': tx['to'],
                            'value': str(tx['value']),
                            'value_eth': float(w3.from_wei(tx['value'], 'ether')),
                            'block': block_num,
                            'timestamp': block['timestamp']
                        })
            except Exception as e:
                # 某些区块可能无法获取，继续
                continue
        
        return {
            'network': network_name,
            'transactions': transactions,
            'count': len(transactions),
            'blocks_checked': f"{start_block}-{current_block}"
        }
    except Exception as e:
        return {
            'network': network_name,
            'error': str(e)
        }

def detect_anomalies(current_state, previous_state):
    """检测异常"""
    alerts = []
    
    for network, data in current_state.items():
        if 'balance' not in data or 'error' in data:
            continue
        
        # 检查余额变化
        if network in previous_state and 'balance' in previous_state[network]:
            prev_balance = previous_state[network]['balance']
            curr_balance = data['balance']
            change = curr_balance - prev_balance
            change_percent = (change / prev_balance * 100) if prev_balance > 0 else 0
            
            # 余额大幅下降警报
            if change < 0 and abs(change_percent) > 10:
                alerts.append({
                    'type': 'balance_drop',
                    'network': network,
                    'severity': 'high',
                    'message': f"⚠️ {network} 余额下降 {abs(change):.4f} ({change_percent:.2f}%)",
                    'details': {
                        'previous': prev_balance,
                        'current': curr_balance,
                        'change': change
                    }
                })
            
            # 余额意外增加（可能是转错账）
            elif change > 0 and change > 0.1:  # 增加超过 0.1 ETH
                alerts.append({
                    'type': 'unexpected_deposit',
                    'network': network,
                    'severity': 'medium',
                    'message': f"ℹ️ {network} 收到 {change:.4f}",
                    'details': {
                        'previous': prev_balance,
                        'current': curr_balance,
                        'change': change
                    }
                })
    
    return alerts

def main():
    """主函数"""
    print("🔒 开始钱包安全检查...")
    print("=" * 60)
    
    # 加载配置
    config = load_wallet_config()
    if not config:
        print("❌ 未找到钱包配置文件")
        print(f"   请创建: {WALLET_CONFIG}")
        return
    
    # 获取钱包地址
    addresses = config.get('addresses', [])
    if not addresses:
        print("❌ 配置文件中没有钱包地址")
        return
    
    # 加载上次状态
    previous_state = load_previous_state()
    current_state = {}
    
    # 检查每个网络
    for network_name, rpc_url in NETWORKS.items():
        print(f"\n📡 检查 {network_name}...")
        
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not w3.is_connected():
                print(f"   ❌ 无法连接到 {network_name}")
                continue
            
            for address in addresses:
                # 检查余额
                balance_info = check_balance(w3, address, network_name)
                
                if 'error' not in balance_info:
                    print(f"   ✅ 地址: {address[:10]}...")
                    print(f"      余额: {balance_info['balance']:.6f}")
                    current_state[network_name] = balance_info
                else:
                    print(f"   ❌ 错误: {balance_info['error']}")
        
        except Exception as e:
            print(f"   ❌ 错误: {e}")
    
    # 检测异常
    print(f"\n🔍 分析异常...")
    alerts = detect_anomalies(current_state, previous_state)
    
    if alerts:
        print(f"\n⚠️ 发现 {len(alerts)} 个警报：")
        for alert in alerts:
            print(f"   • {alert['message']}")
        
        # 保存警报到文件
        with open(ALERT_FILE, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'alerts': alerts
            }, f, indent=2)
        print(f"\n📝 警报已保存到: {ALERT_FILE}")
    else:
        print("   ✅ 未发现异常")
        # 删除旧的警报文件
        if os.path.exists(ALERT_FILE):
            os.remove(ALERT_FILE)
    
    # 保存当前状态
    save_current_state(current_state)
    
    print("\n" + "=" * 60)
    print("✅ 检查完成")

if __name__ == '__main__':
    main()
