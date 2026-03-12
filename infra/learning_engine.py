#!/usr/bin/env python3
"""
学习引擎 - 成长型记忆的核心
功能：
  - 即时错误捕获
  - 规则应用追踪
  - 模式自动检测
  - 知识图谱关联
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
INFRA_DIR = WORKSPACE / "infra"

# 文件路径
TRIGGERS_FILE = INFRA_DIR / "learning_triggers.json"
RULE_APPS_FILE = INFRA_DIR / "rule_applications.jsonl"
GROWTH_METRICS_FILE = INFRA_DIR / "growth_metrics.json"

INFRA_DIR.mkdir(parents=True, exist_ok=True)


# ===== 即时错误捕获 =====

def capture_error(
    error_type: str,
    description: str,
    context: dict = None,
    severity: str = "medium"
):
    """
    即时捕获错误 - 犯错时立刻调用
    
    Args:
        error_type: "mistake" | "correction" | "discovery"
        description: 错误描述
        context: 上下文信息
        severity: "low" | "medium" | "high"
    
    Returns:
        trigger_id
    """
    trigger = {
        "id": generate_id(),
        "ts": datetime.now().isoformat(),
        "type": error_type,
        "description": description,
        "context": context or {},
        "severity": severity,
        "processed": False,
        "processed_at": None,
        "outcome": None  # lesson | pattern | rule | ignored
    }
    
    # 加载现有触发器
    triggers = load_triggers()
    triggers.append(trigger)
    save_triggers(triggers)
    
    # 高严重度错误直接写入lessons.md
    if severity == "high" and error_type == "mistake":
        auto_create_lesson(trigger)
    
    return trigger["id"]


def capture_correction(description: str, context: dict = None):
    """金哥纠正我时调用"""
    return capture_error("correction", description, context, "high")


def capture_discovery(description: str, context: dict = None):
    """发现新模式/规律时调用"""
    return capture_error("discovery", description, context, "medium")


def capture_mistake(description: str, context: dict = None, severity: str = "medium"):
    """我犯错时调用"""
    return capture_error("mistake", description, context, severity)


def load_triggers() -> list:
    """加载学习触发器"""
    if TRIGGERS_FILE.exists():
        return json.loads(TRIGGERS_FILE.read_text())
    return []


def save_triggers(triggers: list):
    """保存学习触发器"""
    TRIGGERS_FILE.write_text(json.dumps(triggers, ensure_ascii=False, indent=2))


def get_unprocessed_triggers() -> list:
    """获取未处理的触发器"""
    triggers = load_triggers()
    return [t for t in triggers if not t.get("processed")]


def mark_trigger_processed(trigger_id: str, outcome: str):
    """标记触发器已处理"""
    triggers = load_triggers()
    for t in triggers:
        if t["id"] == trigger_id:
            t["processed"] = True
            t["processed_at"] = datetime.now().isoformat()
            t["outcome"] = outcome
            break
    save_triggers(triggers)


# ===== 规则应用追踪 =====

def apply_rule(rule_id: str, context: dict) -> str:
    """
    记录规则应用
    
    Returns:
        application_id
    """
    application = {
        "id": generate_id(),
        "ts": datetime.now().isoformat(),
        "rule_id": rule_id,
        "context": context,
        "outcome": None,  # success | partial | failed
        "score": None,    # 1-10
        "feedback": None
    }
    
    with open(RULE_APPS_FILE, "a") as f:
        f.write(json.dumps(application, ensure_ascii=False) + "\n")
    
    return application["id"]


def record_outcome(application_id: str, outcome: str, score: int, feedback: str = None):
    """
    记录规则应用效果
    
    Args:
        application_id: 应用ID
        outcome: "success" | "partial" | "failed"
        score: 1-10
        feedback: 反馈说明
    """
    # 读取所有应用记录
    applications = []
    if RULE_APPS_FILE.exists():
        with open(RULE_APPS_FILE, "r") as f:
            for line in f:
                applications.append(json.loads(line))
    
    # 找到并更新
    rule_id = None
    for app in applications:
        if app["id"] == application_id:
            app["outcome"] = outcome
            app["score"] = score
            app["feedback"] = feedback
            rule_id = app["rule_id"]
            break
    
    # 重写文件
    with open(RULE_APPS_FILE, "w") as f:
        for app in applications:
            f.write(json.dumps(app, ensure_ascii=False) + "\n")
    
    # 更新规则效用评分
    if rule_id:
        update_rule_utility(rule_id, score)


def get_rule_applications(rule_id: str = None, days: int = 30) -> list:
    """获取规则应用记录"""
    if not RULE_APPS_FILE.exists():
        return []
    
    cutoff = datetime.now() - timedelta(days=days)
    applications = []
    
    with open(RULE_APPS_FILE, "r") as f:
        for line in f:
            app = json.loads(line)
            app_time = datetime.fromisoformat(app["ts"])
            if app_time >= cutoff:
                if rule_id is None or app["rule_id"] == rule_id:
                    applications.append(app)
    
    return applications


def update_rule_utility(rule_id: str, new_score: int):
    """更新规则效用评分"""
    rules_file = MEMORY_DIR / "rules.md"
    if not rules_file.exists():
        return
    
    # 这里简化处理：记录到一个效用追踪文件
    utility_file = INFRA_DIR / "rule_utility.json"
    utility = {}
    if utility_file.exists():
        utility = json.loads(utility_file.read_text())
    
    if rule_id not in utility:
        utility[rule_id] = {"scores": [], "avg": 5.0}
    
    utility[rule_id]["scores"].append({
        "ts": datetime.now().isoformat(),
        "score": new_score
    })
    
    # 计算移动平均（最近10次）
    recent_scores = [s["score"] for s in utility[rule_id]["scores"][-10:]]
    utility[rule_id]["avg"] = sum(recent_scores) / len(recent_scores)
    
    utility_file.write_text(json.dumps(utility, ensure_ascii=False, indent=2))


def get_rule_utility(rule_id: str) -> float:
    """获取规则效用评分"""
    utility_file = INFRA_DIR / "rule_utility.json"
    if not utility_file.exists():
        return 5.0
    
    utility = json.loads(utility_file.read_text())
    return utility.get(rule_id, {}).get("avg", 5.0)


# ===== 模式自动检测 =====

def detect_patterns(days: int = 30) -> list:
    """
    自动检测重复模式
    相似错误出现3次以上 → 提炼为模式
    """
    triggers = load_triggers()
    cutoff = datetime.now() - timedelta(days=days)
    
    # 筛选最近的触发器
    recent = [
        t for t in triggers
        if datetime.fromisoformat(t["ts"]) >= cutoff
        and t["type"] in ["mistake", "correction"]
    ]
    
    # 简单聚类：按描述关键词分组
    clusters = defaultdict(list)
    for t in recent:
        # 提取关键词（简化版）
        key = extract_pattern_key(t["description"])
        clusters[key].append(t)
    
    # 找出出现3次以上的
    patterns = []
    for key, items in clusters.items():
        if len(items) >= 3:
            patterns.append({
                "key": key,
                "count": len(items),
                "triggers": items,
                "suggested_pattern": summarize_pattern(items)
            })
    
    return patterns


def extract_pattern_key(description: str) -> str:
    """提取模式关键词"""
    # 简化版：取前20字符的hash
    # 实际应用中可以用更智能的NLP方法
    return hashlib.md5(description[:50].encode()).hexdigest()[:8]


def summarize_pattern(triggers: list) -> str:
    """生成模式描述"""
    descriptions = [t["description"] for t in triggers]
    # 简化版：取第一个描述
    # 实际应用中可以用LLM生成总结
    return f"重复出现的问题：{descriptions[0][:100]}..."


# ===== 知识图谱关联 =====

def add_knowledge_link(
    source_id: str,
    target_id: str,
    link_type: str,
    strength: float = 1.0
):
    """
    添加知识关联
    
    Args:
        source_id: 源知识ID
        target_id: 目标知识ID
        link_type: "semantic" | "temporal" | "causal"
        strength: 关联强度 0-1
    """
    kg_file = MEMORY_DIR / "knowledge-graph.md"
    links_file = INFRA_DIR / "kg_links.json"
    
    links = []
    if links_file.exists():
        links = json.loads(links_file.read_text())
    
    links.append({
        "ts": datetime.now().isoformat(),
        "source": source_id,
        "target": target_id,
        "type": link_type,
        "strength": strength
    })
    
    links_file.write_text(json.dumps(links, ensure_ascii=False, indent=2))


def calculate_connection_density() -> float:
    """计算知识连接密度"""
    links_file = INFRA_DIR / "kg_links.json"
    if not links_file.exists():
        return 0.0
    
    links = json.loads(links_file.read_text())
    
    # 统计节点数
    nodes = set()
    for link in links:
        nodes.add(link["source"])
        nodes.add(link["target"])
    
    if len(nodes) == 0:
        return 0.0
    
    return len(links) / len(nodes)


# ===== 成长指标 =====

def calculate_growth_metrics() -> dict:
    """计算成长指标"""
    triggers = load_triggers()
    
    # 1. 错误捕获率（最近7天）
    recent_triggers = [
        t for t in triggers
        if datetime.fromisoformat(t["ts"]) >= datetime.now() - timedelta(days=7)
    ]
    
    # 2. 教训转化率
    processed = [t for t in triggers if t.get("processed")]
    to_lesson = [t for t in processed if t.get("outcome") == "lesson"]
    conversion_rate = len(to_lesson) / len(processed) if processed else 0
    
    # 3. 错误重复率
    mistake_keys = [extract_pattern_key(t["description"]) for t in triggers if t["type"] == "mistake"]
    unique_keys = set(mistake_keys)
    repeat_rate = 1 - (len(unique_keys) / len(mistake_keys)) if mistake_keys else 0
    
    # 4. 规则效用
    utility_file = INFRA_DIR / "rule_utility.json"
    avg_utility = 5.0
    if utility_file.exists():
        utility = json.loads(utility_file.read_text())
        if utility:
            avg_utility = sum(r["avg"] for r in utility.values()) / len(utility)
    
    # 5. 连接密度
    connection_density = calculate_connection_density()
    
    metrics = {
        "ts": datetime.now().isoformat(),
        "triggers_7d": len(recent_triggers),
        "lesson_conversion_rate": round(conversion_rate, 2),
        "error_repeat_rate": round(repeat_rate, 2),
        "avg_rule_utility": round(avg_utility, 2),
        "connection_density": round(connection_density, 2)
    }
    
    # 保存指标
    GROWTH_METRICS_FILE.write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
    
    return metrics


# ===== 辅助函数 =====

def generate_id() -> str:
    """生成唯一ID"""
    import uuid
    return str(uuid.uuid4())[:8]


def auto_create_lesson(trigger: dict):
    """自动创建教训条目"""
    lessons_file = MEMORY_DIR / "lessons.md"
    
    if not lessons_file.exists():
        return
    
    content = lessons_file.read_text()
    
    # 找到最后一个教训编号
    import re
    matches = re.findall(r'### L(\d+)', content)
    next_num = max([int(m) for m in matches], default=0) + 1
    
    # 生成新教训
    date = datetime.now().strftime("%Y-%m-%d")
    new_lesson = f"""

