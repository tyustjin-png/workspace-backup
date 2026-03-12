#!/usr/bin/env python3
"""列出可用的 Gemini 模型"""

import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

print(">>> 可用的 Gemini 模型：\n")

try:
    models = client.models.list()
    for model in models:
        if 'gemini' in model.name.lower() and 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   支持方法: {', '.join(model.supported_generation_methods)}")
            print()
except Exception as e:
    print(f"❌ 错误: {e}")
