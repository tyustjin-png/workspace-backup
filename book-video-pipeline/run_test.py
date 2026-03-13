#!/usr/bin/env python3
"""
快速测试脚本 - 用一本书测试完整流程
"""
import os
import sys

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline import BookVideoPipeline


def test_pipeline():
    """测试完整流程"""
    
    # 测试书籍信息
    test_book = {
        'title': '原则',
        'author': '瑞·达利欧',
        'content': '''
《原则》是桥水基金创始人瑞·达利欧（Ray Dalio）40多年人生与事业经验的总结。

核心理念：

1. 拥抱现实并应对现实
- 做一个超级现实主义者
- 接受事实，而不是抱怨事实
- 痛苦 + 反思 = 进步

2. 用五步流程实现目标
- 设定清晰的目标
- 发现阻碍目标的问题
- 诊断问题的根本原因
- 设计解决方案
- 执行方案

3. 做到极度透明和极度开放
- 诚实说出你的想法
- 欢迎批评和建议
- 创建创意择优的文化

4. 理解人与人的不同
- 人的大脑结构不同
- 了解自己和他人的优缺点
- 把合适的人放在合适的位置

5. 有效决策
- 相信可信度加权的决策
- 知道什么时候不该做决策
- 用系统化的方法做决策

这本书被比尔·盖茨称为"值得反复阅读的书"，它不仅适用于投资和管理，
更是一套可以应用于人生各个领域的思维框架。
'''
    }
    
    # 创建 pipeline
    pipeline = BookVideoPipeline(output_dir='output')
    
    # 运行（先跳过视频，测试脚本和音频）
    print("🚀 开始测试流程...")
    print("   （首次运行会跳过视频生成，仅测试脚本和音频）\n")
    
    result = pipeline.run(
        book_source='manual',
        book_title=test_book['title'],
        book_author=test_book['author'],
        book_content=test_book['content'],
        voice='zh-CN-YunxiNeural',
        skip_video=True  # 先跳过视频测试
    )
    
    print("\n" + "=" * 50)
    print("📊 测试结果")
    print("=" * 50)
    print(f"脚本字数: {result['script']['word_count']}")
    print(f"预估时长: {result['script']['estimated_duration']} 分钟")
    print(f"实际音频: {result['duration']:.1f} 秒")
    print(f"\n标题建议:")
    for i, title in enumerate(result['script']['titles'], 1):
        print(f"  {i}. {title}")
    print(f"\n金句:")
    for highlight in result['script']['highlights']:
        print(f"  • {highlight}")
    print(f"\n标签: {' '.join(['#' + t for t in result['script']['tags']])}")
    
    return result


if __name__ == '__main__':
    # 检查环境
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("⚠️  请先设置 ANTHROPIC_API_KEY 环境变量")
        print("   export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)
    
    test_pipeline()
