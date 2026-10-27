#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_agents.py —— 本地一致性校验器（复刻版新增工具）

功能说明：
    仓库维护了大量 Agent 定义文件与 JSON 配置。原仓库的校验逻辑依赖
    Shell 脚本（scripts/check-divisions.sh 等），需要 bash 环境。
    本工具用纯 Python 在本地完成同类检查，Windows / macOS / Linux 通用：

      1. divisions.json 中声明的部门目录必须真实存在，且每个部门至少
         包含 1 个带 frontmatter 的 Agent 文件；
      2. 每个 Agent 文件必须包含 name 与 description 两个必需字段；
      3. 关键文件（LICENSE / README.md / tools.json / CONTRIBUTING.md）
         必须存在；
      4. 统计全仓库 Agent 总数与各部门分布，输出汇总报告。

用法：
    python scripts/validate_agents.py            # 完整校验并输出报告
    python scripts/validate_agents.py --quiet    # 只输出问题与结论

退出码：0 表示全部通过；1 表示存在需修复的问题（可用于 CI）。
"""

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FRONTMATTER = ("name", "description")
REQUIRED_FILES = ("LICENSE", "README.md", "tools.json", "CONTRIBUTING.md")
NON_DIVISION_DIRS = {"integrations", "strategy", "examples", "scripts", ".github", "docs", "site"}


def load_divisions(root: Path) -> dict:
    with open(root / "divisions.json", encoding="utf-8") as fh:
        return json.load(fh).get("divisions", {})


def parse_frontmatter(text: str) -> dict | None:
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


def collect_agents(root: Path) -> dict[str, list[tuple[str, dict]]]:
    """返回 division -> [(相对路径, frontmatter)] 的映射。"""
    agents: dict[str, list[tuple[str, dict]]] = {}
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root).as_posix()
        first = rel.split("/", 1)[0]
        if first in NON_DIVISION_DIRS or rel.startswith("."):
            continue
        front = parse_frontmatter(md.read_text(encoding="utf-8", errors="ignore"))
        if front:
            agents.setdefault(first, []).append((rel, front))
    return agents


def main():
    parser = argparse.ArgumentParser(description="Agency Agents 本地一致性校验器")
    parser.add_argument("--quiet", action="store_true", help="只输出问题与最终结论")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    problems: list[str] = []
    divisions = load_divisions(root)
    agents = collect_agents(root)

    # 1) divisions.json 与磁盘目录一致性
    for div in divisions:
        if not (root / div).is_dir():
            problems.append(f"divisions.json 声明了部门「{div}」，但磁盘上不存在该目录")
        elif div not in agents:
            problems.append(f"部门「{div}」目录存在，但没有任何带 frontmatter 的 Agent 文件")

    for div in agents:
        if div not in divisions:
            problems.append(f"磁盘存在部门目录「{div}」，但 divisions.json 未声明")

    # 2) Agent 文件必需字段
    missing_field = 0
    for div, items in agents.items():
        for rel, front in items:
            for field in REQUIRED_FRONTMATTER:
                if not front.get(field):
                    missing_field += 1
                    problems.append(f"{rel} 缺少必需字段: {field}")

    # 3) 关键文件存在性
    for fname in REQUIRED_FILES:
        if not (root / fname).exists():
            problems.append(f"缺少关键文件: {fname}")

    total = sum(len(v) for v in agents.values())

    if not args.quiet:
        print("=== Agency Agents 本地校验报告 ===\n")
        print(f"部门数量   : {len(divisions)}")
        print(f"Agent 总数 : {total}\n")
        print("各部门 Agent 分布:")
        for div in sorted(divisions):
            count = len(agents.get(div, []))
            label = divisions[div].get("label", div)
            print(f"  - {label:<22} {count} 个")
        print()

    if problems:
        print(f"发现 {len(problems)} 个问题：")
        for p in problems:
            print(f"  [!] {p}")
        print("\n结论：校验未通过，请修复上述问题。")
        sys.exit(1)

    print("结论：校验全部通过 ✅（各部门配置一致，Agent 文件格式合规）")
    sys.exit(0)


if __name__ == "__main__":
    main()
