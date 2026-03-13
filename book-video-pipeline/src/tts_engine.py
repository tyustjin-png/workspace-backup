"""
TTS 语音合成模块
支持 Edge TTS (免费)、ElevenLabs、火山引擎
"""
import os
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import subprocess
import tempfile

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False


@dataclass
class TTSConfig:
    """TTS 配置"""
    provider: str = "edge"  # edge / elevenlabs / volcano
    voice: str = "zh-CN-YunxiNeural"  # Edge TTS 声音
    rate: str = "+10%"  # 语速调整
    pitch: str = "+0Hz"  # 音调调整


class TTSEngine:
    """语音合成引擎"""
    
    # 推荐的中文声音
    RECOMMENDED_VOICES = {
        'edge': {
            'male': [
                'zh-CN-YunxiNeural',      # 男声，自然
                'zh-CN-YunjianNeural',    # 男声，新闻播音
                'zh-CN-YunyangNeural',    # 男声，专业
            ],
            'female': [
                'zh-CN-XiaoxiaoNeural',   # 女声，助手风格
                'zh-CN-XiaoyiNeural',     # 女声，活泼
                'zh-CN-XiaochenNeural',   # 女声，温柔
            ]
        }
    }
    
    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()
        
        if self.config.provider == "edge" and not HAS_EDGE_TTS:
            raise ImportError("需要安装 edge-tts: pip install edge-tts")
    
    async def _synthesize_edge(self, text: str, output_path: str) -> str:
        """使用 Edge TTS 合成"""
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.config.voice,
            rate=self.config.rate,
            pitch=self.config.pitch
        )
        await communicate.save(output_path)
        return output_path
    
    def synthesize(self, text: str, output_path: str) -> str:
        """
        合成语音
        
        Args:
            text: 要合成的文本
            output_path: 输出音频文件路径 (.mp3)
        
        Returns:
            输出文件路径
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if self.config.provider == "edge":
            return asyncio.run(self._synthesize_edge(text, output_path))
        elif self.config.provider == "elevenlabs":
            return self._synthesize_elevenlabs(text, output_path)
        elif self.config.provider == "volcano":
            return self._synthesize_volcano(text, output_path)
        else:
            raise ValueError(f"不支持的 TTS 提供商: {self.config.provider}")
    
    def _synthesize_elevenlabs(self, text: str, output_path: str) -> str:
        """使用 ElevenLabs 合成"""
        try:
            from elevenlabs import generate, save, set_api_key
            
            api_key = os.environ.get('ELEVENLABS_API_KEY')
            if not api_key:
                raise ValueError("需要设置 ELEVENLABS_API_KEY 环境变量")
            
            set_api_key(api_key)
            audio = generate(
                text=text,
                voice=self.config.voice,
                model="eleven_multilingual_v2"
            )
            save(audio, output_path)
            return output_path
        except ImportError:
            raise ImportError("需要安装 elevenlabs: pip install elevenlabs")
    
    def _synthesize_volcano(self, text: str, output_path: str) -> str:
        """使用火山引擎 TTS"""
        # 火山引擎需要 SDK，这里提供占位实现
        raise NotImplementedError("火山引擎 TTS 需要单独配置 SDK")
    
    def get_audio_duration(self, audio_path: str) -> float:
        """获取音频时长（秒）"""
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 
                 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 
                 audio_path],
                capture_output=True,
                text=True
            )
            return float(result.stdout.strip())
        except Exception:
            # 备用方案：估算（中文约 3-4 字/秒）
            return 0
    
    @classmethod
    def list_voices(cls, provider: str = "edge", language: str = "zh") -> list:
        """列出可用声音"""
        if provider == "edge":
            async def get_voices():
                voices = await edge_tts.list_voices()
                return [v for v in voices if v['Locale'].startswith(language)]
            return asyncio.run(get_voices())
        return []


def synthesize_script(script_text: str, output_path: str, 
                      voice: str = "zh-CN-YunxiNeural",
                      rate: str = "+10%") -> str:
    """
    便捷函数：合成脚本语音
    
    Args:
        script_text: 脚本文本
        output_path: 输出路径
        voice: 声音名称
        rate: 语速
    
    Returns:
        输出文件路径
    """
    config = TTSConfig(
        provider="edge",
        voice=voice,
        rate=rate
    )
    engine = TTSEngine(config)
    return engine.synthesize(script_text, output_path)


if __name__ == '__main__':
    # 测试
    test_text = """
    你有没有想过，为什么有些人能够持续成功，而大多数人只是昙花一现？
    
    今天我要和你分享的这本书，来自全球最大对冲基金的创始人。
    他用 40 年的时间，总结出了一套可复制的成功原则。
    """
    
    output = synthesize_script(
        test_text, 
        "output/audio/test.mp3",
        voice="zh-CN-YunxiNeural",
        rate="+15%"
    )
    print(f"音频已生成: {output}")
