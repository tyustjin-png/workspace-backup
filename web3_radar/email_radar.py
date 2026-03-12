import os
import imaplib
import smtplib
import email
import requests
from email.header import decode_header
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 初始化 Gemini 2.0 Client
client = genai.Client(api_key=GEMINI_API_KEY)

# 固定随机种子
RANDOM_SEED = 42

# ============================================================
# 顶级机构名单
# ============================================================
TIER1_VCS = [
    "Binance Labs", "YZi Labs", "Coinbase Ventures", "OKX Ventures", "Kraken Ventures",
    "a16z", "Andreessen Horowitz", "Paradigm", "Polychain", "Multicoin Capital",
    "Dragonfly", "Pantera Capital", "Framework Ventures", "Variant Fund",
    "Sequoia", "Tiger Global", "Lightspeed", "Founders Fund", "Union Square Ventures",
    "Delphi Digital", "Jump Crypto", "Wintermute", "GSR",
    "Hack VC", "Robot Ventures", "1kx", "Electric Capital", "Placeholder",
    "Blockchain Capital", "Galaxy Digital", "Digital Currency Group", "DCG",
    "Hashkey", "Animoca Brands", "Spartan Group"
]

# DeFiLlama 赛道中英文映射
CATEGORY_MAP = {
    "Liquid Staking": "流动性质押",
    "Lending": "借贷",
    "Dexes": "DEX",
    "Bridge": "跨链桥",
    "CDP": "稳定币铸造",
    "Restaking": "再质押",
    "Liquid Restaking": "流动性再质押",
    "Yield": "收益",
    "Derivatives": "衍生品",
    "RWA": "RWA",
    "Cross Chain": "跨链",
    "Yield Aggregator": "收益聚合",
    "Prediction Market": "预测市场",
    "Perpetuals": "永续合约",
    "Options": "期权",
    "Payments": "支付",
}


def get_email_body(msg):
    """提取邮件纯文本内容"""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    for encoding in ['utf-8', 'gbk', 'iso-8859-1', 'ascii']:
                        try:
                            return payload.decode(encoding)
                        except:
                            continue
                    return payload.decode('utf-8', errors='ignore')
                except:
                    continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            for encoding in ['utf-8', 'gbk', 'iso-8859-1', 'ascii']:
                try:
                    return payload.decode(encoding)
                except:
                    continue
            return payload.decode('utf-8', errors='ignore')
        except:
            return ""
    return ""


def decode_subject(subject_header):
    """安全解码邮件标题"""
    if not subject_header:
        return "(无标题)"
    decoded_parts = decode_header(subject_header)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(encoding if encoding else 'utf-8'))
            except:
                result.append(part.decode('utf-8', errors='ignore'))
        else:
            result.append(part)
    return ''.join(result)


