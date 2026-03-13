"""
Book Video Pipeline - 主流程控制
一键从书籍生成抖音视频
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from book_extractor import extract_book, BookExtractor
from script_generator import ScriptGenerator, VideoScript
from tts_engine import TTSEngine, TTSConfig, synthesize_script
from video_composer import VideoComposer, VideoConfig, compose_video


class BookVideoPipeline:
    """书籍视频生成流水线"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 子目录
        self.scripts_dir = self.output_dir / "scripts"
        self.audio_dir = self.output_dir / "audio"
        self.video_dir = self.output_dir / "video"
        
        for d in [self.scripts_dir, self.audio_dir, self.video_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        self.extractor = BookExtractor()
        self.script_generator = None  # 延迟初始化
        self.tts_engine = None
        self.video_composer = None
    
    def run(self, 
            book_source: str,
            book_title: str = None,
            book_author: str = None,
            book_content: str = None,
            voice: str = "zh-CN-YunxiNeural",
            skip_video: bool = False) -> dict:
        """
        运行完整流水线
        
        Args:
            book_source: 书籍来源 ('manual' / 文件路径 / 'isbn:xxx')
            book_title: 书名（manual 模式必填）
            book_author: 作者
            book_content: 内容/简介（manual 模式必填）
            voice: TTS 声音
            skip_video: 是否跳过视频生成（调试用）
        
        Returns:
            {
                'book_info': {...},
                'script': {...},
                'audio_path': '...',
                'video_path': '...',
                'duration': 123.4
            }
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("=" * 50)
        print("📚 Book Video Pipeline")
        print("=" * 50)
        
        # Step 1: 提取书籍内容
        print("\n[1/4] 提取书籍内容...")
        
        if book_source == 'manual':
            book_info = self.extractor.from_manual_input(
                book_title or '未命名',
                book_author or '未知',
                book_content or ''
            )
        elif os.path.exists(book_source):
            book_info = self.extractor.extract_from_file(book_source)
            if book_title:
                book_info['title'] = book_title
            if book_author:
                book_info['author'] = book_author
        else:
            raise ValueError(f"无法识别的书籍来源: {book_source}")
        
        safe_title = self._safe_filename(book_info['title'])
        print(f"   书名: {book_info['title']}")
        print(f"   作者: {book_info['author']}")
        print(f"   内容长度: {len(book_info['content'])} 字符")
        
        # Step 2: 生成脚本
        print("\n[2/4] 生成视频脚本...")
        
        if not self.script_generator:
            self.script_generator = ScriptGenerator()
        
        script = self.script_generator.generate(book_info)
        
        # 保存脚本
        script_path = self.scripts_dir / f"{safe_title}_{timestamp}.json"
        self.script_generator.save_script(script, str(script_path))
        
        print(f"   字数: {script.word_count}")
        print(f"   预估时长: {script.estimated_duration} 分钟")
        print(f"   标题: {script.titles[0]}")
        print(f"   脚本已保存: {script_path}")
        
        # Step 3: 合成语音
        print("\n[3/4] 合成语音...")
        
        audio_path = self.audio_dir / f"{safe_title}_{timestamp}.mp3"
        
        if not self.tts_engine:
            self.tts_engine = TTSEngine(TTSConfig(voice=voice, rate="+10%"))
        
        self.tts_engine.synthesize(script.full_script, str(audio_path))
        
        audio_duration = self.tts_engine.get_audio_duration(str(audio_path))
        print(f"   音频已生成: {audio_path}")
        print(f"   实际时长: {audio_duration:.1f} 秒")
        
        # Step 4: 合成视频
        video_path = None
        if not skip_video:
            print("\n[4/4] 合成视频...")
            
            video_path = self.video_dir / f"{safe_title}_{timestamp}.mp4"
            
            if not self.video_composer:
                self.video_composer = VideoComposer()
            
            self.video_composer.compose_simple(
                str(audio_path),
                script.full_script,
                str(video_path),
                book_title=book_info['title'],
                highlights=script.highlights
            )
            
            print(f"   视频已生成: {video_path}")
        else:
            print("\n[4/4] 跳过视频生成")
        
        # 完成
        print("\n" + "=" * 50)
        print("✅ 生成完成！")
        print("=" * 50)
        
        result = {
            'book_info': book_info,
            'script': asdict(script),
            'script_path': str(script_path),
            'audio_path': str(audio_path),
            'video_path': str(video_path) if video_path else None,
            'duration': audio_duration
        }
        
        # 保存结果摘要
        summary_path = self.output_dir / f"{safe_title}_{timestamp}_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    
    def _safe_filename(self, name: str) -> str:
        """生成安全的文件名"""
        # 移除不安全字符
        safe = "".join(c for c in name if c.isalnum() or c in '._- ')
        return safe[:50].strip() or "untitled"
    
    def batch_run(self, books: list, **kwargs) -> list:
        """批量处理多本书"""
        results = []
        for i, book in enumerate(books, 1):
            print(f"\n{'#' * 50}")
            print(f"# 处理第 {i}/{len(books)} 本: {book.get('title', '未知')}")
            print(f"{'#' * 50}")
            
            try:
                result = self.run(
                    book_source='manual',
                    book_title=book.get('title'),
                    book_author=book.get('author'),
                    book_content=book.get('content'),
                    **kwargs
                )
                results.append({'status': 'success', **result})
            except Exception as e:
                print(f"❌ 处理失败: {e}")
                results.append({'status': 'error', 'error': str(e), 'book': book})
        
        return results


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='书籍视频生成流水线')
    parser.add_argument('--source', '-s', required=True,
                        help='书籍来源: manual / 文件路径')
    parser.add_argument('--title', '-t', help='书名')
    parser.add_argument('--author', '-a', help='作者')
    parser.add_argument('--content', '-c', help='书籍内容/简介')
    parser.add_argument('--content-file', '-f', help='内容文件路径')
    parser.add_argument('--voice', '-v', default='zh-CN-YunxiNeural',
                        help='TTS 声音 (默认: zh-CN-YunxiNeural)')
    parser.add_argument('--output', '-o', default='output',
                        help='输出目录 (默认: output)')
    parser.add_argument('--skip-video', action='store_true',
                        help='跳过视频生成')
    
    args = parser.parse_args()
    
    # 读取内容文件
    content = args.content
    if args.content_file:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    
    # 运行流水线
    pipeline = BookVideoPipeline(output_dir=args.output)
    result = pipeline.run(
        book_source=args.source,
        book_title=args.title,
        book_author=args.author,
        book_content=content,
        voice=args.voice,
        skip_video=args.skip_video
    )
    
    print(f"\n📁 输出文件:")
    print(f"   脚本: {result['script_path']}")
    print(f"   音频: {result['audio_path']}")
    if result['video_path']:
        print(f"   视频: {result['video_path']}")


if __name__ == '__main__':
    main()
