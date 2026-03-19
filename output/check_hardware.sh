#!/bin/bash
# EPYC CPU 通道检测 + 硬盘SMART信息一键获取
# 在Ubuntu系统上运行：sudo bash check_hardware.sh

echo "========================================="
echo "  EPYC 服务器硬件检测脚本"
echo "========================================="
echo ""

# CPU信息
echo "📌 CPU 信息"
echo "-----------------------------------------"
lscpu | grep -E "Model name|Socket|Core|Thread|NUMA"
echo ""

# 内存通道检测
echo "📌 内存通道检测"
echo "-----------------------------------------"
dmidecode -t memory | grep -E "Number Of Devices|Size|Speed|Manufacturer|Part Number|Locator" | head -40
echo ""
echo "已用插槽数："
dmidecode -t memory | grep "Size:" | grep -v "No Module" | wc -l
echo "空插槽数："
dmidecode -t memory | grep "No Module" | wc -l
echo ""

# 硬盘SMART信息
echo "📌 硬盘 SMART 信息"
echo "-----------------------------------------"
if command -v smartctl &> /dev/null; then
    for disk in $(lsblk -d -n -o NAME,TYPE | grep disk | awk '{print $1}'); do
        echo ""
        echo "--- /dev/$disk ---"
        smartctl -a /dev/$disk 2>/dev/null | grep -E "Model|Serial|Capacity|Power_On|Wear|Written|Temperature|Percentage Used"
    done
else
    echo "请先安装 smartmontools: sudo apt install smartmontools"
fi

echo ""
echo "========================================="
echo "  检测完成，请截图保存"
echo "========================================="
