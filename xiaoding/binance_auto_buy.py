#!/usr/bin/env python3
"""
币安 API 自动买入 - 分区间定投策略
基于多维度评分体系（z值 0-6）自动执行买入
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
import requests
import hmac
import hashlib
from urllib.parse import urlencode

# ============ 配置 ============
CONFIG_FILE = Path(__file__).parent / 'config/binance_auto_buy.json'
STATE_FILE = Path(__file__).parent / 'data/binance_buy_state.json'
HISTORY_FILE = Path(__file__).parent / 'data/binance_buy_history.jsonl'

# 斐波那契定投倍数映射
Z_MULTIPLIER_MAP = {
    0: 0,   # 不买入（牛市/高位）
    1: 1,   # 1倍基础份额
    2: 2,   # 2倍
    3: 3,   # 3倍
    4: 5,   # 5倍（斐波那契）
    5: 8,   # 8倍
    6: 13   # 13倍（极端底部）
}

# 币安 API 端点
# 通过VPS Nginx代理访问币安API（固定IP，解决白名单问题）
BINANCE_API_BASE = 'http://100.72.82.26:9080/binance'
BINANCE_API_ENDPOINTS = {
    'order': '/api/v3/order',
    'account': '/api/v3/account',
    'ticker_price': '/api/v3/ticker/price'
}


class BinanceClient:
    """币安 API 客户端"""
    
    def __init__(self, api_key, api_secret, testnet=False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://testnet.binance.vision' if testnet else BINANCE_API_BASE
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': api_key
        })
        # 走VPS代理时不经过本地Surge代理
        self.session.trust_env = False
    
    def _sign(self, params):
        """生成签名"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method, endpoint, params=None, signed=False):
        """发送请求"""
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._sign(params)
        
        url = self.base_url + endpoint
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, params=params, timeout=10)
            else:
                raise ValueError(f"不支持的方法: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"❌ API 请求失败: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   响应: {e.response.text}")
            return None
    
    def get_price(self, symbol):
        """获取当前价格"""
        result = self._request('GET', BINANCE_API_ENDPOINTS['ticker_price'], 
                              params={'symbol': symbol})
        if result:
            return float(result['price'])
        return None
    
    def get_account_balance(self, asset):
        """获取账户余额"""
        result = self._request('GET', BINANCE_API_ENDPOINTS['account'], signed=True)
        if result and 'balances' in result:
            for balance in result['balances']:
                if balance['asset'] == asset:
                    return {
                        'free': float(balance['free']),
                        'locked': float(balance['locked'])
                    }
        return None
    
    def market_buy(self, symbol, quote_amount):
        """
        市价买入
        :param symbol: 交易对，如 'BTCUSDT'
        :param quote_amount: 计价货币金额（如 100 USDT）
        """
        params = {
            'symbol': symbol,
            'side': 'BUY',
            'type': 'MARKET',
            'quoteOrderQty': quote_amount  # 用计价货币金额下单
        }
        
        result = self._request('POST', BINANCE_API_ENDPOINTS['order'], 
                              params=params, signed=True)
        return result


class AutoBuyStrategy:
    """自动买入策略"""
    
    def __init__(self, config_path=CONFIG_FILE):
        self.config = self.load_config(config_path)
        self.state = self.load_state()
        self.client = None
        
        # 初始化币安客户端
        if self.config.get('binance_api_key') and self.config.get('binance_api_secret'):
            self.client = BinanceClient(
                self.config['binance_api_key'],
                self.config['binance_api_secret'],
                testnet=self.config.get('testnet', False)
            )
    
    def load_config(self, config_path):
        """加载配置，API Key直接从1Password读取（不落盘）"""
        if not config_path.exists():
            print(f"❌ 配置文件不存在: {config_path}")
            print(f"   请先创建配置文件")
            return {}
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # 直接从1Password CLI读取，无明文文件
        try:
            import subprocess
            token_file = Path('/Users/qianzhao/.openclaw/.op-token')
            if token_file.exists():
                env = dict(os.environ, OP_SERVICE_ACCOUNT_TOKEN=token_file.read_text().strip())
                api_key = subprocess.run(
                    ['op', 'read', 'op://Agent/w54ycg3h3k7uxixfcfhfui3rgu/te2dvfdmjrwpzgweat7ocwjb2e'],
                    capture_output=True, text=True, env=env
                ).stdout.strip()
                api_secret = subprocess.run(
                    ['op', 'read', 'op://Agent/w54ycg3h3k7uxixfcfhfui3rgu/ghdrbpsvsmuuf6bsjxwrxyibvy'],
                    capture_output=True, text=True, env=env
                ).stdout.strip()
                
                # 清理（取64位长的行）
                for line in api_key.split('\n'):
                    if len(line.strip()) == 64:
                        api_key = line.strip()
                        break
                for line in api_secret.split('\n'):
                    if len(line.strip()) == 64:
                        api_secret = line.strip()
                        break
                
                if len(api_key) == 64 and len(api_secret) == 64:
                    config['binance_api_key'] = api_key
                    config['binance_api_secret'] = api_secret
                    print("✅ 已从1Password直接加载API Key（零落盘）")
                else:
                    print("⚠️ 1Password字段格式异常，尝试secrets.json")
                    self._try_secrets_json(config)
            else:
                print("⚠️ .op-token不存在，尝试secrets.json")
                self._try_secrets_json(config)
        except Exception as e:
            print(f"⚠️ 1Password读取失败，尝试secrets.json: {e}")
            self._try_secrets_json(config)
        
        return config
    
    def _try_secrets_json(self, config):
        """Fallback: 从secrets.json读取"""
        secrets_file = Path('/Users/qianzhao/.openclaw/secrets.json')
        if secrets_file.exists():
            try:
                with open(secrets_file, 'r') as f:
                    secrets = json.load(f)
                if secrets.get('binance-api-key'):
                    config['binance_api_key'] = secrets['binance-api-key']
                if secrets.get('binance-secret-key'):
                    config['binance_api_secret'] = secrets['binance-secret-key']
                print("✅ 已从secrets.json加载API Key")
            except Exception as e:
                print(f"⚠️ secrets.json也失败: {e}")
    
    def load_state(self):
        """加载状态"""
        if not STATE_FILE.exists():
            return {
                'total_invested': 0,
                'total_bought': 0,
                'last_z_value': None,
                'last_buy_time': None,
                'buy_count': 0
            }
        
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    
    def save_state(self):
        """保存状态"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def save_history(self, record):
        """保存买入历史"""
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, 'a') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    def get_z_value(self):
        """
        获取当前 z 值
        优先级：
        1. 自动从看板API获取（http://8.216.6.8/）
        2. 从本地缓存文件读取
        3. 手动配置的值
        """
        import subprocess
        
        # 方法1: 调用 get_z_value.py 自动获取最新z值
        try:
            script_path = Path(__file__).parent / 'get_z_value.py'
            if script_path.exists():
                print("📡 正在从看板获取最新z值...")
                result = subprocess.run(
                    ['python3', str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                if result.returncode == 0:
                    # 读取保存的z值数据
                    z_file = Path(__file__).parent / 'data/current_z_value.json'
                    if z_file.exists():
                        with open(z_file, 'r') as f:
                            data = json.load(f)
                            z_value = data.get('z_value')
                            if z_value is not None:
                                print(f"✅ 成功获取z值: {z_value} (数据时间: {data.get('last_update')})")
                                return z_value
        except Exception as e:
            print(f"⚠️ 自动获取z值失败: {e}")
        
        # 方法2: 从本地缓存读取（如果自动获取失败）
        try:
            z_file = Path(__file__).parent / 'data/current_z_value.json'
            if z_file.exists():
                with open(z_file, 'r') as f:
                    data = json.load(f)
                    z_value = data.get('z_value')
                    if z_value is not None:
                        print(f"📁 使用本地缓存z值: {z_value} (数据时间: {data.get('last_update')})")
                        return z_value
        except:
            pass
        
        # 方法3: 手动配置的值（兜底）
        if self.config.get('manual_z_value') is not None:
            z_value = self.config['manual_z_value']
            print(f"⚙️ 使用手动配置z值: {z_value}")
            return z_value
        
        print("❌ 无法获取 z 值")
        return None
    
    def calculate_buy_amount(self, z_value):
        """
        计算应该买入的金额
        """
        if z_value not in Z_MULTIPLIER_MAP:
            print(f"⚠️ 无效的 z 值: {z_value}")
            return 0
        
        multiplier = Z_MULTIPLIER_MAP[z_value]
        
        if multiplier == 0:
            print("📊 当前 z=0，市场处于高位，不买入")
            return 0
        
        # 获取基础份额
        base_amount = self.config.get('base_amount')
        
        if not base_amount:
            # 如果没有设置基础份额，根据预算计算
            total_budget = self.config.get('total_budget')
            expected_multiplier = self.config.get('expected_multiplier', 1.5)
            cycle_days = self.config.get('cycle_days', 365)
            
            if total_budget:
                base_amount = total_budget / (expected_multiplier * cycle_days)
            else:
                print("❌ 请配置 base_amount 或 total_budget")
                return 0
        
        buy_amount = base_amount * multiplier
        
        # 检查预算限制（固定预算模式）
        if self.config.get('mode') == 'fixed_budget':
            total_budget = self.config.get('total_budget', 0)
            remaining = total_budget - self.state['total_invested']
            if buy_amount > remaining:
                buy_amount = remaining
                print(f"⚠️ 预算即将用完，本次买入调整为: ${buy_amount:.2f}")
        
        return buy_amount
    
    def execute_buy(self, dry_run=False):
        """
        执行买入
        :param dry_run: 是否模拟运行（不实际下单）
        """
        print("=" * 60)
        print(f"🤖 币安自动买入 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 获取 z 值
        z_value = self.get_z_value()
        if z_value is None:
            print("❌ 无法获取 z 值，退出")
            import sys; sys.exit(1)
            return
        
        print(f"\n📊 当前 z 值: {z_value}")
        print(f"📈 定投倍数: {Z_MULTIPLIER_MAP.get(z_value, 0)}x")
        
        # 计算买入金额
        buy_amount = self.calculate_buy_amount(z_value)
        
        if buy_amount <= 0:
            print("✅ 无需买入")
            return
        
        # 获取交易对和当前价格
        symbol = self.config.get('symbol', 'BTCUSDT')
        quote_asset = self.config.get('quote_asset', 'USDT')
        
        print(f"\n💰 应买入金额: ${buy_amount:.2f} {quote_asset}")
        print(f"📌 交易对: {symbol}")
        
        if not self.client:
            print("❌ 币安客户端未初始化，请检查 API 配置")
            import sys; sys.exit(1)
            return
        
        # 获取当前价格
        current_price = self.client.get_price(symbol)
        if not current_price:
            print("❌ 无法获取当前价格")
            import sys; sys.exit(1)
            return
        
        print(f"💵 当前价格: ${current_price:.2f}")
        
        estimated_quantity = buy_amount / current_price
        print(f"📦 预计买入: {estimated_quantity:.6f} BTC")
        
        # 模拟运行
        if dry_run:
            print("\n⚠️ 【模拟运行】未实际下单")
            record = {
                'timestamp': datetime.now().isoformat(),
                'z_value': z_value,
                'multiplier': Z_MULTIPLIER_MAP[z_value],
                'buy_amount': buy_amount,
                'price': current_price,
                'estimated_quantity': estimated_quantity,
                'dry_run': True
            }
            self.save_history(record)
            return
        
        # 实际下单
        print("\n🚀 开始下单...")
        
        result = self.client.market_buy(symbol, buy_amount)
        
        if result and 'orderId' in result:
            print("✅ 买入成功！")
            print(f"   订单ID: {result['orderId']}")
            print(f"   成交金额: {result.get('cummulativeQuoteQty', 'N/A')}")
            
            # 更新状态
            self.state['total_invested'] += buy_amount
            self.state['total_bought'] += float(result.get('executedQty', 0))
            self.state['last_z_value'] = z_value
            self.state['last_buy_time'] = datetime.now().isoformat()
            self.state['buy_count'] += 1
            self.save_state()
            
            # 保存历史
            record = {
                'timestamp': datetime.now().isoformat(),
                'z_value': z_value,
                'multiplier': Z_MULTIPLIER_MAP[z_value],
                'buy_amount': buy_amount,
                'price': current_price,
                'order_id': result['orderId'],
                'executed_qty': result.get('executedQty'),
                'fills': result.get('fills', [])
            }
            self.save_history(record)
            
            print("\n📊 累计统计:")
            print(f"   总投入: ${self.state['total_invested']:.2f}")
            print(f"   总买入: {self.state['total_bought']:.6f} BTC")
            print(f"   买入次数: {self.state['buy_count']}")
            
        else:
            print("❌ 买入失败")
            if result:
                print(f"   错误信息: {result}")
            import sys
            sys.exit(1)
        
        print("\n" + "=" * 60)
    
    def show_status(self):
        """显示当前状态"""
        print("=" * 60)
        print("📊 币安自动买入 - 状态")
        print("=" * 60)
        
        print(f"\n🔧 配置:")
        print(f"   交易对: {self.config.get('symbol', 'BTCUSDT')}")
        print(f"   模式: {self.config.get('mode', 'fixed_budget')}")
        print(f"   基础份额: ${self.config.get('base_amount', 'N/A')}")
        print(f"   总预算: ${self.config.get('total_budget', 'N/A')}")
        
        print(f"\n📈 当前状态:")
        print(f"   总投入: ${self.state['total_invested']:.2f}")
        print(f"   总买入: {self.state['total_bought']:.6f} BTC")
        print(f"   买入次数: {self.state['buy_count']}")
        print(f"   上次 z 值: {self.state['last_z_value']}")
        print(f"   上次买入: {self.state['last_buy_time'] or 'N/A'}")
        
        if self.config.get('mode') == 'fixed_budget':
            total_budget = self.config.get('total_budget', 0)
            remaining = total_budget - self.state['total_invested']
            usage = (self.state['total_invested'] / total_budget * 100) if total_budget > 0 else 0
            print(f"\n💰 预算:")
            print(f"   已使用: ${self.state['total_invested']:.2f} ({usage:.1f}%)")
            print(f"   剩余: ${remaining:.2f}")
        
        print("\n" + "=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='币安自动买入 - 分区间定投')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行（不实际下单）')
    parser.add_argument('--status', action='store_true', help='显示状态')
    
    args = parser.parse_args()
    
    strategy = AutoBuyStrategy()
    
    if args.status:
        strategy.show_status()
    else:
        strategy.execute_buy(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
