"""
视频合成模块
使用 MoviePy 或 FFmpeg 生成视频
"""
import os
import re
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
import tempfile

try:
    from moviepy.editor import (
        AudioFileClip, ImageClip, TextClip, CompositeVideoClip,
        ColorClip, concatenate_videoclips
    )
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False


@dataclass  
class VideoConfig:
    """视频配置"""
    width: int = 1080
    height: int = 1920  # 9:16 竖屏
    fps: int = 30
    bg_color: str = "#1a1a2e"  # 深色背景
    text_color: str = "white"
    highlight_color: str = "#ffd700"  # 金色高亮
    font: str = "SimHei"  # 中文字体
    font_size: int = 48
    subtitle_font_size: int = 36


class VideoComposer:
    """视频合成器"""
    
    def __init__(self, config: Optional[VideoConfig] = None):
        self.config = config or VideoConfig()
        
        if not HAS_MOVIEPY:
            print("警告: MoviePy 未安装，将使用 FFmpeg 模式")
    
    def compose_simple(self, 
                       audio_path: str,
                       script_text: str,
                       output_path: str,
                       book_title: str = "",
                       highlights: List[str] = None) -> str:
        """
        简单合成：背景色 + 字幕 + 音频
        
        Args:
            audio_path: 音频文件路径
            script_text: 脚本文本（用于字幕）
            output_path: 输出视频路径
            book_title: 书名（显示在顶部）
            highlights: 金句列表（用于画面强调）
        
        Returns:
            输出视频路径
        """
        if HAS_MOVIEPY:
            return self._compose_with_moviepy(
                audio_path, script_text, output_path, 
                book_title, highlights or []
            )
        else:
            return self._compose_with_ffmpeg(
                audio_path, script_text, output_path
            )
    
    def _compose_with_moviepy(self, audio_path: str, script_text: str,
                               output_path: str, book_title: str,
                               highlights: List[str]) -> str:
        """使用 MoviePy 合成"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 加载音频
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # 创建背景
        bg = ColorClip(
            size=(self.config.width, self.config.height),
            color=self._hex_to_rgb(self.config.bg_color)
        ).set_duration(duration)
        
        clips = [bg]
        
        # 添加书名标题
        if book_title:
            title_clip = TextClip(
                f"📖 {book_title}",
                fontsize=self.config.font_size + 10,
                color=self.config.highlight_color,
                font=self.config.font,
                size=(self.config.width - 100, None),
                method='caption'
            ).set_position(('center', 150)).set_duration(duration)
            clips.append(title_clip)
        
        # 分段显示文字（简单实现）
        sentences = self._split_sentences(script_text)
        sentence_duration = duration / len(sentences) if sentences else duration
        
        current_time = 0
        for sentence in sentences:
            text_clip = TextClip(
                sentence,
                fontsize=self.config.subtitle_font_size,
                color=self.config.text_color,
                font=self.config.font,
                size=(self.config.width - 100, None),
                method='caption',
                align='center'
            ).set_position(('center', 'center')).set_start(current_time).set_duration(sentence_duration)
            clips.append(text_clip)
            current_time += sentence_duration
        
        # 合成
        video = CompositeVideoClip(clips)
        video = video.set_audio(audio)
        
        # 输出
        video.write_videofile(
            output_path,
            fps=self.config.fps,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            preset='medium'
        )
        
        return output_path
    
    def _compose_with_ffmpeg(self, audio_path: str, script_text: str,
                              output_path: str) -> str:
        """使用 FFmpeg 合成（备用方案）"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 获取音频时长
        duration_cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        duration = float(subprocess.check_output(duration_cmd).decode().strip())
        
        # 创建带字幕的视频
        # 使用 drawtext 滤镜
        text_escaped = script_text[:200].replace("'", "\\'").replace(":", "\\:")
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'color=c=0x1a1a2e:s={self.config.width}x{self.config.height}:d={duration}',
            '-i', audio_path,
            '-vf', f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='{text_escaped}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/2",
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            output_path
        ]
        
        subprocess.run(cmd, check=True)
        return output_path
    
    def compose_with_images(self,
                            audio_path: str,
                            images: List[str],
                            output_path: str,
                            subtitles: List[dict] = None) -> str:
        """
        图片轮播 + 字幕模式
        
        Args:
            audio_path: 音频路径
            images: 图片路径列表
            output_path: 输出路径
            subtitles: 字幕列表 [{'text': '', 'start': 0, 'end': 5}]
        """
        if not HAS_MOVIEPY:
            raise ImportError("图片模式需要 MoviePy")
        
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # 每张图片的时长
        img_duration = duration / len(images) if images else duration
        
        clips = []
        for i, img_path in enumerate(images):
            img_clip = ImageClip(img_path).set_duration(img_duration)
            img_clip = img_clip.resize(height=self.config.height)
            img_clip = img_clip.set_position('center')
            img_clip = img_clip.set_start(i * img_duration)
            clips.append(img_clip)
        
        video = CompositeVideoClip(clips, size=(self.config.width, self.config.height))
        video = video.set_audio(audio)
        video.write_videofile(output_path, fps=self.config.fps)
        
        return output_path
    
    def _split_sentences(self, text: str) -> List[str]:
        """分割句子"""
        # 按标点分割
        sentences = re.split(r'[。！？\n]', text)
        # 过滤空句子，限制长度
        result = []
        for s in sentences:
            s = s.strip()
            if s:
                # 长句子再分割
                if len(s) > 50:
                    parts = re.split(r'[，、；]', s)
                    result.extend([p.strip() for p in parts if p.strip()])
                else:
                    result.append(s)
        return result
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """十六进制颜色转 RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def add_subtitles_srt(self, video_path: str, srt_path: str, 
                          output_path: str) -> str:
        """使用 SRT 字幕文件添加字幕"""
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&HFFFFFF&'",
            '-c:a', 'copy',
            output_path
        ]
        subprocess.run(cmd, check=True)
        return output_path


def compose_video(audio_path: str, script_text: str, output_path: str,
                  book_title: str = "", highlights: List[str] = None) -> str:
    """便捷函数"""
    composer = VideoComposer()
    return composer.compose_simple(
        audio_path, script_text, output_path,
        book_title, highlights
    )


if __name__ == '__main__':
    # 测试
    print("视频合成模块已加载")
    print(f"MoviePy 可用: {HAS_MOVIEPY}")
