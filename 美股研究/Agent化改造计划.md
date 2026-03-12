# 金哥的 Agent 化改造计划

**灵感来源**: @xingpt 的个人业务 Agent 化实践  
**制定日期**: 2026-02-23  
**执行周期**: 4 周

---

## 🎯 改造目标

### 量化指标
- **时间效率**: 每日投研时间从 X小时 → 1小时
- **信息覆盖**: 从单一数据源 → 20+ 信息源自动聚合
- **决策质量**: 建立标准化决策框架，减少情绪影响

### 核心转变
从 "手动查信息 → 人工分析 → 凭感觉决策"  
到 "Agent 聚合 → 框架判断 → 数据驱动决策"

---

## 🏗️ 三层架构实施

### 第一层：知识库扩展

#### 已完成 ✅
1. **观察名单** (`watchlist.json`)
   - 芯链：NVDA, MSFT, TSM, AMD, ASML
   - 能量：CEG, CCJ, XOM, NEE

2. **RSS 新闻源** (`rss_feeds.json`)
   - 金融：Reuters, MarketWatch, CNBC, SeekingAlpha, Yahoo
   - 科技：TechCrunch, The Verge, Ars Technica, VentureBeat
   - 能源：World Nuclear News, OilPrice, Energy.gov

3. **投资日志**
   - 每日情报简报
   - 新闻聚合记录

#### 待完善 ⏳

**1. 历史数据库**（第1周）
```
美股研究/
├── 数据库/
│   ├── 宏观数据/
│   │   ├── 美联储利率历史.csv
│   │   ├── CPI_通胀数据.csv
│   │   ├── 非农就业数据.csv
│   │   └── GDP_增长率.csv
│   ├── 公司财报/
│   │   ├── NVDA_财报历史.json
│   │   ├── CEG_财报历史.json
│   │   └── ...
│   └── 市场事件/
│       ├── 2008_金融危机复盘.md
│       ├── 2020_疫情暴跌复盘.md
│       └── 2022_加息周期复盘.md
```

**数据来源**:
- yfinance (历史股价、财报)
- FRED API (宏观数据)
- Alpha Vantage (技术指标)

**2. 实时监控扩展**（第2周）
```python
# 添加到 watchlist.json
"监控指标": {
  "宏观流动性": {
    "美联储资产": "FRED API",
    "TGA账户": "财政部网站",
    "ON RRP": "纽联储",
    "SOFR": "CME"
  },
  "市场情绪": {
    "VIX": "yfinance",
    "MOVE指数": "Bloomberg API",
    "Put/Call比率": "CBOE"
  },
  "资金流向": {
    "散户净买入": "摩根大通数据",
    "机构仓位": "13F文件追踪"
  }
}
```

**3. 个人经验库**（第1周）
```
美股研究/
├── 决策记录/
│   ├── YYYY-MM-DD_买入_NVDA.md
│   ├── YYYY-MM-DD_卖出_XOM.md
│   └── ...
└── 复盘笔记/
    ├── 2026-02_市场暴跌复盘.md
    └── ...
```

**模板**:
```markdown
# 决策记录

**日期**: 2026-02-23  
**操作**: 买入 / 卖出  
**标的**: NVDA  
**价格**: $XXX  
**仓位**: XX%

## 决策依据
1. 技术面：RSI超卖，周线级别支撑
2. 基本面：Q4财报超预期，AI芯片订单强劲
3. 宏观面：美联储降息预期升温

## 预期收益
- 目标价：$XXX
- 止损价：$XXX
- 预期收益率：XX%

## 复盘 (3个月后)
- 实际收益率：XX%
- 判断正确性：✅ / ❌
- 经验教训：...
```

---

### 第二层：Skills 决策框架

#### 待开发 Skills

**Skill 1: 价值投资筛选**
```python
# 文件: skills/value_investing.py

def evaluate_stock(ticker):
    """
    价值投资评估框架
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # 判断标准
    criteria = {
        "ROE": info.get("returnOnEquity", 0) > 0.15,  # >15%
        "debt_ratio": info.get("debtToEquity", 100) < 50,  # <50%
        "fcf_ratio": check_fcf_ratio(ticker),  # FCF > 80% 净利润
        "moat": assess_moat(ticker)  # 护城河评估
    }
    
    # 计分
    score = sum(criteria.values())
    
    # 评级
    if score >= 4: return "A - 强烈买入"
    elif score == 3: return "B - 买入"
    elif score == 2: return "C - 观望"
    else: return "D - 回避"
```

