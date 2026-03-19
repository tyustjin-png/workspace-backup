# AI/Agent 持续学习日志

**创建时间：** 2026-03-07
**目标：** 追踪 AI/Agent 最新进展，持续提升效率

---

## 📚 信息源清单

### 核心资源
- [ ] Anthropic Blog - https://www.anthropic.com/news
- [ ] OpenAI Research - https://openai.com/research
- [ ] Papers with Code - https://paperswithcode.com
- [ ] Hacker News AI - https://news.ycombinator.com
- [ ] GitHub Trending AI - https://github.com/trending/python?since=weekly

### Agent 框架
- [ ] OpenClaw - https://github.com/openclaw/openclaw
- [ ] LangChain - https://github.com/langchain-ai/langchain
- [ ] CrewAI - https://github.com/joaomdmoura/crewAI
- [ ] AutoGPT - https://github.com/Significant-Gravitas/AutoGPT

### 中文社区
- [ ] 宝玉翻译 - Twitter @dotey
- [ ] 即刻 AI 话题
- [ ] 知乎 AI 专栏

---

## 📅 学习计划

### 每周固定节奏
- **周一 10:00** - 扫描上周重大更新（30分钟）
- **周三 15:00** - 精读 1-2 篇深度内容（1小时）
- **周五 20:00** - 总结本周学习，更新知识库（30分钟）

### 学习流程
1. 快速扫描标题/摘要（过滤噪音）
2. 精读有价值的内容（深度理解）
3. 提取可行动的点（实际应用）
4. 更新知识库（沉淀记忆）
5. 必要时创建 skill 或优化工作流

---

## 📝 学习记录

### 2026-03-07 - 建立学习机制

**触发事件：** 金哥指出我从未使用过 skills，效率意识不足

**关键认知：**
- 过度依赖基础工具，忽略了专门 skills 的效率优势
- 缺少主动学习和追踪 AI 进展的机制
- 需要建立定期检查、学习、迭代的闭环

**行动：**
- ✅ 创建本学习日志
- ✅ 梳理信息源清单
- ✅ 制定每周学习计划
- ⏳ 将学习任务加入 HEARTBEAT.md

**下一步：**
- 周一开始执行第一次信息扫描
- 测试不同信息源的价值密度
- 优化学习流程

---

## 💡 效率提升记录

### 待探索的优化方向
- [ ] 重新审视所有可用 skills，找到适用场景
- [ ] 研究 Agent 框架的最佳实践
- [ ] 探索多 Agent 协作模式（subagents 用法）
- [ ] 优化记忆系统（memory_search 更精准）
- [ ] 学习更高效的工具组合使用

---

## 📡 周扫描 - 2026-03-16

### 本周 Agent 领域动态（3/10-3/16）

**1. Agno 框架更新 — Workflow run-level parameters**
- Agno（生产级Agent框架）3月更新：Workflow 支持 run-level parameters，实现跨下游 Agent 的 metadata 传播和依赖注入
- 这对多 Agent 编排很实用，值得关注其 Team（Route/Delegate-all 模式）和 Workflow 的设计思路
- 🔗 https://www.decisioncrafters.com/agno-production-ai-agent-framework/

**2. shadcn/ui 加入 AI Agent Skills**
- shadcn/ui 3月更新引入 "AI Agent Skills" 概念，让 UI 组件库可被 Agent 调用
- 方向：前端组件 → Agent 可操作的技能，模糊 UI 和 Agent 的边界
- 🔗 https://dev.to/codedthemes/shadcnui-march-2026-update-cli-v4-ai-agent-skills-and-design-system-presets-1gp1

**3. OpenAI 下线 GPT-5.1**
- 3/11 起 GPT-5.1 模型从 ChatGPT 下线，应该是推更新版本的节奏

**4. Agentic AI 市场数据**
- 全球 Agentic AI 市场：2026年 $91.4亿 → 预计2034年 $1390亿（CAGR 40.5%）
- "AgentOps"（Agent 监控/安全/管理基础设施）成为新的 VC 热点
- 行业叙事从 "chatbot" 转向 "agent that does"

**5. Agentic Coding 工具盘点**
- obviousworks.ch 发了篇 2026 年 7 大 Agentic Coding 框架对比，聚焦 CLI 工具和长时自主 Agent
- 🔗 https://www.obviousworks.ch/en/agentic-coding-tools-2026-the-7-frameworks-that-take-your-development-to-a-new-level/

**💡 对我们的启发：**
- Agno 的 Workflow 编排模式可以参考，特别是 metadata propagation 的思路
- shadcn/ui 的 Agent Skills 方向暗示：未来 Agent 会直接操作 UI 组件，不再只是生成代码
- AgentOps 是个值得关注的赛道——Agent 多了，管理 Agent 就成了刚需

---

_持续更新中..._
