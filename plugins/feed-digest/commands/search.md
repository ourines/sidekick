---
description: 深度搜索 - 跨多源智能搜索并总结
allowed-tools:
  - Bash
  - Read
  - Write
  - mcp__web-search-prime__webSearchPrime
  - mcp__exa__web_search_exa
---

# Deep Search - 智能多源搜索

根据用户问题，执行多源搜索并 **必须输出整理后的结果回答用户**。

## 执行步骤

### 1. 解析用户问题

从 ARGUMENTS 获取搜索问题：`$ARGUMENTS`

### 2. 执行搜索（三选一，按优先级）

**优先方案：使用 Python 脚本**

```bash
# 1. 读取配置
cat ~/.claude/feeds.local.md

# 2. 准备配置（从上面提取 API keys 和 sites）
cat > /tmp/search_config.json << 'EOF'
{
  "search": {
    "tavily": {"api_key": "从配置提取"},
    "exa": {"api_key": "从配置提取"}
  },
  "sites": [
    {"url": "https://linux.do", "type": "discourse", "name": "Linux.do"}
  ]
}
EOF

# 3. 执行搜索
python3 ${CLAUDE_PLUGIN_ROOT}/skills/feed-digest/scripts/deep_search.py \
  --config /tmp/search_config.json \
  --query "用户的问题"
```

**备选方案：如果脚本失败，使用 MCP 工具**

并行调用：
- `mcp__web-search-prime__webSearchPrime` - 中文搜索
- `mcp__exa__web_search_exa` - 英文搜索
- 直接 curl Linux.do API: `curl "https://linux.do/search.json?q=关键词"`

### 3. 必须输出结果（强制）

**无论使用哪种搜索方式，都必须按以下格式输出结果：**

```markdown
# 搜索结果：[问题摘要]

## 核心发现

> Claude 基于搜索结果对用户问题的直接回答（3-5 句话）

## 相关讨论

### [标题](链接)
**来源**: xxx | **时间**: xxx

> 内容摘要（2-3 句话）

---

（重复 3-5 个最相关的结果）

## 信息来源

| 来源 | 状态 | 结果数 |
|------|------|--------|
| Linux.do | ✓/✗ | N |
| Tavily | ✓/✗ | N |
| Exa | ✓/✗ | N |
```

## 重要

1. **必须回答用户** - 搜索只是手段，目的是回答用户问题
2. **优先中文社区** - Linux.do 结果通常比 Tavily/Exa 更相关
3. **去重合并** - 多个来源的相同链接只保留一个
4. **按相关性排序** - 最相关的放前面

ARGUMENTS: $ARGUMENTS