def fetch_defillama_revenue():
    """
    从 DeFiLlama 获取协议收入排行榜
    返回: top_revenue (收入榜), top_growth (增长榜)
    """
    print(">>> 获取 DeFiLlama 收入排行数据...")

    try:
        response = requests.get(
            "https://api.llama.fi/overview/fees",
            params={
                "excludeTotalDataChart": "true",
                "excludeTotalDataChartBreakdown": "true",
                "dataType": "dailyRevenue"
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        protocols = data.get("protocols", [])

        # 过滤有效数据
        valid = [p for p in protocols if p.get("total24h") and p.get("total24h") > 10000]

        # Top 10 收入榜
        top_revenue = sorted(valid, key=lambda x: x.get("total24h", 0), reverse=True)[:10]
        top_revenue = [{
            "name": p.get("displayName", p.get("name")),
            "revenue_24h": p.get("total24h", 0),
            "revenue_7d": p.get("total7d", 0),
            "change_1d": p.get("change_1d", 0) or 0,
            "category": p.get("category", "N/A")
        } for p in top_revenue]

        # Top 10 增长榜 (24h变化 > 20%)
        growing = [p for p in valid if (p.get("change_1d") or 0) > 20]
        top_growth = sorted(growing, key=lambda x: x.get("change_1d", 0), reverse=True)[:10]
        top_growth = [{
            "name": p.get("displayName", p.get("name")),
            "revenue_24h": p.get("total24h", 0),
            "change_1d": p.get("change_1d", 0) or 0,
            "category": p.get("category", "N/A")
        } for p in top_growth]

        return top_revenue, top_growth

    except Exception as e:
        print(f">>> DeFiLlama 收入数据请求失败: {e}")
        return [], []


def fetch_defillama_flows():
    """
    从 DeFiLlama 获取各赛道 TVL 7日变化数据
    返回资金流入/流出的赛道列表
    """
    print(">>> 获取 DeFiLlama 资金流向数据...")

    try:
        response = requests.get("https://api.llama.fi/protocols", timeout=15)
        response.raise_for_status()
        protocols = response.json()

        # 按赛道聚合
        category_stats = {}
        for p in protocols:
            cat = p.get("category", "Unknown")
            tvl = p.get("tvl", 0) or 0
            change_7d = p.get("change_7d", 0) or 0

            if cat not in category_stats:
                category_stats[cat] = {"tvl": 0, "weighted_change": 0}

            category_stats[cat]["tvl"] += tvl
            category_stats[cat]["weighted_change"] += tvl * change_7d

        # 计算加权变化率
        result = []
        for cat, stats in category_stats.items():
            if stats["tvl"] > 50_000_000:  # TVL > $50M
                avg_change = stats["weighted_change"] / stats["tvl"] if stats["tvl"] > 0 else 0
                cn_name = CATEGORY_MAP.get(cat, cat)
                result.append({
                    "name": f"{cn_name}({cat})",
                    "tvl_b": stats["tvl"] / 1e9,
                    "change_7d": avg_change
                })

        # 分离流入和流出
        inflows = sorted([r for r in result if r["change_7d"] > 3], key=lambda x: x["change_7d"], reverse=True)[:10]
        outflows = sorted([r for r in result if r["change_7d"] < -3], key=lambda x: x["change_7d"])[:8]

        return inflows, outflows

    except Exception as e:
        print(f">>> DeFiLlama 请求失败: {e}")
        return [], []


def build_prompt(email_count, all_content, inflows, outflows):
    """构建提示词"""

    vc_list = ", ".join(TIER1_VCS[:20])

    # 资金流向文本
    flow_text = "## 本周资金流向（DeFiLlama 实时数据）\n\n"
    if inflows:
        flow_text += "【🔥 资金流入赛道（7日TVL增长>3%）】\n"
        for f in inflows:
            flow_text += f"  - {f['name']}: TVL ${f['tvl_b']:.1f}B, 7日 +{f['change_7d']:.1f}%\n"
        flow_text += "\n"
    if outflows:
        flow_text += "【❄️ 资金流出赛道（7日TVL下降>3%）】\n"
        for f in outflows:
            flow_text += f"  - {f['name']}: TVL ${f['tvl_b']:.1f}B, 7日 {f['change_7d']:.1f}%\n"
        flow_text += "\n"
    if not inflows and not outflows:
        flow_text += "（数据获取失败，跳过此参考）\n\n"

    return f"""
# 角色设定
你是【Web3 早期项目猎手】—— 专注发现高赔率早期机会的投资分析师。

# 用户画像
- 身份：Web3工作室主理人
- 资源：有执行团队，可批量撸毛/深度参与
- 决策偏好：高赔率早期项目 > 高确定性成熟项目

{flow_text}

# ===== 核心筛选漏斗 =====

## 漏斗1: 聪明钱信号
识别顶级机构投资动向，出现必须高亮：
{vc_list}

轮次权重：种子轮 > A轮 > B轮+

## 漏斗2: 机制新颖性判断（核心！）

这是最重要的筛选标准。判断该项目是否具有**市场上从未出现过的新玩法**：

【什么是机制创新】
- 全新代币经济模型（如 Pump.fun 的联合曲线发射、Friend.tech 的社交绑定曲线）
- 全新交互范式（如 Polymarket 的预测市场下注、Blur 的积分空投博弈）
- 全新技术路线（如 EigenLayer 的再质押、Celestia 的模块化DA）
- 全新商业模式（如 Helium 的去中心化通信网络、Render 的GPU共享）

【什么不是机制创新】
- 换个链部署的同类项目（又一个L2、又一个DEX、又一个借贷）
- 微调参数的仿盘（手续费低一点、速度快一点）
- 换个皮肤的老玩法（NFT换个主题、GameFi换个IP）

【标注规则】
- 如果有机制创新 → 必须标注【机制创新】并用1-2句话说明创新点
- 如果是仿盘/微创新 → 标注【常规模式】

## 漏斗3: 赛道五问模型

问题1. 赛道定位：属于哪个细分赛道？
问题2. 赛道阶段：
    | 黎明期 | 无龙一，玩家<5个 | 高赔率 |
    | 爆发期 | 龙一确立，龙二争夺 | 找差异 |
    | 成熟期 | 格局固化 | 放弃或找细分 |
问题3. 龙一是谁：赛道统治者
问题4. 卡位判断：挑战者 vs 跟随者
问题5. 资源分配：
    | S级 | 机制创新 + 顶级背书 + 黎明期赛道 | 主力All-in |
    | A级 | 有差异化 + 爆发期赛道 | 重点关注 |
    | B级 | 常规模式但有机构 | 防身参与 |
    | C级 | 仿盘/无亮点 | 放弃 |

## 漏斗4: 资金流向参考
- 项目所属赛道在"资金流入"列表 → 加分项
- 项目所属赛道在"资金流出"列表 → 减分项（但不一票否决）

## 漏斗5: 信息提取
必须提取：项目名称、融资+投资方、代币信息、操作入口、截止时间

## 漏斗6: 市场情报深度提取

对于研报类/数据分析类邮件，必须进行深度提取：

【研报类型判定】
- 宏观研判：市场周期分析、行情预测、资金流向、市场情绪
- 赛道深度：某细分赛道全景分析、竞争格局、发展趋势
- 数据报告：链上数据统计、交易所数据、用户行为分析
- 项目研究：单个/多个项目深度对比
- 监管政策：各国加密政策动态、合规进展

【提取要求】
1. 核心观点：提取研报的1-3个核心结论，用①②③标注
2. 关键数据：必须提取具体数字（TVL、交易量、用户数、涨跌幅、市占率等）
3. 提及项目：列出研报中重点分析的项目名称
4. 工作室启示：基于研报内容，给出1句话可执行建议

【常见研报来源识别】
- Messari, Delphi Digital, The Block, Bankless → 高质量研报
- Glassnode, Nansen, Dune → 数据报告
- 各交易所研究院 → 市场分析

# ===== 输出规范 =====

## 格式
- 纯HTML，全中文，结论直接

## 高亮
- 项目名 → <span style="background:#c8e6c9;padding:2px 6px;border-radius:4px;"><b>名</b></span>
- 顶级机构 → <span style="background:#bbdefb;padding:2px 6px;border-radius:4px;"><b>名</b></span>
- 机制创新 → <span style="background:#fff9c4;padding:2px 6px;border-radius:4px;"><b>【机制创新】</b></span>
- 常规模式 → <span style="color:#9e9e9e;">【常规模式】</span>
- S级边框 → border-left: 4px solid #ffd54f
- A级边框 → border-left: 4px solid #42a5f5
- B级边框 → border-left: 4px solid #bdbdbd

## 输出结构

<h3 style="color:#c62828;">紧急事项</h3>
<ul><li><b>[来源]</b>: 事项 + 操作</li></ul>
<p style="color:#9e9e9e;font-size:0.85em;">若无：暂无紧急事项</p>

<h3 style="color:#2e7d32;">早期机会</h3>
<!-- S→A→B排序，C级不输出 -->
<div style="background:#fafafa; padding:16px; border-radius:8px; margin:12px 0; border-left:4px solid #ffd54f;">
    <div style="margin-bottom:8px;">
        <span style="background:#c8e6c9;padding:2px 6px;border-radius:4px;"><b>[项目名]</b></span>
        <span style="background:#fff9c4;padding:2px 6px;border-radius:4px;margin-left:4px;"><b>【机制创新】</b></span>
        <span style="float:right;background:#ffcc80;padding:2px 8px;border-radius:4px;font-weight:bold;">S级</span>
    </div>
    <div style="font-size:0.95em;color:#333;"><b>核心判断</b>: [定性]</div>
    <table style="width:100%;font-size:0.88em;margin-top:10px;border-collapse:collapse;">
        <tr><td style="padding:6px 0;border-bottom:1px solid #eee;width:28%;color:#666;">融资背书</td>
            <td style="padding:6px 0;border-bottom:1px solid #eee;"><span style="background:#bbdefb;padding:2px 6px;border-radius:4px;"><b>机构</b></span> | 金额</td></tr>
        <tr><td style="padding:6px 0;border-bottom:1px solid #eee;color:#666;">机制判断</td>
            <td style="padding:6px 0;border-bottom:1px solid #eee;"><b>【机制创新】</b>: [1-2句说明创新点] 或 【常规模式】</td></tr>
        <tr><td style="padding:6px 0;border-bottom:1px solid #eee;color:#666;">赛道阶段</td>
            <td style="padding:6px 0;border-bottom:1px solid #eee;">[赛道] @ <b>黎明期/爆发期/成熟期</b></td></tr>
        <tr><td style="padding:6px 0;border-bottom:1px solid #eee;color:#666;">格局分析</td>
            <td style="padding:6px 0;border-bottom:1px solid #eee;">龙一=<b>[X]</b> | 本项目=<b>挑战者/跟随者</b></td></tr>
        <tr><td style="padding:6px 0;border-bottom:1px solid #eee;color:#666;">资金流向</td>
            <td style="padding:6px 0;border-bottom:1px solid #eee;">🔥流入 / ❄️流出 / ➖无明显变化</td></tr>
        <tr><td style="padding:6px 0;border-bottom:1px solid #eee;color:#666;">执行指南</td>
            <td style="padding:6px 0;border-bottom:1px solid #eee;">[步骤/链接]</td></tr>
        <tr><td style="padding:6px 0;color:#666;">工作室策略</td>
            <td style="padding:6px 0;"><b style="color:#2e7d32;">[主力All-in/重点关注/防身参与]</b> - [理由]</td></tr>
    </table>
</div>
<p style="color:#9e9e9e;font-size:0.85em;">若无：本批次无早期机会</p>

<h3 style="color:#1565c0;">市场情报</h3>
<!-- 研报/数据分析/行业洞察归入此类，按重要性排序 -->

<div style="background:#fff; border:1px solid #e0e0e0; border-radius:8px; padding:14px; margin:10px 0;">
    <div style="margin-bottom:6px;">
        <span style="background:#e3f2fd;padding:2px 8px;border-radius:4px;font-size:0.8em;color:#1565c0;">[研报类型]</span>
        <b style="margin-left:6px;">[研报标题/主题]</b>
        <span style="float:right;font-size:0.8em;color:#9e9e9e;">[来源]</span>
    </div>
    <table style="width:100%;font-size:0.88em;border-collapse:collapse;">
        <tr><td style="padding:5px 0;border-bottom:1px solid #f5f5f5;width:22%;color:#666;vertical-align:top;">核心观点</td>
            <td style="padding:5px 0;border-bottom:1px solid #f5f5f5;">[1-3个要点，用①②③标注]</td></tr>
        <tr><td style="padding:5px 0;border-bottom:1px solid #f5f5f5;color:#666;vertical-align:top;">关键数据</td>
            <td style="padding:5px 0;border-bottom:1px solid #f5f5f5;">[提取研报中的具体数字/百分比/排名等]</td></tr>
        <tr><td style="padding:5px 0;border-bottom:1px solid #f5f5f5;color:#666;vertical-align:top;">提及项目</td>
            <td style="padding:5px 0;border-bottom:1px solid #f5f5f5;">[研报中重点提及的项目名称，逗号分隔]</td></tr>
        <tr><td style="padding:5px 0;color:#1565c0;vertical-align:top;">工作室启示</td>
            <td style="padding:5px 0;"><b>[基于研报内容，对工作室的1句话建议]</b></td></tr>
    </table>
</div>

<!-- 研报类型说明（供你判断用，不输出）：
- 宏观研判：市场周期/行情预测/资金流向分析
- 赛道深度：某个细分赛道的全景分析
- 数据报告：链上数据/交易所数据/用户行为统计
- 项目研究：单个或多个项目的对比研究
- 监管政策：各国加密监管动态
-->

<p style="color:#9e9e9e;font-size:0.85em;">若无：本批次无市场研报</p>

<h3 style="color:#757575;">资讯流</h3>
<ul style="font-size:0.9em;">
    <li><b>[来源]</b>: 快讯摘要</li>
</ul>
<p style="color:#9e9e9e;font-size:0.85em;">若无：本批次无资讯</p>

<h3 style="color:#9e9e9e;">处理清单（共{email_count}封）</h3>
<div style="font-size:0.8em;color:#757575;columns:2;">
    <div>1. [标题] → [分类]</div>
</div>

# ===== 强制规则 =====
1. 共 {email_count} 封邮件，必须全部处理
2. 机制新颖性是最重要的判断标准，必须明确标注【机制创新】或【常规模式】
3. 机制创新的项目即使赛道拥挤也可以评A级以上
4. 常规模式的项目最高B级
5. 全部输出使用中文
6. 市场情报必须使用表格格式，必须提取具体数据，不能只写"详见原文"
7. 研报类邮件的"工作室启示"必须是可执行的建议，不能是泛泛而谈

# ===== 输入数据 =====
{all_content}
"""


def send_summary_email(summary_text, inflows, outflows, top_revenue=None, top_growth=None):
    """发送邮件"""
    html_content = summary_text.replace("```html", "").replace("```", "").strip()

    # 收入榜摘要
    revenue_summary = ""
    if top_revenue:
        rev_items = [f"{r['name']} ${r['revenue_24h']/1000:.0f}K" for r in top_revenue[:5]]
        revenue_summary = f"<b>💰 24h收入Top5:</b> {', '.join(rev_items)}<br>"
    if top_growth:
        growth_items = [f"{g['name']} +{g['change_1d']:.0f}%" for g in top_growth[:3]]
        revenue_summary += f"<b>🚀 收入飙升:</b> {', '.join(growth_items)}<br>"

    # 资金流向摘要
    flow_summary = ""
    if inflows:
        flow_items = [f"{f['name']} +{f['change_7d']:.0f}%" for f in inflows[:5]]
        flow_summary += f"<b>🔥 资金流入:</b> {', '.join(flow_items)}<br>"
    if outflows:
        flow_items = [f"{f['name']} {f['change_7d']:.0f}%" for f in outflows[:3]]
        flow_summary += f"<b>❄️ 资金流出:</b> {', '.join(flow_items)}"

    styled_html = f"""
    <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa;">
            <div style="max-width: 720px; margin: 0 auto; padding: 20px; background-color: #fff;">
                <h2 style="color: #1a237e; border-bottom: 3px solid #3f51b5; padding-bottom: 12px; margin-bottom: 15px;">
                    每日早期项目雷达 | {datetime.now().strftime("%Y-%m-%d")}
                </h2>

                <div style="background:#e3f2fd; padding:10px 14px; border-radius:6px; margin-bottom:20px; font-size:0.88em;">
                    {revenue_summary if revenue_summary else ""}
                    {flow_summary if flow_summary else ""}
                    {"数据暂无" if not revenue_summary and not flow_summary else ""}
                </div>

                {html_content}

                <hr style="border: 0; border-top: 1px solid #e0e0e0; margin: 30px 0 15px;">
                <p style="font-size: 11px; color: #9e9e9e; text-align: center;">
                    由 Gemini 2.0 Flash 生成 | 资金数据: DeFiLlama | 种子: {RANDOM_SEED}
                </p>
            </div>
        </body>
    </html>
    """

    msg = MIMEText(styled_html, 'html', 'utf-8')
    msg['Subject'] = f'每日早期项目雷达 - {datetime.now().strftime("%Y-%m-%d")}'
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_USER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASSWORD)
            smtp.send_message(msg)
        print(">>> 研报发送成功")
    except Exception as e:
        print(f">>> 发送失败: {e}")


def main():
    print(">>> 每日早期项目雷达 v5 启动...")

    # 获取收入排行数据
    top_revenue, top_growth = fetch_defillama_revenue()
    if top_revenue:
        print(f">>> 收入榜Top: {top_revenue[0]['name']} ${top_revenue[0]['revenue_24h']:,.0f}")
    if top_growth:
        print(f">>> 增长最快: {top_growth[0]['name']} +{top_growth[0]['change_1d']:.0f}%")

    # 获取资金流向数据
    inflows, outflows = fetch_defillama_flows()
    if inflows:
        print(f">>> 资金流入赛道: {len(inflows)} 个")
    if outflows:
        print(f">>> 资金流出赛道: {len(outflows)} 个")

    # 获取邮件
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        mail.select("inbox")

        since_date = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        print(f">>> 筛选日期: {since_date}")

        status, messages = mail.search(None, f'(UNSEEN SINCE "{since_date}")')

        if not messages or not messages[0]:
            print(">>> 没有新邮件")
            return

        email_ids = messages[0].split()
        email_ids.sort(key=lambda x: int(x))

        process_ids = email_ids[-30:]
        email_count = len(process_ids)
        print(f">>> 发现 {len(email_ids)} 封邮件，处理最近 {email_count} 封")

        all_content = f"【本批次共 {email_count} 封邮件，必须全部处理】\n\n"

        for idx, e_id in enumerate(process_ids, 1):
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject = decode_subject(msg["Subject"])
                    sender = msg.get("From", "(未知发件人)")
                    date = msg.get("Date", "")

                    body = get_email_body(msg)
                    clean_body = body[:5000].replace("\n", " ").strip()
                    body_length = len(body)

                    all_content += f"=== 邮件 #{idx}/{email_count} ===\n"
                    all_content += f"发件人: {sender}\n"
                    all_content += f"时间: {date}\n"
                    all_content += f"标题: {subject}\n"
                    all_content += f"正文长度: {body_length} 字符\n"
                    all_content += f"正文内容:\n{clean_body}\n\n"

        # 调用 AI
        print(">>> 调用 Gemini 2.0 Flash...")

        prompt = build_prompt(email_count, all_content, inflows, outflows)

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                top_p=1.0,
                top_k=1,
                max_output_tokens=8192,
                seed=RANDOM_SEED
            )
        )

        print(">>> 研报生成完毕")
        send_summary_email(response.text, inflows, outflows, top_revenue, top_growth)

        mail.close()
        mail.logout()

    except Exception as e:
        print(f">>> 运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
