#!/bin/bash
set -e

WORKSPACE="/root/.openclaw/workspace"
OPENCLAW="/root/.openclaw"
BACKUP_DIR="$WORKSPACE/openclaw-backup"

cd "$WORKSPACE"

# 同步 OpenClaw 配置（脱敏）
mkdir -p "$BACKUP_DIR/cron" "$BACKUP_DIR/identity" "$BACKUP_DIR/memory" "$BACKUP_DIR/devices"

# 脱敏 openclaw.json
cat "$OPENCLAW/openclaw.json" | \
  sed 's/"token":\s*"[^"]*"/"token": "***REDACTED***"/g' | \
  sed 's/"apiKey":\s*"[^"]*"/"apiKey": "***REDACTED***"/g' | \
  sed 's/"secret":\s*"[^"]*"/"secret": "***REDACTED***"/g' \
  > "$BACKUP_DIR/openclaw.json"

# 复制其他配置
cp "$OPENCLAW/cron/jobs.json" "$BACKUP_DIR/cron/" 2>/dev/null || true
cp "$OPENCLAW/identity/device.json" "$BACKUP_DIR/identity/" 2>/dev/null || true
cp "$OPENCLAW/memory/main.sqlite" "$BACKUP_DIR/memory/" 2>/dev/null || true
cp "$OPENCLAW/devices/"*.json "$BACKUP_DIR/devices/" 2>/dev/null || true

# Git 提交推送
git add -A
git commit -m "🐉 Daily backup - $(date +%Y-%m-%d)" 2>/dev/null || exit 0
git push origin master

echo "[$(date)] Backup completed" >> /tmp/backup.log
