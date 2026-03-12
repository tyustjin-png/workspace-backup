#!/usr/bin/env python3
"""
创建 Solana 交易钱包
"""

import json
import os
from solders.keypair import Keypair

WALLET_PATH = os.path.expanduser("~/.config/solana/trading-bot.json")

def create_wallet():
    """生成新钱包"""
    # 创建目录
    os.makedirs(os.path.dirname(WALLET_PATH), exist_ok=True)
    
    # 生成密钥对
    keypair = Keypair()
    
    # 保存为 JSON 格式（Solana CLI 兼容）
    keypair_bytes = list(bytes(keypair))
    
    with open(WALLET_PATH, 'w') as f:
        json.dump(keypair_bytes, f)
    
    # 设置权限（仅所有者可读）
    os.chmod(WALLET_PATH, 0o600)
    
    # 显示地址
    print(f"✅ 钱包已创建")
    print(f"📍 路径: {WALLET_PATH}")
    print(f"💳 地址: {keypair.pubkey()}")
    print(f"")
    print(f"⚠️  请保管好私钥文件！")
    print(f"⚠️  向该地址充值 SOL 才能开始交易")
    
    return str(keypair.pubkey())

if __name__ == "__main__":
    create_wallet()
