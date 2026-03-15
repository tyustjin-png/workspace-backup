#!/usr/bin/env python3
"""
多链交易管理器
统一管理 Solana + Base 交易
"""

import json
from datetime import datetime

# 风控参数
MAX_PER_TRADE_SOL = 1.0   # Solana 单笔限额
MAX_PER_TRADE_ETH = 0.1   # Base 单笔限额
DAILY_LIMIT_SOL = 3.0     # Solana 每日限额
DAILY_LIMIT_ETH = 0.3     # Base 每日限额
MIN_SCORE = 70

TRADE_LOG = "/root/.openclaw/workspace/multichain_trade_history.json"

class MultiChainTrader:
    def __init__(self):
        # 延迟导入，避免循环依赖
        try:
            from full_auto_trader import Wallet as SolanaWallet, JupiterTrader
            self.solana_wallet = SolanaWallet()
            self.solana_trader = JupiterTrader(self.solana_wallet)
        except Exception as e:
            print(f"⚠️  Solana 交易器初始化失败: {e}")
            self.solana_trader = None
        
        try:
            from base_trader import BaseTrader
            self.base_trader = BaseTrader()
        except Exception as e:
            print(f"⚠️  Base 交易器初始化失败: {e}")
            self.base_trader = None
    
    def load_history(self):
        """加载交易历史"""
        try:
            with open(TRADE_LOG, 'r') as f:
                return json.load(f)
        except:
            return {
                "trades": [],
                "daily_total": {
                    "solana": {},
                    "base": {}
                }
            }
    
    def save_history(self, data):
        """保存交易历史"""
        with open(TRADE_LOG, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_today_total(self, chain):
        """获取今日已用额度"""
        data = self.load_history()
        today = datetime.now().strftime("%Y-%m-%d")
        return data["daily_total"].get(chain, {}).get(today, 0)
    
    def can_trade(self, chain, amount):
        """检查是否可以交易"""
        if chain == 'solana':
            max_per_trade = MAX_PER_TRADE_SOL
            daily_limit = DAILY_LIMIT_SOL
            unit = "SOL"
        elif chain == 'base':
            max_per_trade = MAX_PER_TRADE_ETH
            daily_limit = DAILY_LIMIT_ETH
            unit = "ETH"
        else:
            return False, f"不支持的链: {chain}"
        
        # 单笔限额
        if amount > max_per_trade:
            return False, f"超过单笔限额 {max_per_trade} {unit}"
        
        # 每日限额
        today_total = self.get_today_total(chain)
        if today_total + amount > daily_limit:
            return False, f"超过每日限额 {daily_limit} {unit}（已用 {today_total:.2f}）"
        
        return True, "OK"
    
    def buy_token(self, signal, token_data, analysis):
        """
        根据链类型自动选择交易器
        
        Args:
            signal: 信号数据（包含 chain, contract）
            token_data: 代币数据
            analysis: 分析结果
        """
        chain = signal.get('chain', 'solana')
        contract = signal['contract']
        token_name = signal.get('post_title', 'Unknown')
        score = analysis['score']
        
        print(f"\n{'='*60}")
        print(f"🔄 多链交易触发")
        print(f"   链: {chain.upper()}")
        print(f"   代币: {token_name}")
        print(f"   合约: {contract[:12]}...")
        print(f"   评分: {score:.0f}")
        print(f"{'='*60}\n")
        
        # 根据评分计算买入金额
        if score >= 85:
            amount_multiplier = 1.0
        elif score >= 75:
            amount_multiplier = 0.5
        else:
            amount_multiplier = 0.2
        
        # 不同链使用不同金额
        if chain == 'solana':
            amount = MAX_PER_TRADE_SOL * amount_multiplier
            unit = 'SOL'
        elif chain == 'base':
            amount = MAX_PER_TRADE_ETH * amount_multiplier
            unit = 'ETH'
        else:
            return {
                "success": False,
                "error": f"不支持的链: {chain}"
            }
        
        print(f"💰 买入金额: {amount} {unit}")
        
        # 风控检查
        can_trade, reason = self.can_trade(chain, amount)
        if not can_trade:
            print(f"❌ 交易被拒绝: {reason}")
            return {
                "success": False,
                "error": reason,
                "timestamp": datetime.now().isoformat()
            }
        
        # 选择交易器
        if chain == 'solana':
            if not self.solana_trader:
                return {"success": False, "error": "Solana 交易器未初始化"}
            
            result = self.solana_trader.buy_token(contract, amount, token_name)
        
        elif chain == 'base':
            if not self.base_trader:
                return {"success": False, "error": "Base 交易器未初始化"}
            
            result = self.base_trader.swap_eth_for_token(contract, amount)
        
        else:
            return {"success": False, "error": f"不支持的链: {chain}"}
        
        # 记录交易
        trade_record = {
            "timestamp": datetime.now().isoformat(),
            "chain": chain,
            "contract": contract,
            "token_name": token_name,
            "amount": amount,
            "unit": unit,
            "score": score,
            "result": result
        }
        
        data = self.load_history()
        data["trades"].append(trade_record)
        
        # 更新每日总额
        today = datetime.now().strftime("%Y-%m-%d")
        if chain not in data["daily_total"]:
            data["daily_total"][chain] = {}
        data["daily_total"][chain][today] = data["daily_total"][chain].get(today, 0) + amount
        
        self.save_history(data)
        
        print(f"\n✅ 交易已记录")
        
        return trade_record

# 主程序
def auto_trade_from_signal(signal_file="/root/.openclaw/workspace/meme_signals.json"):
    """从信号文件读取并自动交易（多链）"""
    try:
        with open(signal_file, 'r') as f:
            data = json.load(f)
        
        new_signals = data.get('new_signals', [])
        
        if not new_signals:
            print("暂无新信号")
            return
        
        # 初始化交易器
        trader = MultiChainTrader()
        
        print(f"🐉 紫龙多链自动交易系统")
        print(f"{'='*60}\n")
        
        # 显示余额
        if trader.solana_trader:
            sol_balance = trader.solana_trader.wallet.get_balance()
            print(f"Solana 余额: {sol_balance:.4f} SOL")
        
        if trader.base_trader and trader.base_trader.address:
            eth_balance = trader.base_trader.get_balance()
            print(f"Base 余额: {eth_balance:.4f} ETH")
        
        print("")
        
        # 处理每个信号
        for sig in new_signals:
            analysis = sig.get('analysis', {})
            score = analysis.get('score', 0)
            token_data = sig.get('token', {})
            signal_data = sig.get('signal', {})
            
            # 评分检查
            if score < MIN_SCORE:
                chain = signal_data.get('chain', 'unknown')
                print(f"⏭️  跳过 [{chain}]: 评分过低 ({score:.0f})")
                continue
            
            # 流动性检查（通用）
            liquidity = token_data.get('liquidity', 0)
            if liquidity < 10000:
                print(f"⏭️  跳过: 流动性过低 (${liquidity:,.0f})")
                continue
            
            # 执行交易
            result = trader.buy_token(signal_data, token_data, analysis)
            
            # 返回结果（用于通知）
            return {
                "traded": True,
                "signal": signal_data,
                "result": result
            }
        
        return {"traded": False, "reason": "无符合条件的信号"}
        
    except Exception as e:
        print(f"❌ 自动交易错误: {e}")
        return {"traded": False, "error": str(e)}

if __name__ == "__main__":
    result = auto_trade_from_signal()
    print(f"\n{'='*60}")
    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print(f"{'='*60}")
