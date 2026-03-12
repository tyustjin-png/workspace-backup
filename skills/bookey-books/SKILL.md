# Bookey 书籍摘要下载技能

## 触发条件
- 需要快速了解某本书的核心内容
- 找不到完整版电子书
- 想预览一本书再决定是否深入阅读

## 资源说明
Bookey (cdn.bookey.app) 提供免费书籍摘要PDF下载，通常包含书籍精华内容，页数在100-300页之间。

## 执行步骤

1. **确定书名英文版**
   - 将书名转为英文小写，空格用连字符替换
   - 例：`Elon Musk` → `elon-musk`

2. **构建下载URL**
   ```
   https://cdn.bookey.app/files/pdf/book/en/{book-name}.pdf
   ```

3. **下载文件**
   ```bash
   curl -L -o "{书名}_摘要.pdf" "https://cdn.bookey.app/files/pdf/book/en/{book-name}.pdf"
   ```

4. **验证下载**
   ```bash
   file "{书名}_摘要.pdf"  # 确认是PDF格式
   ls -lh "{书名}_摘要.pdf"  # 检查文件大小
   ```

## 示例

```bash
# 下载《Liftoff》(SpaceX早期史)
curl -L -o "Liftoff_摘要.pdf" "https://cdn.bookey.app/files/pdf/book/en/liftoff.pdf"

# 下载《Power Play》(特斯拉创业史)
curl -L -o "PowerPlay_摘要.pdf" "https://cdn.bookey.app/files/pdf/book/en/power-play.pdf"
```

## 限制
- 只有英文版摘要
- 2024年新书可能还没收录
- 是摘要版，不是完整版

## 备选资源
- LibGen: libgen.is (可能有网络限制)
- Z-Library: z-lib.io (有反爬保护)
- Anna's Archive: annas-archive.org

---
*创建于 2026-03-10，来源：马斯克书籍下载任务*