### L{next_num:03d} - {trigger['description'][:50]}
- **日期：** {date}
- **类型：** {trigger['type']}
- **严重度：** {trigger['severity']}
- **上下文：** {json.dumps(trigger.get('context', {}), ensure_ascii=False)}
- **教训：** [待补充]
- **改进措施：** [待补充]
"""
    
    # 追加到文件
    with open(lessons_file, "a") as f:
        f.write(new_lesson)
    
    # 标记触发器已处理
    mark_trigger_processed(trigger["id"], "lesson")


# ===== 命令行接口 =====

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 learning_engine.py capture <type> <description> [severity]")
        print("  python3 learning_engine.py triggers")
        print("  python3 learning_engine.py patterns")
        print("  python3 learning_engine.py metrics")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "capture":
        error_type = sys.argv[2] if len(sys.argv) > 2 else "mistake"
        description = sys.argv[3] if len(sys.argv) > 3 else "未指定描述"
        severity = sys.argv[4] if len(sys.argv) > 4 else "medium"
        trigger_id = capture_error(error_type, description, {}, severity)
        print(f"✅ 已捕获错误: {trigger_id}")
    
    elif cmd == "triggers":
        triggers = get_unprocessed_triggers()
        print(f"未处理触发器: {len(triggers)}")
        for t in triggers:
            print(f"  - [{t['type']}] {t['description'][:50]}...")
    
    elif cmd == "patterns":
        patterns = detect_patterns()
        print(f"检测到模式: {len(patterns)}")
        for p in patterns:
            print(f"  - {p['key']}: {p['count']}次")
    
    elif cmd == "metrics":
        metrics = calculate_growth_metrics()
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