**Skill 2: 芯片行业周期判断**
```python
# 文件: skills/chip_cycle.py

def chip_cycle_indicator():
    """
    芯片行业周期指标
    """
    indicators = {
        # 供需指标
        "DRAM价格": get_dram_price_trend(),  # 上涨→需求旺盛
        "NAND价格": get_nand_price_trend(),
        
        # 订单指标
        "台积电产能利用率": get_tsm_utilization(),  # >90%→高景气
        "ASML光刻机订单": get_asml_orders(),
        
        # 终端需求
        "PC出货量": get_pc_shipment(),
        "智能手机出货量": get_smartphone_shipment(),
        "数据中心资本开支": get_datacenter_capex(),
        
        # AI需求
        "GPU订单交付周期": get_gpu_lead_time(),  # 拉长→需求强劲
        "HBM价格": get_hbm_price()
    }
    
    # 综合判断
    if 景气度 > 80: return "上行周期 - 加仓芯片股"
    elif 景气度 < 30: return "下行周期 - 减仓等待"
    else: return "震荡期 - 精选个股"
```

**Skill 3: 核能行业催化剂追踪**
```python
# 文件: skills/nuclear_catalyst.py

def nuclear_catalyst_tracker():
    """
    核能行业催化剂追踪
    """
    catalysts = {
        # 政策层面
        "新建核电站审批": monitor_new_approvals(),
        "碳税政策": monitor_carbon_tax(),
        "可再生能源补贴变化": monitor_subsidy(),
        
        # 供需层面
        "铀价": get_uranium_price(),  # 突破$XX→利好矿企
        "铀矿产量": get_uranium_production(),
        "核电装机容量": get_nuclear_capacity(),
        
        # 技术层面
        "SMR(小型堆)商业化进展": monitor_smr(),
        "核聚变突破": monitor_fusion(),
        
        # 公司层面
        "CEG并购动态": monitor_ceg_ma(),
        "CCJ产量指引": monitor_ccj_production()
    }
    
    # 触发条件
    if 铀价突破历史高点:
        return "强烈看多铀矿股 (CCJ)"
    elif 新建核电站审批加速:
        return "看多核电运营商 (CEG)"
```

**Skill 4: 流动性监控预警**
```python
# 文件: skills/liquidity_monitor.py

def liquidity_alert():
    """
    流动性监控与预警（参考作者的框架）
    """
    # 净流动性
    fed_balance = get_fed_balance_sheet()
    tga = get_tga_balance()
    rrp = get_rrp_balance()
    net_liquidity = fed_balance - tga - rrp
    
    # 变化率
    nl_change_weekly = (net_liquidity - net_liquidity_last_week) / net_liquidity_last_week
    
    # 利率指标
    sofr = get_sofr_rate()
    
    # 波动率
    move_index = get_move_index()
    
    # 汇率与利差
    usdjpy = get_usdjpy()
    us2y_jp2y_spread = get_spread("US2Y", "JP2Y")
    
    # 预警逻辑
    alerts = []
    
    if nl_change_weekly < -0.05:
        alerts.append("🚨 净流动性单周下降 >5%")
    
    if sofr > 5.5:
        alerts.append("⚠️ SOFR突破5.5%，减仓风险资产")
    
    if move_index > 130:
        alerts.append("🚨 MOVE指数>130，美债波动剧烈，止损风险资产")
    
    if us2y_jp2y_spread < 1.5 and usdjpy < 145:
        alerts.append("⚠️ 日元套利交易平仓风险")
    
    return {
        "level": "CRITICAL" if len(alerts) >= 3 else "WARNING" if alerts else "OK",
        "alerts": alerts,
        "recommendation": generate_recommendation(alerts)
    }
```

**Skill 5: 爆款内容框架**（借鉴作者）
```python
# 文件: skills/content_framework.py

TITLE_TEMPLATES = {
    "数字冲击型": [
        "{标的}暴涨{XX}%后，我发现了...",
        "年薪150万的投资经理，用{XX}美元的AI完成",
        "持仓{XX}万美元，我总结了..."
    ],
    "反常识型": [
        "为什么{标的}大涨，我却选择卖出",
        "所有人都在买{板块}，我为什么反其道而行",
        "市场认为{观点}，我认为恰恰相反"
    ],
    "价值承诺型": [
        "如何用{方法}筛选10倍股",
        "{板块}投资完全指南（收藏版）",
        "我用这套框架，{时间}内收益{XX}%"
    ]
}

OPENING_TEMPLATES = {
    "具体事件": "2026年2月23日，{具体事件}发生了...",
    "极端对比": "如果你继续{当前做法}... 但6个月后{可能结果}...",
    "先破后立": "市场上主流观点是{观点A/B/C}，我认为以上都不对..."
}

def generate_outline(topic, data):
    """
    生成文章大纲
    """
    return {
        "title_options": [
            generate_title(topic, "数字冲击型"),
            generate_title(topic, "反常识型"),
            generate_title(topic, "价值承诺型")
        ],
        "opening": generate_opening(topic, "具体事件"),
        "structure": [
            {"section": "核心论点", "content": data["thesis"]},
            {"section": "数据支撑", "content": data["data"]},
            {"section": "案例验证", "content": data["case"]},
            {"section": "反面论证", "content": data["counter"]},
            {"section": "行动建议", "content": data["action"]}
        ],
        "visuals": generate_chart_suggestions(data)
    }
```

