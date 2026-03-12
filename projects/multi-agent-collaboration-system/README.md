# 多 Agent 协作系统

构建协作式 AI 代理系统，支持任务分环节处理和多 Agent 协同。

## 📋 项目状态

**当前版本**: v0.1 MVP  
**进度**: 30% (需求分析 + 架构设计完成，代码骨架完成)

## 🎯 MVP 目标

实现 **3 个 Agent 完成简单流水线任务**：

1. **SearchAgent**: 搜索问题答案
2. **RewriteAgent**: 改写成推文
3. **ReviewAgent**: 审核打分

## 🏗️ 架构

```
用户 (Telegram)
    ↓
Master Agent (任务编排)
    ├→ SearchAgent (搜索)
    ├→ RewriteAgent (改写)
    └→ ReviewAgent (审核)
    ↓
状态存储 (JSON)
```

## 📁 目录结构

```
projects/multi-agent-collaboration-system/
├── docs/                        # 文档
│   ├── requirements-analysis.md # 需求分析
│   └── architecture-design.md   # 架构设计
├── src/                         # 源代码
│   ├── master_agent.py          # Master Agent 主逻辑
│   ├── task_state.py            # 状态管理
│   └── utils.py                 # 工具函数
├── states/                      # 任务状态文件
├── logs/                        # 事件日志
├── tests/                       # 测试脚本
│   └── test_pipeline.py
├── tasks/                       # 任务看板
│   ├── backlog.md
│   ├── in-progress.md
│   └── done.md
├── PROJECT.md                   # 项目总览
└── README.md                    # 本文件
```

## 🚀 快速开始

### 1. 测试 Master Agent

```bash
cd projects/multi-agent-collaboration-system
python3 src/master_agent.py "什么是 OpenClaw"
```

这会输出：
- 任务执行计划（JSON）
- Worker 提示词

### 2. 运行测试

```bash
python3 tests/test_pipeline.py
```

### 3. 手动执行流水线（MVP）

由于 MVP 阶段 Python 脚本无法直接调用 OpenClaw 工具，需要在 AI 会话中手动执行：

**步骤 A**: 生成执行计划

```bash
python3 src/master_agent.py "什么是 OpenClaw"
```

**步骤 B**: 在 OpenClaw AI 会话中执行

1. 创建 SearchAgent:
```
请使用 sessions_spawn 创建一个 SearchAgent，任务是搜索 "什么是 OpenClaw"
```

2. 创建 RewriteAgent:
```
使用 sessions_spawn 创建 RewriteAgent，将上一步的结果改写成推文
```

3. 创建 ReviewAgent:
```
使用 sessions_spawn 创建 ReviewAgent，审核推文质量
```

## 📊 技术栈

- **语言**: Python 3
- **Agent 框架**: OpenClaw sessions_spawn/sessions_send
- **状态存储**: JSON 文件
- **通信方式**: OpenClaw 内置通信

## 🎯 里程碑

- [x] 需求分析
- [x] 架构设计
- [x] 代码骨架
- [ ] 端到端测试
- [ ] 完整自动化
- [ ] 文档完善

## 📝 待办事项

1. **自动化执行** (高优先级)
   - 实现自动化编排脚本
   - 集成 OpenClaw API

2. **Worker Agent 优化**
   - 更好的错误处理
   - 超时控制
   - 结果验证

3. **功能扩展** (v1.0)
   - 并行任务支持
   - 更多 Worker 类型
   - Web UI 可视化

## 📖 文档

- [需求分析](docs/requirements-analysis.md) - 详细的需求分析和 MVP 定义
- [架构设计](docs/architecture-design.md) - 系统架构和接口设计

## 🤝 贡献

当前为个人项目，欢迎建议和反馈。

---

**最后更新**: 2026-02-08
