"""
书籍内容提取模块
支持 PDF、TXT、豆瓣 API
"""
import os
import re
import json
from pathlib import Path

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class BookExtractor:
    """书籍内容提取器"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.md']
    
    def extract_from_file(self, file_path: str, max_chars: int = 50000) -> dict:
        """
        从文件提取书籍内容
        
        Args:
            file_path: 文件路径
            max_chars: 最大字符数（避免 token 超限）
        
        Returns:
            {
                'title': '书名',
                'author': '作者',
                'content': '内容',
                'source': 'file'
            }
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return self._extract_pdf(path, max_chars)
        elif suffix in ['.txt', '.md']:
            return self._extract_text(path, max_chars)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")
    
    def _extract_pdf(self, path: Path, max_chars: int) -> dict:
        """提取 PDF 内容"""
        if not HAS_PYMUPDF:
            raise ImportError("需要安装 PyMuPDF: pip install pymupdf")
        
        doc = fitz.open(path)
        
        # 尝试从元数据获取标题和作者
        metadata = doc.metadata
        title = metadata.get('title') or path.stem
        author = metadata.get('author') or '未知'
        
        # 提取文本
        text_parts = []
        total_chars = 0
        
        for page in doc:
            page_text = page.get_text()
            if total_chars + len(page_text) > max_chars:
                # 截断
                remaining = max_chars - total_chars
                text_parts.append(page_text[:remaining])
                break
            text_parts.append(page_text)
            total_chars += len(page_text)
        
        doc.close()
        
        content = '\n'.join(text_parts)
        content = self._clean_text(content)
        
        return {
            'title': title,
            'author': author,
            'content': content,
            'source': 'pdf'
        }
    
    def _extract_text(self, path: Path, max_chars: int) -> dict:
        """提取 TXT/MD 内容"""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(max_chars)
        
        content = self._clean_text(content)
        
        return {
            'title': path.stem,
            'author': '未知',
            'content': content,
            'source': 'text'
        }
    
    def fetch_from_douban(self, isbn_or_title: str) -> dict:
        """
        从豆瓣获取书籍信息
        
        Args:
            isbn_or_title: ISBN 或书名
        
        Returns:
            书籍信息字典
        """
        if not HAS_REQUESTS:
            raise ImportError("需要安装 requests: pip install requests")
        
        # 豆瓣 API 已不可用，使用网页爬取或第三方服务
        # 这里返回一个示例结构，实际需要对接可用的 API
        
        # 尝试用豆瓣搜索页面
        search_url = f"https://search.douban.com/book/subject_search?search_text={isbn_or_title}"
        
        # 实际实现需要解析网页或使用第三方 API
        # 这里返回占位数据
        return {
            'title': isbn_or_title,
            'author': '待手动填写',
            'content': '请提供书籍内容或简介',
            'source': 'douban_placeholder'
        }
    
    def from_manual_input(self, title: str, author: str, content: str) -> dict:
        """手动输入书籍信息"""
        return {
            'title': title,
            'author': author,
            'content': self._clean_text(content),
            'source': 'manual'
        }
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余空白
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        # 移除页码等干扰信息
        text = re.sub(r'\n\d+\n', '\n', text)
        return text.strip()


# 便捷函数
def extract_book(source: str, **kwargs) -> dict:
    """
    提取书籍内容的便捷函数
    
    Args:
        source: 文件路径、ISBN、或 'manual'
        **kwargs: 额外参数（如 title, author, content）
    """
    extractor = BookExtractor()
    
    if source == 'manual':
        return extractor.from_manual_input(
            kwargs.get('title', ''),
            kwargs.get('author', ''),
            kwargs.get('content', '')
        )
    elif source.startswith('isbn:') or source.startswith('douban:'):
        query = source.split(':', 1)[1]
        return extractor.fetch_from_douban(query)
    elif os.path.exists(source):
        return extractor.extract_from_file(source)
    else:
        raise ValueError(f"无法识别的来源: {source}")


if __name__ == '__main__':
    # 测试
    book = extract_book(
        'manual',
        title='原则',
        author='瑞·达利欧',
        content='生活和工作原则...'
    )
    print(json.dumps(book, ensure_ascii=False, indent=2))
