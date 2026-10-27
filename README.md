# 🎭 The Agency：一个装满专职 AI 特工的仓库（中文版）

> 一句话介绍：这个仓库收集了几百个「专职 AI 特工」——每一个都像一位经验丰富的专家，
> 有自己的人格、工作方法和交付标准。你可以在 Claude Code、Cursor、Codex 等工具里直接启用它们。

本仓库是 [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) 的
**独立复刻版本**，在原仓库基础上做了工具链增强与新部门扩展，具体改动见
[REPRODUCTION-NOTES.md](REPRODUCTION-NOTES.md)。

---

## 这是什么？

想象你有一个「AI 梦之队」：前端开发、营销文案、财务分析、安全审计……每位成员都
是某个领域的专家，随时待命。这个仓库就是这支队伍的档案库——每个 AI 特工就是
一个 Markdown 文件，里面写清楚了它的身份、性格、核心工作方法、交付物和衡量指标。

原仓库英文介绍见 [README.en.md](README.en.md)（内容一字未改，方便对照）。

## 仓库结构

```
academic/  academic-*       学术研究类特工
design/    design-*         设计类特工
education/ education-*      教育类特工（本次复刻新增）
engineering/ engineering-*  工程开发类特工
finance/   finance-*        财务金融类特工
...（共 19 个部门，每个部门一个目录）
divisions.json               部门总表（名称、图标、颜色）
scripts/                     安装与校验脚本
tools.json                   工具清单
```

## 快速上手

### 方式一：在 Claude Code 里使用

```bash
# 安装某个部门的所有特工到你的 Claude Code
./scripts/install.sh --tool claude-code

# 或者只复制你需要的部门
cp engineering/*.md ~/.claude/agents/
```

### 方式二：用新增的推荐器，让工具帮你挑特工

仓库里有几百个特工，不知道用哪个？运行下面的命令，输入你的任务描述，
推荐器会按匹配度推荐最合适的 3 个：

```bash
python scripts/agent_matcher.py "帮我写一个 React 前端页面"
python scripts/agent_matcher.py "分析市场竞品和定价策略" --top 5
```

### 方式三：当参考模板用

每个特工文件都包含：身份与性格、核心使命与工作流、技术交付示例、
成功指标与沟通风格。直接阅读、复制、改造成你自己的专属特工即可。

## 本次复刻的优化内容

| 方向 | 说明 |
| ---- | ---- |
| 智能推荐器 | 新增 `scripts/agent_matcher.py`，根据任务描述自动推荐最匹配的特工 |
| 本地校验器 | 新增 `scripts/validate_agents.py`，无需 bash 即可校验仓库一致性（原校验脚本依赖 Shell 环境） |
| 新部门 | 新增 `education/` 教育部门（3 个特工：Tutor / 课程设计 / 教育科技），同步更新 `divisions.json` |
| 中文文档 | README 改为中文，新增 `REPRODUCTION-NOTES.md` 复现说明 |

## 许可

本项目遵循 MIT 许可证，完整文本见 [LICENSE](LICENSE)。

> 注意：本仓库为独立复刻，与原仓库无 git 历史关联；仅供学习与二次开发参考。
