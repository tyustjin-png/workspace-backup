# Slide Deck Outline

**Topic**: OpenClaw 使用技巧：搭建个人AI助手系统的实战经验
**Style**: editorial-infographic
**Dimensions**: clean + cool + editorial + dense
**Audience**: general
**Language**: zh
**Slide Count**: 14 slides
**Generated**: 2026-03-18 16:20

---

<STYLE_INSTRUCTIONS>
Design Aesthetic: High-quality magazine explainer aesthetic with clean visual storytelling. Transforms complex AI system architecture information into digestible, professional narratives. Think Wired or The Verge — bold typography, structured layouts, and purposeful illustrations. Clean flat design with cool analytical palette.

Background:
  Texture: None — clean solid backgrounds
  Base Color: Pure White (#FFFFFF) or Light Gray (#F8F9FA) for section dividers

Typography:
  Headlines: Bold display sans-serif with strong visual presence and editorial sophistication. Large scale for immediate impact. Clean geometric letterforms.
  Body: Humanist sans-serif optimized for reading. Clear, professional, accessible with comfortable line spacing.

Color Palette:
  Primary Text: Near Black (#1A1A1A) — Headlines, body copy
  Background: Pure White (#FFFFFF) — Primary background
  Alt Background: Light Gray (#F8F9FA) — Section backgrounds, card fills
  Secondary Text: Dark Gray (#4A5568) — Captions, metadata
  Accent 1: Editorial Blue (#2563EB) — Primary accent, icons, highlights
  Accent 2: Coral (#F97316) — Secondary accent, warnings, attention
  Accent 3: Emerald (#10B981) — Positive elements, savings, success
  Accent 4: Amber (#F59E0B) — Warnings, attention elements
  Dividers: Medium Gray (#D1D5DB) — Section dividers, borders

Visual Elements:
  - Clean flat illustrations (absolutely no photos or realistic imagery)
  - Structured multi-section card layouts
  - Callout boxes with bold accent color borders for key insights
  - Icon-based data visualization and comparison tables
  - Flow diagrams with clear directional arrows
  - Pull quotes with large quotation marks in accent color
  - Tier/pyramid diagrams for hierarchical concepts

Density Guidelines:
  - Content per slide: 2-4 key points maximum
  - Whitespace: Generous margins, minimum 60px padding
  - Element count: 3-5 visual elements per slide

Style Rules:
  Do: Create clear visual narrative flow; use structured multi-section card layouts; highlight key stats in large bold callout boxes; design visual metaphors for complex ideas; maintain magazine-quality polish throughout.
  Don't: Use photographic imagery; create cluttered dense layouts; mix too many visual styles; add decorative elements without purpose; add slide numbers, footers, or logos.
</STYLE_INSTRUCTIONS>

---

## Slide 1 of 14

**Type**: Cover
**Filename**: 01-slide-cover.png

// NARRATIVE GOAL
引起兴趣，建立分享的专业感与实战感——这不是理论课，是真实踩坑后的干货总结。

// KEY CONTENT
Headline: 打造个人AI助手系统
Sub-headline: 5个关键决策，让效率翻倍、成本减半
Author: 金哥 · 2026-03-18

// VISUAL
Magazine-style editorial cover. Large bold Chinese headline dominates upper two-thirds. A sleek stylized illustration of interconnected nodes/gears representing an AI system flows in the right half — flat vector style in Editorial Blue and Coral. Small structured grid of 5 numbered icons at bottom representing the 5 tips. White background with a bold left editorial stripe in #2563EB.

// LAYOUT
Layout: title-hero
Full-bleed left accent stripe. Title left-aligned. Illustration right side. Clean, confident, authoritative.

---

## Slide 2 of 14

**Type**: Content
**Filename**: 02-slide-overview.png

// NARRATIVE GOAL
快速预览5个核心主题，建立整体框架，让读者知道接下来会学到什么。

// KEY CONTENT
Headline: 5个实战经验，从踩坑到优化
Body:
- ① 模型按任务分级，省钱又提效
- ② 能用脚本就别用Agent
- ③ 并行任务分发是最大效率杠杆
- ④ 记忆系统三层架构
- ⑤ 公众号文章直接API抓取

// VISUAL
Clean numbered list layout with 5 horizontal cards stacked vertically. Each card has a bold number in Editorial Blue circle, short title in Near Black, and a tiny icon on the right. Light Gray card backgrounds. Subtle connecting arrow or timeline line down the left edge.

// LAYOUT
Layout: vertical-list
Five equal-height cards, full width, with consistent left-right padding.

---

## Slide 3 of 14

**Type**: Content
**Filename**: 03-slide-model-tiers.png

// NARRATIVE GOAL
介绍模型分级理念——把AI模型当员工分级，确定性任务不用顶配。

// KEY CONTENT
Headline: 不是所有任务都需要最强模型
Sub-headline: 把模型当员工分级——能让实习生干的活，别请总监

// VISUAL
Bold pull quote card. Large quotation mark in Editorial Blue. Quote text in large Near Black bold. Below: a three-tier horizontal bar showing Haiku / Sonnet / Opus with cost labels ($0.25/M → $3/M → $15/M). Bars in gradient from light green to Editorial Blue to Coral. Clean white background.

// LAYOUT
Layout: quote-callout
Upper half: pull quote. Lower half: tier comparison bar chart.

---

## Slide 4 of 14

**Type**: Content
**Filename**: 04-slide-model-tier-table.png

// NARRATIVE GOAL
具体展示三层模型分配表，让读者立刻知道如何实际操作。

// KEY CONTENT
Headline: 三层模型分配：正确的任务配正确的模型
Body:
- 执行层 | Haiku | $0.25/M | 固定逻辑、脚本、格式化输出
- 处理层 | Sonnet | $3/M | 信息处理、日报生成、搜索总结
- 思考层 | Opus | $15/M | 深度分析、策略制定、创作任务

// VISUAL
Three-row structured table with icons. Left column: role label (执行层/处理层/思考层) in bold with icon (gear/document/brain). Middle: model name in large Editorial Blue. Price in Emerald. Right: usage scenarios in Dark Gray. Alternating row backgrounds (white / light gray). Strong left border accent in matching tier color.

// LAYOUT
Layout: data-table
Three rows, four columns. Clean header row with Divider Gray.

---

## Slide 5 of 14

**Type**: Content
**Filename**: 05-slide-model-result.png

// NARRATIVE GOAL
用真实数字说话：切换模型后成本降60%，效果零差异。这是最有说服力的证据。

// KEY CONTENT
Headline: 18个定时任务，6个切Haiku后：成本降60%
Sub-headline: 效果零差异——这笔账值得算清楚

// VISUAL
Bold stat callout: giant "60%" in Emerald color dominating center-left, with label "成本降低" below in Dark Gray. Right side: simple before/after comparison — two stacked pill bars. "之前：全用Sonnet" in plain bar; "之后：6个切Haiku" in split bar (partial light green + partial blue). White background, generous whitespace.

// LAYOUT
Layout: stat-hero
Left: large stat number. Right: before/after comparison.

---

## Slide 6 of 14

**Type**: Content
**Filename**: 06-slide-script-vs-agent.png

// NARRATIVE GOAL
引入第二个核心观点：Agent不是银弹，能用脚本搞定的别套Agent壳子。

// KEY CONTENT
Headline: Agent不是银弹
Sub-headline: 能用脚本解决的问题，套Agent壳子只会更慢、更贵、更不可控

// VISUAL
Editorial bold statement slide. Large headline in Near Black spanning 60% of width. Below: a stylized badge/icon — a shield with a broken "A" (Agent) overlaid with a "×", in Coral. To the right: three short negative labels in Coral cards: "更慢" / "更贵" / "更不可控". Clean white, high contrast.

// LAYOUT
Layout: statement-visual
Headline left dominant. Visual metaphor right side.

---

## Slide 7 of 14

**Type**: Content
**Filename**: 07-slide-pyramid.png

// NARRATIVE GOAL
用三层金字塔直观展示脚本→Skill→Agent的选择框架。

// KEY CONTENT
Headline: 三层金字塔：按需选工具
Body:
- Agent（顶层）：多步推理、动态策略
- Skill（中层）：LLM单步处理
- 脚本（底层）：确定逻辑、固定流程

// VISUAL
Clean flat pyramid diagram, wide at base. Bottom tier: large base labeled "脚本" in Near Black with light Emerald fill. Middle tier: "Skill" in lighter Editorial Blue. Top tier: narrow "Agent" in Coral. Each tier has a brief description label to the right. Pyramid centered on white background.

// LAYOUT
Layout: diagram-center
Pyramid centered. Labels right-aligned alongside each tier.

---

## Slide 8 of 14

**Type**: Content
**Filename**: 08-slide-decision-tree.png

// NARRATIVE GOAL
提供三个判断问题的决策树，让读者立刻能应用到自己的场景。

// KEY CONTENT
Headline: 3个问题，决定用什么工具
Body:
- 输入输出确定吗？→ 是 → 脚本
- 需要LLM理解，但一步完成？→ 是 → Skill
- 需要多步推理、动态调整？→ 是 → Agent

// VISUAL
Horizontal decision flow diagram. Three sequential diamond shapes in Editorial Blue, each containing a yes/no question. Green "是" arrows lead right to outcome boxes (脚本/Skill/Agent) with matching tier colors. Clean white background, subtle connecting lines.

// LAYOUT
Layout: flow-diagram
Left-to-right flow. Decision diamonds + outcome boxes.

---

## Slide 9 of 14

**Type**: Content
**Filename**: 09-slide-parallel.png

// NARRATIVE GOAL
展示并行任务分发的威力——从"好几天"到"几小时"。

// KEY CONTENT
Headline: 1244篇笔记，从"好几天"到"几小时"
Sub-headline: 并行分发是ROI最高的能力

// VISUAL
Before/after comparison. Left panel (Before): single AI icon with "1244篇" label, downward arrow to clock showing "好几天" in Coral. Right panel (After): one master icon branching into 13 parallel AI icons, downward arrow to clock showing "几小时" in Emerald. Bold "VS" divider between panels. White background.

// LAYOUT
Layout: before-after
Two equal panels with VS divider.

---

## Slide 10 of 14

**Type**: Content
**Filename**: 10-slide-parallel-detail.png

// NARRATIVE GOAL
展示两轮并行分析的具体流程，让读者看清楚实际是怎么操作的。

// KEY CONTENT
Headline: 两轮并行：先扫描，再精读
Body:
- 第一轮：Sonnet × 3批并行快速扫描 → 3份分析报告
- 第二轮：Opus × 13批并行深度精读 → 13份深度报告（约20000字/批）
- 一条指令 → 拆分多个AI并行 → 结果自动回报

// VISUAL
Two-row flow diagram. Top row (第一轮): three Sonnet icons in parallel → merge arrow → 3份报告. Bottom row (第二轮): thirteen Opus icons in parallel → merge arrow → 13份报告. Each row labeled with model name and count. Emerald for Sonnet, Coral for Opus rows. Vertical arrow between rows labeled "成本递进". White background.

// LAYOUT
Layout: two-row-flow
Two parallel flow diagrams stacked.

---

## Slide 11 of 14

**Type**: Content
**Filename**: 11-slide-memory-system.png

// NARRATIVE GOAL
引入记忆系统三层架构——从记录到蒸馏到公理，才是AI真正发挥价值的地方。

// KEY CONTENT
Headline: 三层记忆系统：从记录到蒸馏到公理
Body:
- L1 日常观察：每天事件流水账（原始记录）
- L2 模式提炼：从重复中识别规律，提炼硬性规则
- L3 决策公理：7个类别，46条带置信度的决策公理

// VISUAL
Three horizontal stacked layers, growing narrower toward top (inverted pyramid or layer cake). Bottom (L1): wide bar labeled "L1 日常观察" in Light Gray fill. Middle (L2): narrower bar labeled "L2 模式提炼" in Editorial Blue fill. Top (L3): narrowest bar labeled "L3 决策公理" in Coral fill. Right side: upward arrow labeled "信息密度 × 几百倍". White background.

// LAYOUT
Layout: layer-stack
Three layers with upward distillation arrow on right.

---

## Slide 12 of 14

**Type**: Content
**Filename**: 12-slide-memory-insight.png

// NARRATIVE GOAL
点出最关键洞察：本质是教会AI你的决策风格，大多数人卡在L1是最大浪费。

// KEY CONTENT
Headline: 本质是教会AI你的决策风格
Sub-headline: 1244篇日记 → 46条决策公理，信息密度提升几百倍
Body:
- 大多数人只做L1（记录），从不蒸馏
- AI帮你蒸馏——这可能是AI对个人知识管理最大的价值

// VISUAL
Bold insight callout card. Large "46" in huge Coral numeral left side with label "条决策公理" below. Right side: two-line comparison in styled card — "大多数人：卡在L1" with ❌ icon; "进阶做法：L1→L2→L3蒸馏" with ✓ icon in Emerald. White background.

// LAYOUT
Layout: stat-comparison
Left stat + right insight card.

---

## Slide 13 of 14

**Type**: Content
**Filename**: 13-slide-wechat-api.png

// NARRATIVE GOAL
介绍公众号抓取工具——解锁中文互联网最大内容孤岛，配合AI做内容分析。

// KEY CONTENT
Headline: 微信公众号：中文互联网最大内容孤岛
Sub-headline: 一个API，免登录抓取全文，5分钟完成分析
Body:
- 工具：down.mptext.top（在线版）
- 能力：传入文章链接 → 返回标题+作者+全文+发布时间
- 扩展：批量建知识库、竞品监控、AI摘要翻译

// VISUAL
Magazine-style product explainer. Left: stylized phone/browser mockup showing a WeChat article being "extracted" — flat vector illustration with Editorial Blue phone frame. Right: three-step flow → URL输入 → API抓取 → AI分析. Each step in a numbered card with small icon. Emerald checkmark for result. White background.

// LAYOUT
Layout: product-explainer
Left illustration + right step-by-step flow.

---

## Slide 14 of 14

**Type**: Back Cover
**Filename**: 14-slide-back-cover.png

// NARRATIVE GOAL
总结5条核心原则，给读者带走清单式的行动框架。

// KEY CONTENT
Headline: 5条原则，带走即用
Body:
- ① 模型分级：确定性任务用最便宜的，省出来的钱给Opus
- ② 脚本优先：逻辑确定的任务，脚本比Agent更可靠
- ③ 并行分发：大任务拆批次并行，时间成本断崖下降
- ④ 三层记忆：L1记录 → L2提炼 → L3公理，不要停在L1
- ⑤ 工具开源：中文互联网的内容孤岛，有API可以破

// VISUAL
Clean summary card grid. Five numbered summary cards in 2-column layout (3 top + 2 bottom or 2+2+1). Each card: bold number in Editorial Blue circle, short bold title, one-line description. Card fill: Light Gray. Bottom: subtle editorial closing line "基于真实踩坑，所有数据均为实际使用数据" in Dark Gray italic.

// LAYOUT
Layout: summary-grid
Five cards in organized grid. Editorial closing note at bottom.