---

### 第三层：CRON 自动化升级

#### 当前状态 ✅
```
8:30 AM - 情报官V2（价格+财报+新闻30条）
5:30 AM - 收盘复盘
```

#### 升级计划（第3周）

**新增任务**:

**1. 每日策略生成**（8:35 AM）
```python
# 基于8:30情报，自动生成策略建议

输入:
  - 价格快照（涨跌幅、52周位置）
  - 新闻摘要（重大事件）
  - 流动性指标（来自 Skill 4）

处理:
  - 匹配历史相似场景
  - 应用决策 Skills
  - 生成仓位建议

输出:
  📊 今日策略建议
  - 市场环境：流动性{宽松/收紧}，情绪{贪婪/恐慌}
  - 核心观点：{1-2句话}
  - 操作建议：
    · 芯链板块：{加仓/减仓/持有} - {理由}
    · 能量板块：{加仓/减仓/持有} - {理由}
  - 风险提示：{关键风险}
```

**2. 周末深度研报**（周日 10:00 AM）
```python
# 每周生成深度研究报告

内容:
  - 本周市场回顾（涨跌+关键事件）
  - 核心标的分析（运行 Skill 1 价值投资筛选）
  - 行业趋势判断（运行 Skill 2/3 行业周期）
  - 下周关键日程（财报、经济数据）
  - 投资组合建议

格式:
  - Markdown（存档）
  - Telegram（推送摘要）
```

**3. 月度复盘**（每月1日 09:00 AM）
```python
# 自动生成月度复盘

分析维度:
  - 收益率统计（各标的表现）
  - 决策复盘（哪些对了，哪些错了）
  - Skills 优化（哪个框架需要调整）
  - 市场总结（主要驱动因素）

自动化:
  - 读取「决策记录」文件夹
  - 对比实际收益 vs 预期收益
  - 标记判断失误的案例
  - 生成改进建议
```

---

## 📅 实施时间表

### 第1周（2026-02-24 - 03-02）
- [ ] 创建数据库文件夹结构
- [ ] 下载宏观数据历史（FRED API）
- [ ] 建立决策记录模板
- [ ] 补充过往决策记录（至少10条）

### 第2周（2026-03-03 - 03-09）
- [ ] 开发 Skill 1: 价值投资筛选
- [ ] 开发 Skill 4: 流动性监控
- [ ] 测试 Skills 准确性
- [ ] 添加实时监控指标（VIX, MOVE等）

### 第3周（2026-03-10 - 03-16）
- [ ] 开发 Skill 2: 芯片周期判断
- [ ] 开发 Skill 3: 核能催化剂追踪
- [ ] 配置 CRON: 每日策略生成
- [ ] 配置 CRON: 周末深度研报

### 第4周（2026-03-17 - 03-23）
- [ ] 开发 Skill 5: 内容框架（如果需要）
- [ ] 配置 CRON: 月度复盘
- [ ] 完整系统测试
- [ ] 优化调整

---

## 🎯 成功标准

### 量化指标
1. **时间节省**: 每日投研时间 < 1小时
2. **信息覆盖**: 自动监控 20+ 指标
3. **决策质量**: 月度复盘准确率 > 70%

### 质性指标
1. **思维转变**: 从"我该做什么"到"Agent该怎么做"
2. **情绪管理**: 决策基于框架，而非临时冲动
3. **可复制性**: 系统可以迁移到其他领域

---

## 💡 关键认知

### 从作者学到的
1. **Agent化不是可选项，是必选项**
   - 时间换收入的模式天花板已定
   - 算法杠杆可以突破物理限制

2. **知识库是基础，Skills是灵魂**
   - 数据只是原料
   - 判断框架才是核心竞争力

3. **持续优化比一次性完美更重要**
   - 先跑通最小闭环
   - 每周复盘迭代

4. **商业化路径清晰**
   - 个人使用 → 咨询服务 → 产品化
   - 从 SaaS 到 AaaS

---

## 🚀 下一步行动

**本周立即执行**:
1. 创建文件夹结构
2. 补充3-5条历史决策记录
3. 下载美联储利率、CPI历史数据

**需要金哥配合**:
1. 确认决策记录模板是否合适
2. 提供过往投资决策案例（如有）
3. 明确优先级（投研 vs 内容）

---

*参考来源: @xingpt 推文*  
*制定人: 紫龙 🐉*  
*最后更新: 2026-02-23*
