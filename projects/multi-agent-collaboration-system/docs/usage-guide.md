# 多 Agent 系统使用指南

## 🎯 快速使用

### 方式 1：直接对话唤起（推荐）

最简单！直接跟紫龙说：

```
用多 agent 系统帮我 <任务描述>
```

**示例**：
```
用多 agent 系统帮我搜索 OpenAI Sora 并改写成推文
```

紫龙会自动执行：
1. SearchAgent - 搜索相关信息
2. RewriteAgent - 改写成推文
3. ReviewAgent - 审核打分

你会收到最终结果和评分。

---

### 方式 2：命令行启动

如果你想先看执行计划：

```bash
cd projects/multi-agent-collaboration-system
./run_task.sh "你的任务描述"
```

或者直接用 Python：

```bash
python3 src/master_agent.py "你的任务描述"
```

这会生成：
- 📄 执行计划（JSON）
- 📝 Worker 提示词
- 💾 任务状态文件

然后你可以：
- 让紫龙执行这个计划
- 自己手动执行
- 或者修改计划后执行

---

## 📋 支持的任务类型（MVP）

当前 3-Agent 流水线适合：

✅ **信息搜索 + 内容创作**
- "搜索 X 并改写成推文"
- "调研 Y 并生成摘要"
- "了解 Z 并写成博客"

✅ **内容审核评估**
- 自动评分（1-10）
- 给出改进建议
- 多维度分析

---

## 🔧 自定义 Worker（进阶）

想要添加新的 Worker 类型？

### 1. 编辑 master_agent.py

找到 `generate_worker_prompt()` 方法，添加新类型：

```python
prompts = {
    "search": "...",
    "rewrite": "...",
    "review": "...",
    "your_new_type": """你是一个 XXX 助手...
输出格式（JSON）:
{
  "status": "success",
  "output": { ... }
}
"""
}
```

### 2. 更新 plan() 方法

在任务规划中添加新步骤：

```python
plan = [
    {"worker_type": "search", ...},
    {"worker_type": "your_new_type", ...},
    {"worker_type": "rewrite", ...},
]
```

### 3. 测试

```bash
python3 src/master_agent.py "测试任务"
```

---

## 📊 查看任务状态

所有任务执行后会保存状态：

```bash
# 查看状态文件
ls -lh states/

# 查看事件日志
cat logs/event_log.jsonl | jq .
```

状态文件包含：
- 任务描述
- 执行状态（idle/planning/executing/done/error）
- 每个步骤的输出
- 时间戳

---

## 🚀 未来扩展（v1.0+）

**即将支持**：
- 并行任务（多个 Agent 同时工作）
- 更多 Worker 类型（coder, tester, analyst）
- 自定义流水线配置
- Web UI 可视化

**想要的功能？** 告诉紫龙！

---

## 💡 提示

**当前限制**：
- MVP 阶段固定 3 步流水线
- 需要手动触发执行（通过对话）
- Python 脚本仅生成计划，不直接执行

**最佳实践**：
- 任务描述清晰具体
- 一次只做一个任务
- 查看执行计划了解流程

---

**最后更新**: 2026-02-08
