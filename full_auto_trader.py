#!/usr/bin/env python3
"""
全自动交易系统 - 无需确认，自动买入
"""

import json
import requests
import os
from datetime import datetime, timedelta
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import transfer, TransferParams
from solders.rpc.responses import SendTransactionResp
import base58

# ==================== 配置 ====================
WALLET_PATH = os.path.expanduser("~/.config/solana/trading-bot.json")
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
JUPITER_API = "https://public.jupiterapi.com"

# 风控参数
MAX_PER_TRADE = 1.0  # 单笔最多 1 SOL
DAILY_LIMIT = 3.0    # 每日最多 3 SOL
MIN_SCORE = 70       # 最低评分（优化后更容易达到）
MIN_LIQUIDITY = 10000  # 最低流动性 $10K（降低门槛）
STOP_LOSS_PCT = -0.50  # -50% 止损
TAKE_PROFIT_BREAKEVEN = 1.00  # +100% 卖出 50% 回本，剩余继续持有（无止盈）

# 交易记录文件
TRADE_LOG = "/root/.openclaw/workspace/trade_history.json"

# ==================== 钱包管理 ====================
class Wallet:
    def __init__(self):
        with open(WALLET_PATH, 'r') as f:
            keypair_bytes = json.load(f)
        self.keypair = Keypair.from_bytes(bytes(keypair_bytes))
        self.pubkey = self.keypair.pubkey()
    
    def get_address(self):
        return str(self.pubkey)
    
    def get_balance(self):
        """获取 SOL 余额"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [str(self.pubkey)]
            }
            resp = requests.post(SOLANA_RPC, json=payload, timeout=10)
            data = resp.json()
            lamports = data.get('result', {}).get('value', 0)
            return lamports / 1e9
        except:
            return 0

# ==================== 交易记录 ====================
class TradeLogger:
    def __init__(self):
        self.log_file = TRADE_LOG
    
    def load_history(self):
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except:
            return {"trades": [], "daily_total": {}}
    
    def save_history(self, data):
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_trade(self, trade):
        data = self.load_history()
        data["trades"].append(trade)
        
        # 更新每日总额
        today = datetime.now().strftime("%Y-%m-%d")
        data["daily_total"][today] = data["daily_total"].get(today, 0) + trade.get("amount_sol", 0)
        
        self.save_history(data)
    
    def get_today_total(self):
        """获取今日已用额度"""
        data = self.load_history()
        today = datetime.now().strftime("%Y-%m-%d")
        return data["daily_total"].get(today, 0)
    
    def can_trade(self, amount):
        """检查是否可以交易"""
        today_total = self.get_today_total()
        
        if amount > MAX_PER_TRADE:
            return False, f"超过单笔限额 {MAX_PER_TRADE} SOL"
        
        if today_total + amount > DAILY_LIMIT:
            return False, f"超过每日限额 {DAILY_LIMIT} SOL（已用 {today_total:.2f}）"
        
        return True, "OK"

# ==================== Jupiter 交易 ====================
class JupiterTrader:
    def __init__(self, wallet):
        self.wallet = wallet
        self.logger = TradeLogger()
    
    def sell_token(self, token_contract, amount_pct=100, token_name="Unknown"):
        """
        卖出代币
        
        Args:
            token_contract: 代币合约地址
            amount_pct: 卖出百分比（默认 100%）
            token_name: 代币名称
        """
        print(f"\n{'='*60}")
        print(f"💸 卖出代币")
        print(f"   代币: {token_name}")
        print(f"   合约: {token_contract[:12]}...")
        print(f"   卖出: {amount_pct}%")
        print(f"{'='*60}\n")
        
        try:
            # 1. 获取代币余额
            from solders.rpc.requests import GetTokenAccountsByOwner
            from solders.rpc.config import RpcTokenAccountsFilterMint
            
            # 简化版：直接获取所有代币账户
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    str(self.wallet.pubkey),
                    {"mint": token_contract},
                    {"encoding": "jsonParsed"}
                ]
            }
            
            resp = requests.post(SOLANA_RPC, json=payload, timeout=10)
            data = resp.json()
            
            accounts = data.get('result', {}).get('value', [])
            if not accounts:
                print(f"❌ 未找到代币账户")
                return {"success": False, "error": "未找到代币"}
            
            token_account = accounts[0]
            token_balance = int(token_account['account']['data']['parsed']['info']['tokenAmount']['amount'])
            
            if token_balance == 0:
                print(f"❌ 代币余额为 0")
                return {"success": False, "error": "余额为 0"}
            
            # 计算卖出数量
            sell_amount = int(token_balance * amount_pct / 100)
            
            print(f"💰 代币余额: {token_balance:,}")
            print(f"📤 卖出数量: {sell_amount:,}")
            
            # 2. 获取报价（反向：代币 -> SOL）
            sol_mint = "So11111111111111111111111111111111111111112"
            
            quote_url = f"{JUPITER_API}/quote"
            params = {
                "inputMint": token_contract,
                "outputMint": sol_mint,
                "amount": sell_amount,
                "slippageBps": 1500  # 15% 滑点（卖出更宽松）
            }
            
            print(f"📊 获取卖出报价...")
            quote_resp = requests.get(quote_url, params=params, timeout=15)
            
            if quote_resp.status_code != 200:
                print(f"❌ 无法获取报价")
                return {"success": False, "error": "无法获取报价"}
            
            quote = quote_resp.json()
            out_lamports = int(quote.get('outAmount', 0))
            out_sol = out_lamports / 1e9
            
            print(f"✅ 预计获得: {out_sol:.4f} SOL")
            
            # 3. 执行卖出（复用 execute_swap）
            result = self.execute_swap(quote)
            
            if result.get('success'):
                print(f"\n✅ 卖出成功！")
                print(f"   获得: {out_sol:.4f} SOL")
                print(f"   签名: {result.get('signature', '')[:16]}...")
            
            return result
            
        except Exception as e:
            print(f"❌ 卖出失败: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_quote(self, output_mint, amount_sol):
        """获取交易报价"""
        try:
            sol_mint = "So11111111111111111111111111111111111111112"
            amount_lamports = int(amount_sol * 1e9)
            
            url = f"{JUPITER_API}/quote"
            params = {
                "inputMint": sol_mint,
                "outputMint": output_mint,
                "amount": amount_lamports,
                "slippageBps": 1000  # 10% 滑点（meme 币波动大）
            }
            
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"❌ 获取报价失败: {e}")
        return None
    
    def execute_swap(self, quote):
        """
        执行真实的 Jupiter Swap 交易
        
        流程：
        1. 调用 Jupiter /swap API 获取序列化交易
        2. 反序列化交易
        3. 用钱包签名
        4. 发送到 Solana 链
        """
        try:
            # 1. 调用 Jupiter Swap API
            swap_url = f"{JUPITER_API}/swap"
            swap_payload = {
                "quoteResponse": quote,
                "userPublicKey": str(self.wallet.pubkey),
                "wrapAndUnwrapSol": True,
                "dynamicComputeUnitLimit": True,
                "prioritizationFeeLamports": "auto"
            }
            
            print("📡 调用 Jupiter Swap API...")
            swap_resp = requests.post(swap_url, json=swap_payload, timeout=30)
            
            if swap_resp.status_code != 200:
                return {
                    "success": False,
                    "error": f"Jupiter API 错误: {swap_resp.text}",
                    "simulated": False
                }
            
            swap_data = swap_resp.json()
            swap_transaction = swap_data.get('swapTransaction')
            
            if not swap_transaction:
                return {
                    "success": False,
                    "error": "未获得交易数据",
                    "simulated": False
                }
            
            # 2. 反序列化交易（Base64 -> bytes）
            import base64
            tx_bytes = base64.b64decode(swap_transaction)
            
            # 3. 签名交易
            print("✍️  签名交易...")
            from solders.transaction import VersionedTransaction
            tx = VersionedTransaction.from_bytes(tx_bytes)
            
            # 用钱包私钥签名
            signed_tx = VersionedTransaction(
                tx.message,
                [self.wallet.keypair]
            )
            
            # 4. 发送到 Solana 链
            print("🚀 发送交易到链上...")
            send_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    base64.b64encode(bytes(signed_tx)).decode('utf-8'),
                    {
                        "encoding": "base64",
                        "skipPreflight": False,
                        "preflightCommitment": "confirmed",
                        "maxRetries": 3
                    }
                ]
            }
            
            send_resp = requests.post(SOLANA_RPC, json=send_payload, timeout=30)
            send_data = send_resp.json()
            
            if send_data.get('error'):
                return {
                    "success": False,
                    "error": f"链上错误: {send_data['error']}",
                    "simulated": False
                }
            
            tx_signature = send_data.get('result')
            
            print(f"✅ 交易已发送！")
            print(f"   Signature: {tx_signature}")
            print(f"   查看: https://solscan.io/tx/{tx_signature}")
            
            return {
                "success": True,
                "signature": tx_signature,
                "explorer": f"https://solscan.io/tx/{tx_signature}",
                "simulated": False
            }
            
        except Exception as e:
            print(f"❌ 交易执行失败: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "simulated": False
            }
    
    def buy_token(self, contract, amount_sol, token_name="Unknown"):
        """
        自动买入代币
        
        Args:
            contract: 代币合约地址
            amount_sol: 买入金额
            token_name: 代币名称
        """
        print(f"\n{'='*60}")
        print(f"🔄 自动交易触发")
        print(f"   代币: {token_name}")
        print(f"   合约: {contract[:12]}...")
        print(f"   金额: {amount_sol} SOL")
        print(f"{'='*60}\n")
        
        # 1. 风控检查
        can_trade, reason = self.logger.can_trade(amount_sol)
        if not can_trade:
            print(f"❌ 交易被拒绝: {reason}")
            return {
                "success": False,
                "error": reason,
                "timestamp": datetime.now().isoformat()
            }
        
        # 2. 余额检查
        balance = self.wallet.get_balance()
        print(f"💰 钱包余额: {balance:.4f} SOL")
        
        if balance < amount_sol + 0.01:
            print(f"❌ 余额不足")
            return {
                "success": False,
                "error": f"余额不足（需要 {amount_sol + 0.01} SOL）",
                "timestamp": datetime.now().isoformat()
            }
        
        # 3. 获取报价
        print(f"📊 获取报价...")
        quote = self.get_quote(contract, amount_sol)
        
        if not quote:
            print(f"❌ 无法获取报价")
            return {
                "success": False,
                "error": "无法获取报价",
                "timestamp": datetime.now().isoformat()
            }
        
        out_amount = int(quote.get('outAmount', 0))
        print(f"✅ 报价成功")
        print(f"   预计获得: {out_amount:,} 代币单位")
        
        # 4. 执行交易
        print(f"⚡ 执行交易...")
        result = self.execute_swap(quote)
        
        # 5. 记录交易
        trade_record = {
            "timestamp": datetime.now().isoformat(),
            "contract": contract,
            "token_name": token_name,
            "amount_sol": amount_sol,
            "expected_tokens": out_amount,
            "status": "simulated" if result.get("simulated") else ("success" if result.get("success") else "failed"),
            "result": result
        }
        
        self.logger.add_trade(trade_record)
        
        print(f"\n✅ 交易已记录")
        print(f"   状态: {trade_record['status']}")
        print(f"   时间: {trade_record['timestamp']}")
        
        # 6. 如果交易成功，记录到持仓管理
        if result.get("success"):
            try:
                from position_manager import PositionManager
                pm = PositionManager()
                
                # 获取买入价格（从报价中）
                in_amount = int(quote.get('inAmount', 0))
                buy_price_per_token = (amount_sol * 1e9) / out_amount if out_amount > 0 else 0
                
                pm.add_position(
                    contract=contract,
                    token_name=token_name,
                    amount_sol=amount_sol,
                    buy_price=buy_price_per_token,
                    tokens_received=out_amount
                )
                
                print(f"📝 已添加到持仓管理")
            except Exception as e:
                print(f"⚠️  持仓记录失败: {e}")
        
        return trade_record

# ==================== 主程序 ====================
def auto_trade_from_signal(signal_file="/root/.openclaw/workspace/meme_signals.json"):
    """从信号文件读取并自动交易"""
    try:
        with open(signal_file, 'r') as f:
            data = json.load(f)
        
        new_signals = data.get('new_signals', [])
        
        if not new_signals:
            print("暂无新信号")
            return
        
        # 初始化交易器
        wallet = Wallet()
        trader = JupiterTrader(wallet)
        
        print(f"🐉 紫龙全自动交易系统")
        print(f"📍 钱包: {wallet.get_address()}")
        print(f"💰 余额: {wallet.get_balance():.4f} SOL\n")
        
        # 处理每个信号
        for sig in new_signals:
            analysis = sig.get('analysis', {})
            score = analysis.get('score', 0)
            token_data = sig.get('token', {})
            signal_data = sig.get('signal', {})
            
            # 评分检查
            if score < MIN_SCORE:
                print(f"⏭️  跳过: {signal_data.get('contract', '')[:8]}... 评分过低 ({score:.0f})")
                continue
            
            # 流动性检查
            liquidity = token_data.get('liquidity', 0)
            if liquidity < MIN_LIQUIDITY:
                print(f"⏭️  跳过: {signal_data.get('contract', '')[:8]}... 流动性过低 (${liquidity:,.0f})")
                continue
            
            # 计算买入金额（基于评分）
            if score >= 85:
                amount = 1.0  # 高分：1 SOL
            elif score >= 75:
                amount = 0.5  # 中高分：0.5 SOL
            else:
                amount = 0.2  # 及格分：0.2 SOL
            
            # 执行交易
            result = trader.buy_token(
                contract=signal_data.get('contract'),
                amount_sol=amount,
                token_name=signal_data.get('post_title', 'Unknown')[:30]
            )
            
            # 返回结果（用于通知）
            return {
                "traded": True,
                "signal": signal_data,
                "amount": amount,
                "result": result
            }
        
        return {"traded": False, "reason": "无符合条件的信号"}
        
    except Exception as e:
        print(f"❌ 自动交易错误: {e}")
        return {"traded": False, "error": str(e)}

if __name__ == "__main__":
    result = auto_trade_from_signal()
    print(f"\n{'='*60}")
    print(f"结果: {json.dumps(result, indent=2)}")
    print(f"{'='*60}")
