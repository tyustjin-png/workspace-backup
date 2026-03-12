# 无头浏览器配置技能

## 触发条件
- 服务器无图形界面但需要运行浏览器
- 需要自动化网页操作（登录、截图、爬取）
- Playwright/Puppeteer启动失败

## 问题诊断
```bash
# 检查是否有显示器
echo $DISPLAY  # 空=无图形界面

# 检查浏览器依赖
ldd /path/to/chromium | grep "not found"
```

## 解决方案

### 1. 安装虚拟显示器 (xvfb)
```bash
apt update && apt install -y xvfb
```

### 2. 安装 Playwright 和浏览器
```bash
pip install playwright
playwright install chromium
playwright install-deps  # 安装系统依赖
```

### 3. 手动安装缺失依赖（如果playwright install-deps失败）
```bash
apt install -y \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libdrm2 \
  libxkbcommon0 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libasound2
```

### 4. 配置浏览器选项
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,  # 必须
        args=['--no-sandbox', '--disable-setuid-sandbox']  # 在root下运行需要
    )
    page = browser.new_page()
    page.goto('https://example.com')
    # ...操作
    browser.close()
```

## 验证
```bash
# 使用xvfb-run测试
xvfb-run python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    page.goto('https://example.com')
    print('Success:', page.title())
    browser.close()
"
```

## 常见错误
- `No usable sandbox`: 添加 `--no-sandbox` 参数
- `Missing X server`: 安装 xvfb
- `libXXX.so not found`: 运行 `playwright install-deps`

---
*创建于 2026-03-10，来源：LinkedIn密码验证任务*
