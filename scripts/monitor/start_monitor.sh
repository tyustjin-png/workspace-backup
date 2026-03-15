#!/bin/bash
# Meme 币监控系统启动脚本

cd /root/.openclaw/workspace

# 激活虚拟环境并运行
./meme_monitor_env/bin/python meme_monitor_mvp.py
