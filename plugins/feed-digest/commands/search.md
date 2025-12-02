---
description: 深度搜索 - 跨多源智能搜索并总结
allowed-tools:
  - Bash
  - Read
  - Write
---

# Deep Search - 智能多源搜索

根据用户问题，使用 Tavily/Exa 全网搜索 + 站点原生搜索，汇总分析结果。

## 执行步骤

### 1. 解析用户问题

从 ARGUMENTS 获取用户的搜索问题。Claude 需要：
1. 理解用户意图
2. 可选：提取/扩展关键词（如果问题复杂）

### 2. 读取配置

```bash
cat ~/.claude/feeds.local.md
```

从 YAML frontmatter 提取：
- `search.tavily.api_key`
- `search.exa.api_key`
- `sites[]` 配置的站点

### 3. 准备搜索配置

将配置写入临时 JSON：

```bash
cat > /tmp/search_config.json << 'EOF'
{
  "search": {
    "tavily": {"api_key": "your-key"},
    "exa": {"api_key": "your-key"}
  },
  "sites": [
    {"url": "https://linux.do", "type": "discourse", "name": "Linux.do"}
  ]
}
EOF
```

### 4. 执行搜索

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/feed-digest/scripts/deep_search.py \
  --config /tmp/search_config.json \
  --query "用户的问题"
```

### 5. 分析结果

Claude 分析搜索结果，输出格式：

```markdown
# 搜索结果：[问题摘要]

## 核心发现

> Claude 对问题的直接回答（基于搜索结果）

## 相关讨论

### [标题](链接)
**来源**: xxx | **热度**: xxx

> 内容摘要...

---

## 信息来源

| 来源 | 状态 | 结果数 |
|------|------|--------|
| Tavily | ✓ | 10 |
| Linux.do | ✓ | 5 |
| ... | ... | ... |
```

## 示例

```
/feed-digest:search cursor 和 windsurf 哪个更好
/feed-digest:search 最近有什么好用的 AI 编程工具
/feed-digest:search Claude Code 怎么配置 MCP
```

## 注意

- 如果没有配置 API Key，只使用站点原生搜索
- Claude 应该综合多个来源的信息给出答案
- 对于技术问题，优先引用官方文档或高质量讨论

ARGUMENTS: $ARGUMENTS
