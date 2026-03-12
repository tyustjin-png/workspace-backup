# 多 Agent 协作系统 - 架构设计

**版本**: v0.1  
**日期**: 2026-02-08  
**状态**: 草稿

---

## 1. 架构概览

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    用户 (金哥)                          │
│                 通过 Telegram 交互                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Master Agent (orchestrator)               │
│  - 任务分解和调度                                        │
│  - Worker 生命周期管理                                   │
│  - 结果聚合和汇报                                        │
│  - 状态管理和持久化                                      │
└─────────┬───────────────┬───────────────┬───────────────┘
          │               │               │
          ▼               ▼               ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ Worker A │    │ Worker B │    │ Worker C │
   │ (search) │    │ (rewrite)│    │ (review) │
   └──────────┘    └──────────┘    └──────────┘
          │               │               │
          └───────────────┴───────────────┘
                     │
                     ▼
           ┌──────────────────┐
           │  状态存储 (JSON)  │
           │  - task_state.json│
           │  - event_log.json │
           └──────────────────┘
```

### 1.2 核心组件

| 组件 | 职责 | 实现方式 |
|------|------|----------|
| **Master Agent** | 任务编排、调度、汇报 | Python 脚本 + OpenClaw sessions |
| **Worker Agent** | 执行具体任务 | OpenClaw `sessions_spawn` |
| **状态存储** | 任务状态、事件日志 | JSON 文件 |
| **通信层** | Agent 间消息传递 | OpenClaw `sessions_send` |

---

## 2. Master Agent 设计

### 2.1 核心职责

1. **任务分解**: 将用户请求拆分成子任务
2. **Worker 管理**: 创建、监控、销毁 Worker Agent
3. **调度控制**: 决定任务执行顺序（顺序/并行）
4. **结果聚合**: 收集 Worker 输出，生成最终报告
5. **用户交互**: 向金哥汇报进度和结果

### 2.2 接口定义

```python
class MasterAgent:
    """
    Master Agent 负责任务编排和调度
    """
    
    def __init__(self, task_description: str):
        """初始化 Master Agent
        
        Args:
            task_description: 用户输入的任务描述
        """
        self.task_id = generate_task_id()
        self.task_description = task_description
        self.workers = []
        self.state = TaskState()
        
    def plan(self) -> List[SubTask]:
        """任务规划：分解成子任务
        
        Returns:
            子任务列表 [SubTask(agent_type, input_data), ...]
        """
        pass
        
    def execute(self, plan: List[SubTask]) -> TaskResult:
        """执行任务计划
        
        Args:
            plan: 子任务列表
            
        Returns:
            任务执行结果
        """
        pass
        
    def spawn_worker(self, agent_type: str, task: str) -> str:
        """创建 Worker Agent
        
        Args:
            agent_type: Worker 类型 (search/rewrite/review)
            task: 任务描述
            
        Returns:
            session_key: Worker 的 session 标识
        """
        pass
        
    def send_to_worker(self, session_key: str, message: str) -> str:
        """向 Worker 发送消息
        
        Args:
            session_key: Worker session
            message: 消息内容
            
        Returns:
            Worker 的响应
        """
        pass
        
    def aggregate_results(self, results: List[Any]) -> str:
        """聚合 Worker 结果
        
        Args:
            results: 各 Worker 的输出
            
        Returns:
            最终报告文本
        """
        pass
        
    def report_to_user(self, message: str):
        """向用户汇报
        
        Args:
            message: 汇报内容
        """
        pass
```

### 2.3 状态机

Master Agent 的任务执行状态：

```
IDLE → PLANNING → EXECUTING → AGGREGATING → DONE
         ↓            ↓            ↓
       ERROR      ERROR        ERROR
```

状态转换逻辑：
- `IDLE`: 初始状态，等待任务
- `PLANNING`: 分解任务为子任务
- `EXECUTING`: 调度 Worker 执行
- `AGGREGATING`: 收集并整合结果
- `DONE`: 任务完成
- `ERROR`: 任何阶段出错

---

## 3. Worker Agent 设计

### 3.1 Worker 类型

MVP 阶段支持 3 种 Worker：

| Worker 类型 | 职责 | 技能要求 |
|------------|------|----------|
| **SearchAgent** | 搜索问题答案 | web_search, web_fetch |
| **RewriteAgent** | 改写成推文 | 文案能力 |
| **ReviewAgent** | 审核打分 | 评审能力 |

### 3.2 Worker 接口

每个 Worker 通过 `sessions_spawn` 创建，接收标准化输入：

```json
{
  "task_type": "search",
  "input": {
    "query": "什么是 OpenClaw?"
  },
  "context": {
    "task_id": "task-12345",
    "step": 1,
    "total_steps": 3
  }
}
```

Worker 输出标准格式：

```json
{
  "status": "success",
  "output": {
    "answer": "OpenClaw 是一个 AI 助手框架..."
  },
  "metadata": {
    "execution_time": 3.5,
    "tokens_used": 1200
  }
}
```

### 3.3 Worker Agent 模板

```python
# worker_template.py
import sys
import json

