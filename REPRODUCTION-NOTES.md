# REPRODUCTION-NOTES（复现说明）

本文件记录该仓库的复现信息与后续维护记录。

## 原仓库链接

- 仓库：https://github.com/msitarzewski/agency-agents
- 分支：main（浅克隆 `--depth 1`）

## 复现日期

2026-10-27（北京时间）

## 复现方式说明

1. 通过 GitHub Trending 榜单（github.com/trending 及多源榜单交叉核对）选定本项目：
   当日新增 star 约 6,205，属于「Agent 实际运用」方向的代表性项目，仓库体积约 5MB，
   符合体量适中、结构清晰的选择标准。
2. 使用 `git clone --depth 1` 获取最新快照。
3. 断血缘处理：将源码复制到新目录（跳过 `.git` 目录），重新 `git init`，
   与原始仓库的 git 历史完全脱离，实现独立复刻。
4. 在复刻副本上完成优化，保留原 LICENSE 文件，提交并推送至公开仓库。

## 优化内容

1. **新增 `scripts/agent_matcher.py`（智能 Agent 推荐器）**
   - 读取 `divisions.json` 与全部特工文件的 YAML frontmatter；
   - 根据用户输入的任务描述做关键词打分，推荐最匹配的特工（默认 Top 3，可调）；
   - 支持 `--json` 输出，便于脚本集成；纯标准库实现，零第三方依赖。

2. **新增 `scripts/validate_agents.py`（本地一致性校验器）**
   - 校验 `divisions.json` 声明的部门与磁盘目录是否一致；
   - 校验每个特工文件是否包含 `name` / `description` 必需字段；
   - 校验 LICENSE、README.md、tools.json 等关键文件是否存在；
   - 输出各部门特工数量分布报告；Windows / macOS / Linux 通用，可接入 CI。

3. **新增 `education/` 教育部门（3 个特工）**
   - `education-tutor.md`：个性化辅导特工（自适应学习路径、概念讲解、进度跟踪）；
   - `education-curriculum-designer.md`：课程设计特工（成果导向、评估蓝图、评分量规）；
   - `education-educational-technologist.md`：教育科技特工（选型评估、流程自动化、无障碍设计）；
   - 同步在 `divisions.json` 中登记该部门（图标 BookOpen，品牌色 #10B981）。

4. **中文文档化**
   - 新增中文 `README.md`，原英文 README 保留为 `README.en.md`；
   - 新增本文件 `REPRODUCTION-NOTES.md`。

## 维护记录表

| 日期 | 版本 | 操作人 | 变更摘要 |
| ---- | ---- | ------ | -------- |
| 2026-10-27 | v1.0 | buait | 首次复刻；新增推荐器、校验器、教育部门与中文文档 |

## 与上游仓库的差异说明

1. **未包含 GitHub Actions workflow 文件**：上游仓库含 6 个
   `.github/workflows/*.yml`（CI 校验类）。由于当前推送凭证（buait 的 OAuth token /
   deploy key）不具备 `workflow` scope，GitHub 会拒绝任何包含 workflow 文件的推送
   （REST 上传该类路径同样返回 404）。如需 CI 校验，可从上游仓库手动拷贝
   `.github/workflows/` 目录后推送（需 `workflow` scope 的凭证）。
2. 其余源码、文档、LICENSE 与上游保持一致的对应关系，详见上方优化内容。
