# 📚 Book Video Pipeline

AI 驱动的书籍视频生成流水线：从书籍内容到抖音视频，全流程自动化。

## 🎯 核心功能

```
书籍内容 → AI 脚本 → TTS 配音 → 视频合成 → 发布就绪
```

| 环节 | AI 程度 | 工具 |
|-----|--------|------|
| 内容提取 | 100% | PDF 解析 / 手动输入 |
| 脚本生成 | 100% | Claude API |
| 语音合成 | 100% | Edge TTS (免费) |
| 视频合成 | 100% | MoviePy / FFmpeg |
| 发布 | 80% | 手动 / RPA |

## 🚀 快速开始

### 1. 安装依赖

```bash
cd book-video-pipeline
pip install -r requirements.txt

# 视频处理需要 FFmpeg
# Mac: brew install ffmpeg
# Ubuntu: apt install ffmpeg
```

### 2. 配置 API Key

```bash
export ANTHROPIC_API_KEY="your-claude-api-key"
```

### 3. 运行测试

```bash
python run_test.py
```

### 4. 正式使用

```bash
# 方式1: 命令行
python src/pipeline.py \
  --source manual \
  --title "原则" \
  --author "瑞·达利欧" \
  --content-file books/yuanze.txt \
  --voice zh-CN-YunxiNeural

# 方式2: Python 调用
from src.pipeline import BookVideoPipeline

pipeline = BookVideoPipeline()
result = pipeline.run(
    book_source='manual',
    book_title='原则',
    book_author='瑞·达利欧',
    book_content='...',
)
```

## 📁 项目结构

```
book-video-pipeline/
├── src/
│   ├── book_extractor.py    # 书籍内容提取
│   ├── script_generator.py  # AI 脚本生成
│   ├── tts_engine.py        # TTS 语音合成
│   ├── video_composer.py    # 视频合成
│   └── pipeline.py          # 主流程控制
├── templates/
│   └── script_prompt.md     # 脚本生成 Prompt
├── config/
│   └── settings.yaml        # 配置文件
├── books/                   # 放书籍文件
├── output/
│   ├── scripts/            # 生成的脚本
│   ├── audio/              # 生成的音频
│   └── video/              # 生成的视频
├── requirements.txt
├── run_test.py
└── README.md
```

## 🎙️ TTS 声音选择

### Edge TTS (免费推荐)

| 声音 | 类型 | 风格 |
|------|------|------|
| zh-CN-YunxiNeural | 男声 | 自然对话 |
| zh-CN-YunjianNeural | 男声 | 新闻播音 |
| zh-CN-XiaoxiaoNeural | 女声 | 助手风格 |
| zh-CN-XiaoyiNeural | 女声 | 活泼青春 |

```bash
# 列出所有中文声音
python -c "import asyncio; import edge_tts; print(asyncio.run(edge_tts.list_voices()))" | grep zh-CN
```

## 📝 脚本 Prompt 优化

编辑 `templates/script_prompt.md` 调整生成风格：

- **钩子类型**: 反常识 / 痛点 / 悬念 / 数据
- **内容结构**: 观点数量、案例风格
- **语言风格**: 口语化程度、金句密度

## 🎬 视频风格

### 当前支持

- **纯色背景 + 字幕**: 简单快速，适合起步
- **图片轮播 + 字幕**: 需要提供图片素材

### 计划支持

- [ ] 数字人口播 (HeyGen / D-ID 对接)
- [ ] AI 生成配图 (Midjourney / DALL-E)
- [ ] 自动剪辑 (Runway / Pika)

## 📱 抖音发布

### 手动发布 (推荐起步)

1. 视频生成在 `output/video/`
2. 复制到手机发布
3. 标题/标签在脚本 JSON 中

### RPA 自动化 (进阶)

```python
# 需要额外配置，使用 Airtest / uiautomator2
# 暂未集成，后续版本支持
```

## 🔧 配置说明

编辑 `config/settings.yaml`:

```yaml
api:
  claude:
    model: "claude-sonnet-4-20250514"  # 或 claude-3-opus
  tts:
    provider: "edge"           # edge / elevenlabs
    edge:
      voice: "zh-CN-YunxiNeural"
      
video:
  width: 1080
  height: 1920               # 9:16 竖屏
  font_size: 48
```

## 💰 成本估算

| 项目 | 每条视频成本 | 月 60 条成本 |
|------|------------|-------------|
| Claude API | ¥0.5-1.0 | ¥30-60 |
| Edge TTS | 免费 | 免费 |
| 视频合成 | 本地免费 | 免费 |
| **合计** | **¥0.5-1.0** | **¥30-60** |

## 🐛 常见问题

### Q: MoviePy 安装失败？
```bash
# 确保有 FFmpeg
ffmpeg -version

# Mac 用户
brew install ffmpeg

# 或者跳过 MoviePy，使用纯 FFmpeg 模式
```

### Q: 中文字体显示问题？
```bash
# Ubuntu 安装中文字体
apt install fonts-wqy-microhei fonts-wqy-zenhei
```

### Q: 音频生成报错？
```bash
# Edge TTS 需要网络连接
# 检查网络代理设置
```

## 📈 后续计划

- [ ] 数字人集成 (HeyGen API)
- [ ] AI 配图 (Midjourney / DALL-E)
- [ ] 抖音 RPA 发布
- [ ] 数据追踪 (播放量/转化率)
- [ ] 批量处理 UI

---

Made with 🐉 by 紫龙
