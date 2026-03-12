#!/usr/bin/env python3
"""
自动从看板API获取z值
看板地址: http://8.216.6.8/
API接口: http://8.216.6.8/api/current
"""
import json
import requests
import sys
from datetime import datetime

DASHBOARD_API = "http://8.216.6.8/api/current"

def get_z_value():
    """从看板API获取当前z值"""
    try:
        response = requests.get(DASHBOARD_API, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'error' in data:
            print(f"❌ API返回错误: {data['error']}", file=sys.stderr)
            return None
        
        score = data.get('score', {})
        z_value = score.get('s_normalized')
        dca_mult = score.get('dca_mult')
        price = score.get('price')
        last_update = data.get('last_update')
        
        if z_value is None:
            print(f"❌ API数据中缺少 s_normalized 字段", file=sys.stderr)
            return None
        
        # 打印详细信息
        print(f"✅ 成功获取z值")
        print(f"📅 数据时间: {last_update}")
        print(f"💰 BTC价格: ${price:,.2f}")
        print(f"📊 z值: {z_value}")
        print(f"📈 定投倍数: {dca_mult}x")
        
        return {
            'z_value': z_value,
            'dca_mult': dca_mult,
            'price': price,
            'last_update': last_update,
            'fetched_at': datetime.now().isoformat()
        }
        
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时: {DASHBOARD_API}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ 未知错误: {e}", file=sys.stderr)
        return None

def save_z_value(data, filepath='/root/.openclaw/workspace/xiaoding/data/current_z_value.json'):
    """保存z值到文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 z值已保存到: {filepath}")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    data = get_z_value()
    if data:
        save_z_value(data)
        # 返回z值（供其他脚本调用）
        print(f"\n当前z值: {data['z_value']}")
        sys.exit(0)
    else:
        print("❌ 获取z值失败", file=sys.stderr)
        sys.exit(1)
