"""
AI 脚本生成模块
使用 Claude API 生成视频脚本
"""
import os
import re
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


@dataclass
class VideoScript:
    """视频脚本数据结构"""
    book_title: str
    author: str
    titles: list[str]  # 3个备选标题
    hook: str  # 开场钩子
    content: str  # 核心内容（完整口播稿）
    cta: str  # 行动号召
    highlights: list[str]  # 字幕金句
    tags: list[str]  # 推荐标签
    full_script: str  # 完整脚本文本
    word_count: int  # 字数
    estimated_duration: float  # 预估时长（分钟）


class ScriptGenerator:
    """脚本生成器"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        if not HAS_ANTHROPIC:
            raise ImportError("需要安装 anthropic: pip install anthropic")
        
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("需要设置 ANTHROPIC_API_KEY 环境变量")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
        
        # 加载 prompt 模板
        template_path = Path(__file__).parent.parent / 'templates' / 'script_prompt.md'
        if template_path.exists():
            self.prompt_template = template_path.read_text(encoding='utf-8')
        else:
            self.prompt_template = self._default_prompt()
    
    def generate(self, book_info: dict) -> VideoScript:
        """
        生成视频脚本
        
        Args:
            book_info: {
                'title': '书名',
                'author': '作者',
                'content': '书籍内容/简介'
            }
        
        Returns:
            VideoScript 对象
        """
        # 构建 prompt
        prompt = self.prompt_template.format(
            book_title=book_info.get('title', ''),
            author=book_info.get('author', ''),
            book_content=book_info.get('content', '')[:30000]  # 限制长度
        )
        
        # 调用 Claude API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # 解析响应
        return self._parse_response(response_text, book_info)
    
    def _parse_response(self, response: str, book_info: dict) -> VideoScript:
        """解析 Claude 响应"""
        
        # 提取各部分
        titles = self._extract_section(response, r'【标题建议】(.*?)【开场钩子】', as_list=True)
        hook = self._extract_section(response, r'【开场钩子】(.*?)【核心内容】')
        content = self._extract_section(response, r'【核心内容】(.*?)【行动号召】')
        cta = self._extract_section(response, r'【行动号召】(.*?)【字幕金句】')
        highlights = self._extract_section(response, r'【字幕金句】(.*?)【推荐标签】', as_list=True)
        tags_text = self._extract_section(response, r'【推荐标签】(.*?)(?:$|```)')
        
        # 解析标签
        tags = re.findall(r'#(\S+)', tags_text)
        
        # 组合完整口播稿
        full_script = f"{hook}\n\n{content}\n\n{cta}"
        
        # 计算字数和时长
        word_count = len(re.sub(r'\s', '', full_script))
        estimated_duration = word_count / 200  # 约 200字/分钟
        
        return VideoScript(
            book_title=book_info.get('title', ''),
            author=book_info.get('author', ''),
            titles=titles[:3] if titles else ['待定标题'],
            hook=hook.strip(),
            content=content.strip(),
            cta=cta.strip(),
            highlights=highlights[:5] if highlights else [],
            tags=tags[:5] if tags else [],
            full_script=full_script.strip(),
            word_count=word_count,
            estimated_duration=round(estimated_duration, 1)
        )
    
    def _extract_section(self, text: str, pattern: str, as_list: bool = False) -> str | list:
        """提取文本段落"""
        match = re.search(pattern, text, re.DOTALL)
        if not match:
            return [] if as_list else ''
        
        content = match.group(1).strip()
        
        if as_list:
            # 按行或数字分割
            lines = re.split(r'\n\d+[\.\、]|\n-\s*', content)
            return [line.strip() for line in lines if line.strip()]
        
        return content
    
    def _default_prompt(self) -> str:
        """默认 prompt 模板"""
        return """
你是一位资深的读书博主，擅长将书籍内容提炼成引人入胜的短视频脚本。

书名：{book_title}
作者：{author}
内容：
{book_content}

请生成一个 2-3 分钟的口播脚本，包含：
1. 开场钩子（反常识/痛点/悬念）
2. 3个核心观点（每个配案例）
3. 行动号召（引导关注+橱窗）

输出格式：
【标题建议】
【开场钩子】
【核心内容】
【行动号召】
【字幕金句】
【推荐标签】
"""
    
    def save_script(self, script: VideoScript, output_path: str):
        """保存脚本到文件"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            'book_title': script.book_title,
            'author': script.author,
            'titles': script.titles,
            'hook': script.hook,
            'content': script.content,
            'cta': script.cta,
            'highlights': script.highlights,
            'tags': script.tags,
            'full_script': script.full_script,
            'word_count': script.word_count,
            'estimated_duration': script.estimated_duration
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # 同时保存纯文本版本
        txt_path = path.with_suffix('.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"# {script.book_title}\n")
            f.write(f"作者：{script.author}\n")
            f.write(f"时长：约 {script.estimated_duration} 分钟 ({script.word_count} 字)\n\n")
            f.write("---\n\n")
            f.write(script.full_script)
            f.write("\n\n---\n\n")
            f.write("【标题建议】\n")
            for i, title in enumerate(script.titles, 1):
                f.write(f"{i}. {title}\n")
            f.write("\n【字幕金句】\n")
            for highlight in script.highlights:
                f.write(f"• {highlight}\n")
            f.write(f"\n【标签】 {' '.join(['#' + t for t in script.tags])}\n")
        
        return str(path), str(txt_path)


if __name__ == '__main__':
    # 测试
    generator = ScriptGenerator()
    
    book = {
        'title': '原则',
        'author': '瑞·达利欧',
        'content': '''
        《原则》是桥水基金创始人瑞·达利欧的人生和工作原则总结。
        核心观点：
        1. 拥抱现实并面对现实
        2. 用系统化的方法做决策
        3. 极度透明和极度开放
        4. 痛苦+反思=进步
        5. 相信有意义的工作和有意义的人际关系
        '''
    }
    
    script = generator.generate(book)
    print(f"生成脚本: {script.word_count} 字, 约 {script.estimated_duration} 分钟")
    print(f"标题: {script.titles[0]}")
