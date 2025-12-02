---
description: 获取订阅源摘要，支持关键词过滤
argument-hint: "[--filter keyword1,keyword2]"
allowed-tools:
  - Read
  - Bash
  - Skill
---

从配置的订阅源获取内容，智能分类、评分筛选，生成摘要。

## 执行步骤

### 1. 读取配置

读取 `~/.claude/feeds.local.md`，提取 feeds 数组。

### 2. 准备临时配置

将 feeds 写入临时 JSON 文件供脚本使用：

```bash
echo '{"feeds": [...]}' > /tmp/feeds_config.json
```

### 3. 获取内容

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/feed-digest/scripts/fetch_feeds.py /tmp/feeds_config.json
```

如果用户指定了 `--filter`：

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/feed-digest/scripts/fetch_feeds.py /tmp/feeds_config.json --filter "keyword1,keyword2"
```

### 4. 分类与评分

加载 feed-digest skill，对返回的帖子：

1. **评分** (10分制，参考 references/scoring.md)
   - 内容价值 40%
   - 时效性 30%
   - 相关性 20%
   - 可读性 10%

2. **分类** (Claude 根据内容自动判断)
   - 技术开发、AI/ML、科技资讯、数码硬件、职场生活等
   - 不限于固定类别

3. **筛选**
   - ≥7分: 精选推荐
   - 4-6分: 值得一看
   - <4分: 忽略

### 5. 输出摘要

按类别组织输出，格式：

```markdown
# Feed 摘要 (2024-12-02 23:30)

共获取 45 篇内容，来自 3 个源，精选 12 篇

---

## 技术开发

### [标题](链接) - 8.5分
**来源**: Linux.do | **作者**: xxx

> 摘要内容...

---

## AI/ML

...

---

## 值得一看

- [标题](链接) - 5.8分 (HN)
- [标题](链接) - 4.2分 (Linux.do)

---

## 统计
- 成功获取: 3/3 源
- 热门来源: Linux.do (20篇)
- 高频词: AI, Claude, VPS
```

## 参数说明

- `--filter`: 逗号分隔的关键词，只显示标题或描述中包含这些词的内容

## 示例

```
/feeds:digest
/feeds:digest --filter AI,Claude
/feeds:digest --filter VPS,服务器
```
