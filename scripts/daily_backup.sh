#!/bin/bash
set -e
cd /root/.openclaw/workspace
git add -A
git commit -m "🐉 Daily backup - $(date +%Y-%m-%d)" 2>/dev/null || exit 0
git push origin master
echo "[$(date)] Backup completed" >> /tmp/backup.log
