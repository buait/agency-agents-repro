#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent_matcher.py —— 智能 Agent 推荐器（复刻版新增工具）

功能说明：
    仓库里躺着几百个专职 AI Agent（按部门目录组织）。本工具读取
    divisions.json 与全部 Agent 定义文件（*.md 的 YAML frontmatter），
    根据你输入的任务描述做关键词打分，推荐最匹配的 3 个 Agent，
    并给出每个 Agent 所在的部门、文件路径与匹配得分。

用法示例：
    python scripts/agent_matcher.py "帮我写一个 React 前端页面"
    python scripts/agent_matcher.py "分析一下市场竞品和定价策略" --top 5
    python scripts/agent_matcher.py "写营销文案" --json

参数说明：
    --top  控制返回的推荐数量，默认 3，最大 10。
    --json 以 JSON 格式输出，方便脚本调用方解析。

本脚本只依赖 Python 标准库，无第三方依赖，可直接运行。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# 非部门目录（与 scripts/check-divisions.sh 的 NON_DIVISION_DIRS 保持一致）
NON_DIVISION_DIRS = {"integrations", "strategy", "examples", "scripts", ".github", "docs", "site"}

# 必需字段，缺失会触发校验告警
REQUIRED_FRONTMATTER = ("name", "description")


def load_divisions(root: Path) -> dict:
    """读取 divisions.json，返回部门名 -> 元信息 的映射。"""
    with open(root / "divisions.json", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("divisions", {})


def parse_frontmatter(text: str) -> dict | None:
    """解析 markdown 文件开头的 YAML frontmatter 块。

    约定：文件以 --- 开头，第二个 --- 之前为 YAML 字段。
    字段按 键: 值 形式逐行解析（值去除首尾空白）。
    """
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end].strip()
    front = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        front[key.strip()] = value.strip()
    return front


def iter_agents(root: Path):
    """遍历仓库内所有 Agent 定义文件，产出 (相对路径, frontmatter) 元组。"""
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root).as_posix()
        first = rel.split("/", 1)[0]
        if first in NON_DIVISION_DIRS or rel.startswith("."):
            continue
        front = parse_frontmatter(md.read_text(encoding="utf-8", errors="ignore"))
        if front:
            yield rel, front


# 常用中文任务词 → 英文关键词映射：仓库 Agent 的描述以英文为主，
# 直接输入中文任务也能命中相关特工。
CN_KEYWORD_MAP = {
    "前端": ["frontend", "react", "vue", "ui", "web"],
    "写": ["write", "create", "build", "code"],
    "营销": ["marketing"],
    "设计": ["design"],
    "测试": ["testing", "test"],
    "安全": ["security", "secure"],
    "财务": ["finance", "financial"],
    "数据": ["data", "analytics"],
    "教育": ["education", "tutor", "teaching"],
    "教学": ["education", "tutor", "teaching"],
    "课程": ["curriculum", "course"],
    "合同": ["legal", "contract"],
    "销售": ["sales"],
    "产品": ["product"],
    "项目": ["project"],
    "游戏": ["game"],
    "研究": ["research"],
    "分析": ["analy", "analysis"],
    "优化": ["optimize", "optimization"],
    "开发": ["develop", "engineering", "code"],
    "页面": ["web", "frontend", "ui"],
}


def tokenize(text: str) -> set[str]:
    """把输入文本切成小写关键词集合；中文任务词按映射表补充英文关键词。"""
    words = set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}", text.lower()))
    for cn_word, en_words in CN_KEYWORD_MAP.items():
        if cn_word in text:
            words.update(en_words)
    return words


def score_agent(query_words: set[str], name: str, description: str) -> float:
    """基于关键词打分：命中 name 权重高，命中 description 权重低。"""
    name_l = name.lower()
    desc_l = description.lower()
    score = 0.0
    for w in query_words:
        if w in name_l:
            score += 3.0
        elif w in desc_l:
            score += 1.0
        elif any(w in seg for seg in re.split(r"[\s,;/]+", name_l)):
            score += 1.5
    # 描述被完整包含时加权，鼓励语义更贴近的 Agent
    for q in query_words:
        if len(q) > 4 and q in desc_l:
            score += 0.5
    return score


def recommend(root: Path, query: str, top: int = 3, as_json: bool = False):
    divisions = load_divisions(root)
    query_words = tokenize(query)
    hits = []

    for rel, front in iter_agents(root):
        name = front.get("name", "")
        desc = front.get("description", "")
        s = score_agent(query_words, name, desc)
        if s > 0:
            division = rel.split("/", 1)[0]
            hits.append(
                {
                    "score": round(s, 2),
                    "division": division,
                    "division_label": divisions.get(division, {}).get("label", division),
                    "agent": name,
                    "file": rel,
                    "description": desc,
                }
            )

    hits.sort(key=lambda x: (-x["score"], x["division"], x["agent"]))
    hits = hits[:top]

    if as_json:
        print(json.dumps({"query": query, "matched": hits}, ensure_ascii=False, indent=2))
        return

    if not hits:
        print(f"没有找到与「{query}」匹配的 Agent，换个更通用的关键词试试。")
        return

    print(f"根据「{query}」为你推荐以下 Agent：\n")
    for i, h in enumerate(hits, 1):
        print(f"{i}. [{h['division_label']}] {h['agent']}  (匹配分 {h['score']})")
        print(f"   文件: {h['file']}")
        print(f"   简介: {h['description']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Agency Agents 智能 Agent 推荐器：输入任务描述，推荐最合适的专职 Agent。"
    )
    parser.add_argument("query", nargs="+", help="任务描述，例如：写一个 React 前端页面")
    parser.add_argument("--top", type=int, default=3, help="推荐数量，默认 3，最大 10")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    top = max(1, min(args.top, 10))
    recommend(root, " ".join(args.query), top=top, as_json=args.json)


if __name__ == "__main__":
    main()
