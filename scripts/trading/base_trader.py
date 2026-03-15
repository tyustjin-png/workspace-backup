#!/usr/bin/env python3
"""
Base 链交易模块
支持 Uniswap V3 / Aerodrome 自动交易
"""

import json
import os
from web3 import Web3
from eth_account import Account
import requests

# 配置
BASE_RPC = "https://mainnet.base.org"
WALLET_PATH = os.path.expanduser("~/.config/base/trading-bot-key.json")

# Uniswap V3 Router (Base)
UNISWAP_V3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"  # SwapRouter02
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"  # WETH on Base

# 1inch API for Base (用于获取最优路由)
ONEINCH_API = "https://api.1inch.dev/swap/v5.2/8453"  # Base chain ID

class BaseTrader:
    def __init__(self, wallet_path=WALLET_PATH):
        """初始化 Base 交易器"""
        self.w3 = Web3(Web3.HTTPProvider(BASE_RPC))
        
        # 加载钱包
        if os.path.exists(wallet_path):
            with open(wallet_path, 'r') as f:
                wallet_data = json.load(f)
            
            self.private_key = wallet_data.get('private_key')
            self.account = Account.from_key(self.private_key)
            self.address = self.account.address
        else:
            self.private_key = None
            self.account = None
            self.address = None
            print(f"⚠️  钱包文件不存在: {wallet_path}")
    
    def get_balance(self):
        """获取 ETH 余额"""
        if not self.address:
            return 0
        
        try:
            balance_wei = self.w3.eth.get_balance(self.address)
            return self.w3.from_wei(balance_wei, 'ether')
        except:
            return 0
    
    def get_token_balance(self, token_address):
        """获取代币余额"""
        if not self.address:
            return 0
        
        try:
            # ERC20 balanceOf ABI
            abi = [{"constant": True, "inputs": [{"name": "_owner", "type": "address"}], 
                    "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], 
                    "type": "function"}]
            
            contract = self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)
            balance = contract.functions.balanceOf(self.address).call()
            return balance
        except:
            return 0
    
    def get_quote_1inch(self, from_token, to_token, amount_wei):
        """
        使用 1inch API 获取交易报价
        
        Args:
            from_token: 源代币地址 (ETH 用 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE)
            to_token: 目标代币地址
            amount_wei: 金额（wei）
        """
        url = f"{ONEINCH_API}/quote"
        
        params = {
            "src": from_token,
            "dst": to_token,
            "amount": str(amount_wei)
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except:
            pass
        return None
    
    def get_swap_tx_data(self, from_token, to_token, amount_wei, slippage=5.0):
        """
        使用 1inch API 获取 Swap 交易数据
        
        Args:
            from_token: 源代币地址 (ETH 用 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE)
            to_token: 目标代币地址
            amount_wei: 金额（wei）
            slippage: 滑点容忍度（%）
        """
        url = f"{ONEINCH_API}/swap"
        
        params = {
            "src": from_token,
            "dst": to_token,
            "amount": str(amount_wei),
            "from": self.address,
            "slippage": str(slippage),
            "disableEstimate": "false",
            "allowPartialFill": "false"
        }
        
        # 1inch API 需要 API key（免费版限流）
        # 这里使用公开 endpoint（可能有限制）
        
        try:
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"❌ 1inch API 错误: {resp.status_code}")
                print(f"   响应: {resp.text[:200]}")
        except Exception as e:
            print(f"❌ 1inch API 请求失败: {e}")
        
        return None
    
    def swap_eth_for_token(self, token_address, amount_eth, slippage=5.0):
        """
        用 ETH 买入代币
        
        Args:
            token_address: 代币合约地址
            amount_eth: 买入金额（ETH）
            slippage: 滑点容忍度（%）
        """
        if not self.account:
            return {"success": False, "error": "钱包未初始化"}
        
        print(f"\n{'='*60}")
        print(f"🔄 Base 链交易")
        print(f"   代币: {token_address[:12]}...")
        print(f"   金额: {amount_eth} ETH")
        print(f"   滑点: {slippage}%")
        print(f"{'='*60}\n")
        
        # 1. 检查余额
        balance = self.get_balance()
        print(f"💰 钱包余额: {balance:.4f} ETH")
        
        if balance < amount_eth + 0.001:  # 预留 Gas
            return {
                "success": False,
                "error": f"余额不足（需要 {amount_eth + 0.001} ETH）"
            }
        
        # 2. 获取 Swap 交易数据
        print(f"📊 获取交易数据...")
        amount_wei = self.w3.to_wei(amount_eth, 'ether')
        
        # ETH 的特殊地址（1inch 使用）
        eth_address = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        
        # 使用 1inch API
        swap_data = self.get_swap_tx_data(eth_address, token_address, amount_wei, slippage)
        
        if not swap_data:
            print(f"❌ 无法获取交易数据")
            print(f"⚠️  可能原因：")
            print(f"   - 1inch API 限流")
            print(f"   - 代币流动性不足")
            print(f"   - 网络问题")
            return {
                "success": False,
                "error": "无法获取交易数据"
            }
        
        # 3. 执行交易
        print(f"⚡ 执行交易...")
        
        try:
            # 从 1inch 返回的数据中提取交易参数
            tx_data = swap_data.get('tx', {})
            
            if not tx_data:
                print(f"❌ 交易数据格式错误")
                return {
                    "success": False,
                    "error": "交易数据格式错误"
                }
            
            # 构建交易
            tx = {
                'from': self.address,
                'to': tx_data.get('to'),
                'data': tx_data.get('data'),
                'value': int(tx_data.get('value', 0)),
                'gas': int(tx_data.get('gas', 300000)),
                'gasPrice': int(tx_data.get('gasPrice', self.w3.eth.gas_price)),
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'chainId': 8453  # Base Mainnet
            }
            
            # 签名交易
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            
            # 发送交易
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"✅ 交易已发送")
            print(f"   交易哈希: {tx_hash.hex()}")
            
            # 等待确认（可选）
            print(f"⏳ 等待确认...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt['status'] == 1:
                print(f"✅ 交易成功！")
                return {
                    "success": True,
                    "tx_hash": tx_hash.hex(),
                    "block": receipt['blockNumber']
                }
            else:
                print(f"❌ 交易失败")
                return {
                    "success": False,
                    "error": "交易执行失败",
                    "tx_hash": tx_hash.hex()
                }
        
        except Exception as e:
            print(f"❌ 交易执行错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def sell_token(self, token_address, amount_pct=100):
        """
        卖出代币换 ETH
        
        Args:
            token_address: 代币合约地址
            amount_pct: 卖出百分比（0-100）
        """
        if not self.account:
            return {"success": False, "error": "钱包未初始化"}
        
        # 获取持有数量
        balance = self.get_token_balance(token_address)
        
        if balance == 0:
            return {"success": False, "error": "未持有该代币"}
        
        sell_amount = int(balance * amount_pct / 100)
        
        print(f"\n📤 卖出代币")
        print(f"   代币: {token_address[:12]}...")
        print(f"   持有: {balance}")
        print(f"   卖出: {sell_amount} ({amount_pct}%)")
        
        # TODO: 完整实现
        return {
            "success": False,
            "note": "卖出功能待实现",
            "simulated": True
        }

# 创建钱包文件
def create_wallet():
    """生成新的 Base 钱包"""
    import secrets
    
    # 生成随机私钥
    private_key = "0x" + secrets.token_hex(32)
    account = Account.from_key(private_key)
    
    wallet_data = {
        "private_key": private_key,
        "address": account.address,
        "created_at": "2026-02-01"
    }
    
    # 保存
    os.makedirs(os.path.dirname(WALLET_PATH), exist_ok=True)
    with open(WALLET_PATH, 'w') as f:
        json.dump(wallet_data, f, indent=2)
    
    os.chmod(WALLET_PATH, 0o600)
    
    print(f"✅ Base 钱包已创建")
    print(f"📍 地址: {account.address}")
    print(f"🔐 私钥已保存到: {WALLET_PATH}")
    print(f"")
    print(f"⚠️  请向该地址充值 ETH（用于交易和 Gas）")
    
    return account.address

# 导入已有钱包
def import_wallet(private_key):
    """导入已有钱包"""
    try:
        # 验证私钥
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
        
        account = Account.from_key(private_key)
        
        wallet_data = {
            "private_key": private_key,
            "address": account.address,
            "imported_at": "2026-02-01"
        }
        
        # 保存
        os.makedirs(os.path.dirname(WALLET_PATH), exist_ok=True)
        with open(WALLET_PATH, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        
        os.chmod(WALLET_PATH, 0o600)
        
        print(f"✅ 钱包导入成功")
        print(f"📍 地址: {account.address}")
        print(f"🔐 私钥已保存到: {WALLET_PATH}")
        
        return account.address
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return None

if __name__ == "__main__":
    print("🐉 Base 链交易系统\n")
    
    # 测试连接
    trader = BaseTrader()
    
    if trader.account:
        print(f"钱包地址: {trader.address}")
        print(f"ETH 余额: {trader.get_balance():.4f}")
    else:
        print("钱包未配置")
        print("")
        print("使用方法：")
        print("  python base_trader.py create    # 创建新钱包")
        print("  python base_trader.py import <private_key>  # 导入钱包")
