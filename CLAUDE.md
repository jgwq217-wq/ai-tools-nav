# CLAUDE.md — AI 工具导航站

## 项目定位
一个纯静态的 AI 工具导航网站，收录 100+ 实用 AI 工具，支持分类筛选、场景标签、优劣对比。
部署在 GitHub Pages，零成本运行。

## 技术栈
- **纯 HTML/CSS/JS** — 无框架，无构建工具，单文件 `index.html`
- **数据存储**：所有工具数据内嵌在 `<script>` 中的 `tools` 数组
- **持久化**：localStorage（收藏、提交记录、点击统计、更新日志）
- **部署**：GitHub Pages，仓库 `jgwq217-wq/ai-tools-nav`

## 文件结构
```
/
├── index.html          ← 唯一文件，包含 HTML + CSS + JS + 110 条工具数据
├── sitemap.xml         ← SEO
├── robots.txt          ← SEO
├── scripts/
│   └── discover.py     ← 每周自动发现新工具（GitHub Actions）
└── .github/workflows/
    └── auto-discover.yml
```

## 架构约束（不要改）
1. **单文件架构** — 所有内容在 `index.html` 中，不拆 CSS/JS 文件
2. **零依赖** — 不引入 npm、CDN 外部库
3. **中文优先** — 面向中文用户，描述、标签、UI 均为中文
4. **工具数据内嵌** — 不要将 tools 抽到 JSON 文件再 fetch（会引入加载失败风险）
5. **所有修改必须同时更新 vault 副本和仓库** — `~/Desktop/工作/ai-tools-nav/` 和 `02-项目/AI工具导航站/`

## 工具数据格式
```js
t('工具名','一句话描述','分类','价格标签',['场景标签数组'],'官网URL',新增标记,[优势数组],[短板数组],评分)
```

- 分类：大模型 / 对话AI / 编程 / 设计 / 写作 / 效率 / 视频 / 其他
- 场景标签：免费、免注册、需注册、无限额、适合新手、企业级、国产、海外、本地
- 价格标签：免费 / 免费+付费 / 付费
- 评分：1-5，一位小数

## 使用 Claude Code 时
- 仓库路径：`~/Desktop/工作/ai-tools-nav/`
- Vault 副本：`~/Desktop/自生长专属知识库/02-项目/AI工具导航站/index.html`
- 修改流程：改 vault 副本 → 复制到仓库 → `git commit` → `git push`
- 推送用 SSH：`git@github.com-ai-tools:jgwq217-wq/ai-tools-nav.git`
- SSH Key：`~/.ssh/github_ai_tools`
