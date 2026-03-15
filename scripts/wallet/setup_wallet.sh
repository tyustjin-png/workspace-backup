#!/bin/bash
# Solana 钱包设置脚本

echo "🐉 紫龙自动交易系统 - 钱包设置"
echo ""

# 检查 Solana CLI
if ! command -v solana &> /dev/null; then
    echo "📦 安装 Solana CLI..."
    sh -c "$(curl -sSfL https://release.solana.com/v1.18.0/install)"
    export PATH="/Users/qianzhao/.local/share/solana/install/active_release/bin:$PATH"
fi

# 创建钱包目录
mkdir -p ~/.config/solana

# 生成新钱包（如果不存在）
WALLET_PATH=~/.config/solana/trading-bot.json

if [ -f "$WALLET_PATH" ]; then
    echo "✅ 钱包已存在"
else
    echo "🔑 生成新钱包..."
    solana-keygen new --no-bip39-passphrase --outfile $WALLET_PATH
fi

# 显示钱包地址
echo ""
echo "📍 你的钱包地址:"
solana-keygen pubkey $WALLET_PATH

echo ""
echo "⚠️  重要提示:"
echo "1. 往这个地址充值 SOL（用于交易和 Gas 费）"
echo "2. 建议初始充值 0.5-1 SOL"
echo "3. 私钥保存在: $WALLET_PATH"
echo "4. 请妥善备份私钥！"
