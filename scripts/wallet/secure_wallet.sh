#!/bin/bash
# 钱包安全管理脚本

WALLET_PLAIN="/Users/qianzhao/.config/solana/trading-bot.json"
WALLET_ENCRYPTED="/Users/qianzhao/.config/solana/trading-bot.json.age"
WALLET_KEY="/Users/qianzhao/.config/solana/.wallet.key"

# 生成加密密钥（只运行一次）
generate_key() {
    if [ -f "$WALLET_KEY" ]; then
        echo "❌ 密钥已存在"
        return 1
    fi
    
    # 生成随机密钥
    openssl rand -base64 32 > "$WALLET_KEY"
    chmod 600 "$WALLET_KEY"
    
    echo "✅ 密钥已生成: $WALLET_KEY"
    echo "⚠️  请立即备份此密钥！"
}

# 加密钱包
encrypt() {
    if [ ! -f "$WALLET_PLAIN" ]; then
        echo "❌ 未找到钱包文件"
        return 1
    fi
    
    if [ ! -f "$WALLET_KEY" ]; then
        echo "❌ 未找到密钥，请先运行: $0 generate"
        return 1
    fi
    
    # 使用密钥加密
    cat "$WALLET_PLAIN" | age -e -i "$WALLET_KEY" -o "$WALLET_ENCRYPTED"
    
    echo "✅ 钱包已加密: $WALLET_ENCRYPTED"
    echo "⚠️  即将删除明文钱包..."
    read -p "确认删除明文钱包? (yes/no): " confirm
    
    if [ "$confirm" == "yes" ]; then
        shred -u "$WALLET_PLAIN"
        echo "✅ 明文钱包已安全删除"
    fi
}

# 解密钱包（临时使用）
decrypt_temp() {
    if [ ! -f "$WALLET_ENCRYPTED" ]; then
        echo "❌ 未找到加密钱包"
        return 1
    fi
    
    # 解密到临时位置（内存）
    TMP_WALLET="/dev/shm/trading-bot-$$.json"
    
    age -d -i "$WALLET_KEY" "$WALLET_ENCRYPTED" > "$TMP_WALLET"
    
    echo "✅ 钱包已临时解密: $TMP_WALLET"
    echo "⚠️  此文件在内存中，重启后自动删除"
    echo "⚠️  使用完毕请运行: rm $TMP_WALLET"
    echo "$TMP_WALLET"
}

# 查看钱包地址（不解密完整私钥）
show_address() {
    if [ ! -f "$WALLET_ENCRYPTED" ]; then
        echo "❌ 未找到加密钱包"
        return 1
    fi
    
    # 临时解密并显示地址
    TMP=$(mktemp)
    age -d -i "$WALLET_KEY" "$WALLET_ENCRYPTED" > "$TMP"
    
    # 使用 Python 显示地址
    python3 -c "
import json
from solders.keypair import Keypair

with open('$TMP', 'r') as f:
    data = json.load(f)

keypair = Keypair.from_bytes(bytes(data))
print(f'📍 钱包地址: {str(keypair.pubkey())}')
"
    
    rm "$TMP"
}

# 使用说明
usage() {
    echo "用法: $0 <command>"
    echo ""
    echo "命令:"
    echo "  generate      - 生成加密密钥（首次使用）"
    echo "  encrypt       - 加密钱包文件"
    echo "  decrypt       - 临时解密到内存"
    echo "  address       - 查看钱包地址"
    echo "  help          - 显示此帮助"
}

# 主逻辑
case "$1" in
    generate)
        generate_key
        ;;
    encrypt)
        encrypt
        ;;
    decrypt)
        decrypt_temp
        ;;
    address)
        show_address
        ;;
    help|*)
        usage
        ;;
esac
