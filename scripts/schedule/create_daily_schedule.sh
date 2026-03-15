#!/bin/bash
# 每日 07:30 创建当天日程文件

WORKSPACE="/Users/qianzhao/.openclaw/workspace"
DATE=$(date +%Y-%m-%d)
DAY=$(date +%A)
SCHEDULE_FILE="$WORKSPACE/memory/daily-schedule/$DATE.md"

# 如果已经存在则跳过
if [ -f "$SCHEDULE_FILE" ]; then
    echo "✅ 日程文件已存在：$SCHEDULE_FILE"
    exit 0
fi

# 创建日程文件
cat > "$SCHEDULE_FILE" << EOF
# 每日日程 $DATE（$DAY）

## ⛹️ 运动
- [ ] 100仰卧起坐
- [ ] 50俯卧撑
- [ ] 20深蹲
- [ ] 100提臀

## 💰 投资
- [ ] 定投相关
- [ ] 链上数据
- [ ] 美股跟踪

## ✍️ 写作
- [ ] 邮件
- [ ] 公众号
- [ ] 推特

## 🤝 社交/人脉
- [ ] 行业交流
- [ ] 朋友聚会

## 🏠 家庭
- [ ] 罗老师
- [ ] 父母
- [ ] 儿子

---
_创建时间：$(date '+%Y-%m-%d %H:%M')_
EOF

echo "✅ 日程文件已创建：$SCHEDULE_FILE"
