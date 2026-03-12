#!/usr/bin/env python3
"""将最近的邮件标记为未读，用于测试"""

import os
import imaplib
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

def mark_recent_as_unread(count=10):
    """将最近的 count 封邮件标记为未读"""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        mail.select("inbox")
        
        # 获取所有邮件ID
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        
        # 取最近的 count 封
        recent_ids = email_ids[-count:]
        
        print(f">>> 准备标记 {len(recent_ids)} 封邮件为未读...")
        
        for e_id in recent_ids:
            mail.store(e_id, '-FLAGS', '\\Seen')
        
        print(f">>> ✅ 已标记 {len(recent_ids)} 封邮件为未读")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f">>> ❌ 操作失败: {e}")

if __name__ == "__main__":
    mark_recent_as_unread(10)
