---
description: 列出已配置的订阅源
allowed-tools:
  - Read
---

显示用户在 `~/.claude/feeds.local.md` 中配置的所有订阅源。

## 执行步骤

1. 读取 `~/.claude/feeds.local.md`
2. 解析 YAML frontmatter 中的 feeds 数组
3. 格式化输出

## 输出格式

```
已配置 N 个订阅源:

1. Linux.do
   https://linux.do/latest.rss

2. Hacker News
   https://news.ycombinator.com/rss

3. (未命名)
   https://lobste.rs/rss
```

## 注意

- 如果配置文件不存在，提示用户使用 `/feeds:add` 添加源
- 如果 feeds 数组为空，同样提示