def main():
    # 读取输入（从 Master 通过 sessions_send 传入）
    task_input = sys.stdin.read()
    data = json.loads(task_input)
    
    task_type = data["task_type"]
    input_data = data["input"]
    
    # 执行具体任务
    if task_type == "search":
        result = perform_search(input_data["query"])
    elif task_type == "rewrite":
        result = perform_rewrite(input_data["content"])
    elif task_type == "review":
        result = perform_review(input_data["content"])
    else:
        raise ValueError(f"Unknown task type: {task_type}")
    
    # 输出结果
    output = {
        "status": "success",
        "output": result,
        "metadata": {"execution_time": 0}
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
```

---

## 4. 通信协议

### 4.1 Master → Worker

Master 通过 `sessions_send` 向 Worker 发送任务：

```python
# Master 端
session_key = spawn_worker("search", "搜索 OpenClaw")
response = sessions_send(
    session_key=session_key,
    message=json.dumps({
        "task_type": "search",
        "input": {"query": "什么是 OpenClaw?"}
    })
)
```

### 4.2 Worker → Master

Worker 完成任务后，返回结果：

```python
# Worker 端（实际由 OpenClaw 处理）
# Worker 的最后一条消息会被 Master 的 sessions_send 捕获
print(json.dumps({
    "status": "success",
    "output": {"answer": "..."}
}))
```

### 4.3 消息格式约定

**任务消息** (Master → Worker):
```json
{
  "task_type": "search|rewrite|review",
  "input": { /* 任务特定参数 */ },
  "context": {
    "task_id": "唯一任务 ID",
    "step": "当前步骤",
    "total_steps": "总步骤数"
  }
}
```

**结果消息** (Worker → Master):
```json
{
  "status": "success|error",
  "output": { /* 结果数据 */ },
  "error": "错误信息（仅 status=error 时）",
  "metadata": {
    "execution_time": 3.5,
    "tokens_used": 1200
  }
}
```

---

## 5. 状态管理

### 5.1 状态存储格式

**task_state.json** - 任务执行状态：

```json
{
  "task_id": "task-20260208-001",
  "description": "搜索并改写成推文",
  "status": "executing",
  "created_at": 1707393600,
  "updated_at": 1707393650,
  "steps": [
    {
      "step": 1,
      "worker_type": "search",
      "session_key": "isolated-abc123",
      "status": "done",
      "output": {"answer": "..."}
    },
    {
      "step": 2,
      "worker_type": "rewrite",
      "session_key": "isolated-def456",
      "status": "running",
      "output": null
    }
  ]
}
```

**event_log.json** - 事件日志（用于调试和回放）：

```json
[
  {
    "timestamp": 1707393600,
    "event": "task_created",
    "data": {"task_id": "task-001", "description": "..."}
  },
  {
    "timestamp": 1707393605,
    "event": "worker_spawned",
    "data": {"worker_type": "search", "session_key": "..."}
  },
  {
    "timestamp": 1707393610,
    "event": "worker_completed",
    "data": {"session_key": "...", "output": {...}}
  }
]
```

### 5.2 状态持久化

```python
class TaskState:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.file_path = f"states/{task_id}.json"
        
    def save(self):
        """保存状态到文件"""
        with open(self.file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
            
    def load(self):
        """从文件加载状态"""
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            self.from_dict(data)
            
    def log_event(self, event: str, data: dict):
        """记录事件到日志"""
        event_log.append({
            "timestamp": time.time(),
            "event": event,
            "data": data
        })
```

---

## 6. MVP 实现流程

### 6.1 执行流程图

```
用户: "搜索 OpenClaw 并改写成推文"
  │
  ▼
Master: 分析任务 → 规划 3 个步骤
  │
  ├─→ Step 1: Spawn SearchAgent
  │      └─→ sessions_spawn(task="搜索 OpenClaw")
  │      └─→ sessions_send(message='{"task_type":"search", "input":{"query":"OpenClaw"}}')
  │      └─→ 等待结果: {"output": {"answer": "OpenClaw是..."}}
  │
  ├─→ Step 2: Spawn RewriteAgent
  │      └─→ sessions_spawn(task="改写成推文")
  │      └─→ sessions_send(message='{"task_type":"rewrite", "input":{"content":"OpenClaw是..."}}')
  │      └─→ 等待结果: {"output": {"tweet": "🚀 OpenClaw..."}}
  │
  ├─→ Step 3: Spawn ReviewAgent
  │      └─→ sessions_spawn(task="审核推文")
  │      └─→ sessions_send(message='{"task_type":"review", "input":{"content":"🚀 OpenClaw..."}}')
  │      └─→ 等待结果: {"output": {"score": 8, "feedback": "..."}}
  │
  ▼
Master: 聚合结果 → 生成报告
  │
  ▼
向金哥汇报:
  ✅ 任务完成
  📝 最终推文: "🚀 OpenClaw..."
  ⭐ 审核评分: 8/10
  💡 改进建议: "..."
```

### 6.2 核心代码结构

```
projects/multi-agent-collaboration-system/
├── src/
│   ├── master_agent.py          # Master Agent 主逻辑
│   ├── worker_search.py         # SearchAgent 实现
│   ├── worker_rewrite.py        # RewriteAgent 实现
│   ├── worker_review.py         # ReviewAgent 实现
│   ├── task_state.py            # 状态管理
│   └── utils.py                 # 工具函数
├── states/                      # 状态文件存储
│   └── task-*.json
├── logs/                        # 事件日志
│   └── event_log.json
└── tests/                       # 测试脚本
    └── test_pipeline.py
```

---

## 7. 技术细节

### 7.1 OpenClaw API 调用示例

```python
import subprocess
import json

def spawn_worker(agent_type: str, task: str) -> str:
    """创建 Worker Agent"""
    cmd = [
        "sessions_spawn",
        "--task", task,
        "--label", f"worker-{agent_type}",
        "--cleanup", "delete"  # 完成后自动删除
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # 解析输出获取 session_key
    return parse_session_key(result.stdout)

def send_to_worker(session_key: str, message: str) -> str:
    """向 Worker 发送消息并等待响应"""
    cmd = [
        "sessions_send",
        "--sessionKey", session_key,
        "--message", message
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout
```

### 7.2 错误处理策略

| 错误类型 | 处理策略 |
|---------|---------|
| Worker 创建失败 | 重试 3 次，失败后中止任务 |
| Worker 执行超时 | 30 秒超时，记录错误，跳过该步骤 |
| Worker 返回错误 | 记录日志，尝试降级方案或中止 |
| 通信失败 | 重试 2 次，失败后标记 Worker 为失效 |

### 7.3 性能优化

1. **并行执行（v1.0）**: 独立任务可并发
2. **结果缓存**: 相同输入复用结果
3. **超时控制**: 防止单个 Worker 卡住整个流程
4. **资源清理**: Worker 完成后自动销毁（`--cleanup delete`）

---

## 8. 测试计划

### 8.1 单元测试

- [ ] Master Agent 任务分解逻辑
- [ ] Worker Agent 各类型功能
- [ ] 状态管理的保存/加载
- [ ] 通信层消息序列化/反序列化

### 8.2 集成测试

- [ ] 完整 3-Agent 流水线
- [ ] 错误处理和重试机制
- [ ] 超时和资源清理
- [ ] 并发场景（v1.0）

### 8.3 端到端测试

**测试用例 1: 正常流程**
```
输入: "搜索 Claude 4.5 并改写成推文"
预期: 
  - SearchAgent 返回搜索结果
  - RewriteAgent 生成推文
  - ReviewAgent 评分 > 6
  - 总耗时 < 2 分钟
```

**测试用例 2: Worker 失败**
```
输入: "搜索不存在的内容"
预期:
  - SearchAgent 返回空结果或错误
  - Master 记录错误日志
  - 向用户汇报失败原因
```

---

## 9. 后续扩展方向

### 9.1 v1.0 功能

- ✅ 并行任务支持（DAG 调度）
- ✅ 更多 Worker 类型（coder, tester, analyst）
- ✅ Web UI 可视化进度
- ✅ 失败重试和降级策略

### 9.2 v2.0 功能

- ✅ 游戏场景（狼人杀）
- ✅ 多轮对话管理
- ✅ Agent 间自主协商
- ✅ 分布式部署

---

## 10. 总结

**核心设计原则**:
1. **简单优先**: MVP 用最简单的方案（顺序执行、JSON 存储）
2. **可扩展**: 架构支持后续增加并行、游戏等功能
3. **可观测**: 完整的状态持久化和事件日志
4. **容错性**: 清晰的错误处理和重试机制

**下一步**: 开始编码实现（master_agent.py + 3 个 Worker）

---

**文档结束**
