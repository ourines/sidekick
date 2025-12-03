---
description: GitHub Issues 搜索与摘要
allowed-tools:
  - Bash
  - Read
  - Write
---

# GitHub Issues 搜索与摘要

从配置的 GitHub 仓库获取 Issues，支持搜索和每周摘要两种模式。

## 执行步骤

### 1. 读取配置

```bash
cat ~/.claude/feeds.local.md
```

从 YAML frontmatter 中提取 `github_issues` 配置：

```yaml
github_issues:
  - repo: ruanyf/weekly
    name: 阮一峰周刊投稿
```

如果没有配置，提示用户添加。

### 2. 解析参数

用户输入：`$ARGUMENTS`

- **有关键词** → 搜索模式
- **无关键词** → 摘要模式（本周精选）

### 3. 获取 Issues

```bash
# 搜索模式
python3 ${CLAUDE_PLUGIN_ROOT}/skills/feed-digest/scripts/fetch_github_issues.py \
  --repos "ruanyf/weekly" \
  --search "关键词"

# 摘要模式（默认 7 天）
python3 ${CLAUDE_PLUGIN_ROOT}/skills/feed-digest/scripts/fetch_github_issues.py \
  --repos "ruanyf/weekly" \
  --days 7
```

### 4. AI 评分与输出

按 [评分标准](../skills/feed-digest/references/scoring.md) 对每个 Issue 打分。

**GitHub Issues 评分加权：**
- reactions (👍❤️🎉🚀) 多 → 内容价值 +1~2 分
- comments 多 → 讨论热度高 → 时效性 +1 分

**输出格式：**

```markdown
# GitHub Issues 摘要 (YYYY-MM-DD)

**模式**: 搜索 "关键词" / 每周精选
**来源**: ruanyf/weekly 等 N 个仓库
**共获取**: X 条，精选 Y 条

---

## 精选推荐 (≥7分)

### [Issue 标题](链接) - 8.5分
**来源**: ruanyf/weekly #123 | **作者**: @username
**标签**: `tool` `AI`
👍 15 | 💬 3

> Issue 内容摘要（2-3句话）

---

## 值得一看 (4-6分)

- [标题](链接) - 5.8分 (ruanyf/weekly #456)
- [标题](链接) - 4.5分 (ruanyf/weekly #789)

---

## 统计

| 仓库 | 状态 | Issues 数 |
|------|------|-----------|
| ruanyf/weekly | ✓ | 45 |
```

## 配置示例

在 `~/.claude/feeds.local.md` 添加：

```yaml
---
feeds:
  - url: https://linux.do/latest.rss
github_issues:
  - repo: ruanyf/weekly
    name: 阮一峰周刊投稿
  - repo: anthropics/claude-code
    name: Claude Code
---
```

## 注意事项

1. **API 限制**: 无 token 60次/小时，有 `GITHUB_TOKEN` 环境变量则 5000次/小时
2. **搜索范围**: 仅搜索 open issues
3. **时间范围**: 摘要模式默认取最近 7 天

ARGUMENTS: $ARGUMENTS
