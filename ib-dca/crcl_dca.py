#!/usr/bin/env python3
"""
CRCL 条件定投脚本
================
根据价格阶梯策略自动买入 CRCL 股票

使用方法:
    python crcl_dca.py              # 正常执行
    python crcl_dca.py --dry-run    # 模拟运行，不实际下单
    python crcl_dca.py --config /path/to/config.yaml  # 指定配置文件
"""

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import yaml
from ib_insync import IB, Stock, MarketOrder, util


class CRCLDCATrader:
    """CRCL 条件定投交易器"""

    def __init__(self, config_path: str = "config.yaml", dry_run: bool = False):
        self.config_path = config_path
        self.dry_run = dry_run
        self.config = self._load_config()
        self.ib: Optional[IB] = None
        self._setup_logging()

    def _load_config(self) -> dict:
        """加载配置文件"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _setup_logging(self) -> None:
        """配置日志"""
        log_config = self.config.get("logging", {})
        log_level = getattr(logging, log_config.get("level", "INFO").upper())
        log_file = log_config.get("file", "logs/crcl_dca.log")

        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # 配置根日志器
        self.logger = logging.getLogger("CRCL_DCA")
        self.logger.setLevel(log_level)

        # 文件处理器（轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config.get("max_size_mb", 10) * 1024 * 1024,
            backupCount=log_config.get("backup_count", 5),
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # 格式
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def connect(self) -> bool:
        """连接 IB Gateway"""
        ib_config = self.config.get("ib", {})
        host = ib_config.get("host", "127.0.0.1")
        port = ib_config.get("port", 4001)
        client_id = ib_config.get("client_id", 1)
        timeout = ib_config.get("timeout", 30)

        self.logger.info(f"正在连接 IB Gateway ({host}:{port})...")

        try:
            self.ib = IB()
            self.ib.connect(host, port, clientId=client_id, timeout=timeout)
            self.logger.info("✓ IB Gateway 连接成功")
            return True
        except Exception as e:
            self.logger.error(f"✗ IB Gateway 连接失败: {e}")
            return False

    def disconnect(self) -> None:
        """断开 IB Gateway 连接"""
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()
            self.logger.info("已断开 IB Gateway 连接")

    def get_stock_price(self) -> Optional[float]:
        """获取 CRCL 实时价格"""
        stock_config = self.config.get("stock", {})
        symbol = stock_config.get("symbol", "CRCL")
        exchange = stock_config.get("exchange", "SMART")
        currency = stock_config.get("currency", "USD")

        self.logger.info(f"正在获取 {symbol} 实时价格...")

        try:
            contract = Stock(symbol, exchange, currency)
            self.ib.qualifyContracts(contract)

            # 请求市场数据
            ticker = self.ib.reqMktData(contract, "", False, False)

            # 等待数据（最多10秒）
            for _ in range(100):
                self.ib.sleep(0.1)
                if ticker.last and ticker.last > 0:
                    break
                if ticker.close and ticker.close > 0:
                    break

            # 取 last 价格，如果没有就取 close
            price = ticker.last if ticker.last and ticker.last > 0 else ticker.close

            # 取消市场数据订阅
            self.ib.cancelMktData(contract)

            if price and price > 0:
                self.logger.info(f"✓ {symbol} 当前价格: ${price:.2f}")
                return float(price)
            else:
                self.logger.warning(f"✗ 无法获取 {symbol} 价格 (last={ticker.last}, close={ticker.close})")
                return None

        except Exception as e:
            self.logger.error(f"✗ 获取价格失败: {e}")
            return None

    def calculate_buy_amount(self, price: float) -> Optional[float]:
        """根据价格计算买入金额"""
        max_buy_price = self.config.get("max_buy_price", 90.0)

        if price > max_buy_price:
            self.logger.info(f"价格 ${price:.2f} 高于阈值 ${max_buy_price:.2f}，跳过买入")
            return None

        tiers = self.config.get("tiers", [])
        for tier in tiers:
            price_max = tier.get("price_max", float("inf"))
            price_min = tier.get("price_min", 0)
            amount = tier.get("amount", 0)

            if price_min < price <= price_max:
                self.logger.info(
                    f"价格 ${price:.2f} 在区间 (${price_min:.2f}, ${price_max:.2f}]，"
                    f"买入金额: ${amount}"
                )
                return float(amount)

        self.logger.warning(f"价格 ${price:.2f} 不在任何定义的区间内")
        return None

    def calculate_shares(self, amount: float, price: float) -> int:
        """计算买入股数（向下取整）"""
        shares = int(amount / price)
        self.logger.info(f"买入金额 ${amount} / 价格 ${price:.2f} = {shares} 股")
        return shares

    def place_order(self, shares: int) -> dict:
        """下市价单买入"""
        stock_config = self.config.get("stock", {})
        symbol = stock_config.get("symbol", "CRCL")
        exchange = stock_config.get("exchange", "SMART")
        currency = stock_config.get("currency", "USD")

        ib_config = self.config.get("ib", {})
        readonly = ib_config.get("readonly", False)

        result = {
            "success": False,
            "order_id": None,
            "filled_shares": 0,
            "avg_price": 0.0,
            "message": "",
        }

        if self.dry_run or readonly:
            mode = "DRY-RUN" if self.dry_run else "READONLY"
            self.logger.info(f"[{mode}] 模拟下单: 买入 {shares} 股 {symbol}")
            result["success"] = True
            result["message"] = f"[{mode}] 模拟成功"
            return result

        try:
            contract = Stock(symbol, exchange, currency)
            self.ib.qualifyContracts(contract)

            order = MarketOrder("BUY", shares)
            order.tif = self.config.get("order", {}).get("tif", "DAY")

            self.logger.info(f"正在下单: 买入 {shares} 股 {symbol}...")
            trade = self.ib.placeOrder(contract, order)

            # 等待订单完成（最多60秒）
            timeout = 60
            for _ in range(timeout * 10):
                self.ib.sleep(0.1)
                if trade.isDone():
                    break

            if trade.orderStatus.status == "Filled":
                result["success"] = True
                result["order_id"] = trade.order.orderId
                result["filled_shares"] = trade.orderStatus.filled
                result["avg_price"] = trade.orderStatus.avgFillPrice
                result["message"] = (
                    f"成交 {result['filled_shares']} 股 @ ${result['avg_price']:.2f}"
                )
                self.logger.info(f"✓ 订单成交: {result['message']}")
            else:
                result["message"] = f"订单状态: {trade.orderStatus.status}"
                self.logger.warning(f"✗ 订单未完全成交: {result['message']}")

        except Exception as e:
            result["message"] = str(e)
            self.logger.error(f"✗ 下单失败: {e}")

        return result

    def send_notification(self, title: str, message: str, is_error: bool = False) -> None:
        """发送通知（通过 openclaw message）"""
        notif_config = self.config.get("notification", {})

        if not notif_config.get("enabled", True):
            return

        # 根据配置决定是否发送
        if is_error and not notif_config.get("on_failure", True):
            return
        if not is_error and not notif_config.get("on_success", True):
            return

        emoji = "❌" if is_error else "✅"
        full_message = f"{emoji} **{title}**\n\n{message}"

        self.logger.info(f"发送通知: {title}")

        try:
            result = subprocess.run(
                ["openclaw", "message", "send", "--message", full_message],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                self.logger.debug("通知发送成功")
            else:
                self.logger.warning(f"通知发送失败: {result.stderr}")
        except FileNotFoundError:
            self.logger.warning("openclaw 命令未找到，跳过通知")
        except Exception as e:
            self.logger.warning(f"发送通知时出错: {e}")

    def run(self) -> bool:
        """执行定投流程"""
        self.logger.info("=" * 50)
        self.logger.info("CRCL 条件定投开始执行")
        self.logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"模式: {'DRY-RUN (模拟)' if self.dry_run else 'LIVE (实盘)'}")
        self.logger.info("=" * 50)

        try:
            # 1. 连接 IB
            if not self.connect():
                self.send_notification(
                    "CRCL 定投失败",
                    "无法连接 IB Gateway",
                    is_error=True,
                )
                return False

            # 2. 获取价格
            price = self.get_stock_price()
            if price is None:
                self.send_notification(
                    "CRCL 定投失败",
                    "无法获取 CRCL 实时价格",
                    is_error=True,
                )
                return False

            # 3. 计算买入金额
            amount = self.calculate_buy_amount(price)
            if amount is None:
                notif_config = self.config.get("notification", {})
                if notif_config.get("on_skip", False):
                    self.send_notification(
                        "CRCL 定投跳过",
                        f"当前价格 ${price:.2f} 高于阈值，不执行买入",
                        is_error=False,
                    )
                self.logger.info("本次定投跳过")
                return True

            # 4. 计算股数
            shares = self.calculate_shares(amount, price)
            if shares <= 0:
                self.logger.warning("计算股数为 0，跳过下单")
                return True

            # 5. 下单
            result = self.place_order(shares)

            # 6. 发送通知
            if result["success"]:
                self.send_notification(
                    "CRCL 定投成功",
                    f"价格: ${price:.2f}\n"
                    f"计划金额: ${amount}\n"
                    f"买入股数: {shares}\n"
                    f"结果: {result['message']}",
                    is_error=False,
                )
                return True
            else:
                self.send_notification(
                    "CRCL 定投失败",
                    f"价格: ${price:.2f}\n"
                    f"计划买入: {shares} 股\n"
                    f"错误: {result['message']}",
                    is_error=True,
                )
                return False

        except Exception as e:
            self.logger.exception(f"执行过程中发生异常: {e}")
            self.send_notification(
                "CRCL 定投异常",
                f"发生未预期的错误:\n{str(e)}",
                is_error=True,
            )
            return False

        finally:
            self.disconnect()
            self.logger.info("=" * 50)
            self.logger.info("CRCL 条件定投执行结束")
            self.logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="CRCL 条件定投脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        "-c",
        default="config.yaml",
        help="配置文件路径 (默认: config.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="模拟运行，不实际下单",
    )

    args = parser.parse_args()

    # 切换到脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    import os
    os.chdir(script_dir)

    trader = CRCLDCATrader(config_path=args.config, dry_run=args.dry_run)
    success = trader.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
