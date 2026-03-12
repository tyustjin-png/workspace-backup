# 编码规范与最佳实践

## 🎯 总则

1. **简单优于复杂**: 能用 10 行解决的不用 100 行
2. **可读性优先**: 代码是写给人看的，顺便给机器执行
3. **防御式编程**: 假设所有外部输入都是恶意的
4. **文档同步**: 代码变了，注释也要改

## 🐍 Python 规范

### 命名规范
```python
# 变量、函数: snake_case
def calculate_profit_rate(buy_price, sell_price):
    profit_rate = (sell_price - buy_price) / buy_price
    return profit_rate

# 类名: PascalCase
class PositionManager:
    pass

# 常量: UPPER_SNAKE_CASE
MAX_SLIPPAGE = 0.05
DEFAULT_TIMEOUT = 30
```

### 错误处理
```python
# ✅ 推荐：具体异常 + 日志
import logging

try:
    price = fetch_price_from_api(token_address)
except requests.exceptions.Timeout:
    logging.error(f"API timeout for {token_address}")
    price = None
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    raise

# ❌ 避免：裸 except
try:
    do_something()
except:  # 太宽泛，会隐藏 bug
    pass
```

### 函数设计
```python
# ✅ 单一职责，明确输入输出
def calculate_score(liquidity: float, holders: int, age_hours: int) -> int:
    """
    计算 Meme 币评分
    
    Args:
        liquidity: 流动性（美元）
        holders: 持有人数量
        age_hours: 创建时长（小时）
    
    Returns:
        评分 (0-100)
    """
    score = 0
    if liquidity > 100000:
        score += 30
    if holders > 100:
        score += 20
    # ...
    return min(score, 100)

# ❌ 避免：功能杂糅
def do_everything(data):
    # 既解析数据，又计算评分，又发送通知...
    pass
```

### 文件结构
```python
# 标准脚本模板

#!/usr/bin/env python3
"""
脚本功能简述
"""

import logging
import sys
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 常量
API_ENDPOINT = "https://api.dexscreener.com/latest/..."
TIMEOUT = 30

# 函数定义
def main():
    """主函数"""
    try:
        # 业务逻辑
        pass
    except KeyboardInterrupt:
        logging.info("User interrupted")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 📜 Shell 脚本规范

### 基本结构
```bash
#!/usr/bin/env bash
set -euo pipefail  # 错误即退出，未定义变量报错，管道失败传播

# 变量：全大写
MEMORY_THRESHOLD=80
LOG_FILE="/tmp/monitor.log"

# 函数：snake_case
check_memory_usage() {
    local usage
    usage=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
    
    if [[ $usage -gt $MEMORY_THRESHOLD ]]; then
        echo "⚠️ Memory usage: ${usage}%"
        return 1
    fi
    return 0
}

# 主逻辑
main() {
    if check_memory_usage; then
        echo "✅ Memory OK"
    else
        echo "🚨 Memory alert!" > "$LOG_FILE"
    fi
}

main "$@"
```

### 安全实践
```bash
# ✅ 引用变量防止空格问题
file="my file.txt"
rm "$file"  # 正确
# rm $file  # 错误：会被解析为 rm my file.txt

# ✅ 检查命令是否存在
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required"
    exit 1
fi

# ✅ 临时文件用 mktemp
temp_file=$(mktemp)
trap "rm -f $temp_file" EXIT  # 退出时自动清理
```

## 📄 JSON 数据规范

### 文件格式
```json
{
  "positions": [
    {
      "symbol": "PEPE",
      "address": "0x...",
      "buyPrice": 0.0000012,
      "currentPrice": 0.0000015,
      "amount": 1000000,
      "stopLoss": 0.0000010,
      "takeProfit": 0.0000020,
      "buyTime": "2026-02-08T10:00:00Z"
    }
  ],
  "lastUpdate": "2026-02-08T20:19:00Z"
}
```

### 字段命名
- **驼峰命名**: `buyPrice`, `stopLoss` (JSON 标准)
- **时间戳**: ISO 8601 格式 `YYYY-MM-DDTHH:MM:SSZ`
- **金额**: 浮点数，避免字符串

## 📝 Markdown 文档规范

### 文件命名
- **小写 + 连字符**: `claude-code-context-loss-analysis.md`
- **日期格式**: `memory/2026-02-08.md`

### 结构规范
```markdown
# 一级标题 - 文档标题

> 简短描述（可选）

## 二级标题 - 主要章节

### 三级标题 - 小节

正文内容...

**重点**：使用粗体  
*斜体*：用于强调  
`代码`：行内代码  

```代码块
# 带语法高亮
```

- 列表项 1
- 列表项 2

---

**最后更新**: 2026-02-08
```

### 特殊约定
```markdown
# 状态标记
- ✅ 完成
- 🚧 进行中
- ⏸️ 暂停
- ❌ 失败
- ⚠️ 警告

# Emoji 使用
- 📊 数据/统计
- 🔧 技术/工具
- 💡 建议/想法
- 🚨 告警/紧急
- 📝 笔记/记录
```

## 🔄 Git 提交规范

### 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 重构（不改变功能）
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具变更

### 示例
```
feat(meme-monitor): 添加流动性过滤器

- 新增最小流动性阈值配置
- 过滤掉流动性 < $50K 的代币
- 减少误报率约 30%

Closes #123
```

## 🚫 禁止事项

1. **硬编码敏感信息**
   ```python
   # ❌ 绝对禁止
   API_KEY = "sk-..."
   PRIVATE_KEY = "0x..."
   
   # ✅ 使用环境变量
   import os
   API_KEY = os.getenv("DEXSCREENER_API_KEY")
   ```

2. **忽略错误**
   ```python
   # ❌ 危险
   try:
       critical_operation()
   except:
       pass  # 静默失败，问题难以发现
   ```

3. **魔法数字**
   ```python
   # ❌ 难以理解
   if profit_rate > 0.3:
       sell()
   
   # ✅ 使用常量
   TAKE_PROFIT_RATE = 0.3  # 30% 止盈
   if profit_rate > TAKE_PROFIT_RATE:
       sell()
   ```

## ✅ 代码审查清单

提交代码前自查：

- [ ] 代码是否遵循命名规范？
- [ ] 是否有足够的错误处理？
- [ ] 是否有必要的日志输出？
- [ ] 敏感信息是否妥善保护？
- [ ] 是否更新了相关文档？
- [ ] 临时文件是否清理？
- [ ] 是否测试过边界情况？

---

**版本**: v1.0  
**最后更新**: 2026-02-08 20:19  
**维护者**: 紫龙
