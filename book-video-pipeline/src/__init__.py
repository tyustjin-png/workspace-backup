"""
Book Video Pipeline
AI 驱动的书籍视频生成流水线
"""
from .book_extractor import BookExtractor, extract_book
from .script_generator import ScriptGenerator, VideoScript
from .tts_engine import TTSEngine, TTSConfig, synthesize_script
from .video_composer import VideoComposer, VideoConfig, compose_video
from .pipeline import BookVideoPipeline

__version__ = "0.1.0"
__all__ = [
    'BookExtractor', 'extract_book',
    'ScriptGenerator', 'VideoScript', 
    'TTSEngine', 'TTSConfig', 'synthesize_script',
    'VideoComposer', 'VideoConfig', 'compose_video',
    'BookVideoPipeline'
]
