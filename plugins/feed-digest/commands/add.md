---
description: 添加 RSS/Atom 订阅源到配置
argument-hint: <url> [name]
allowed-tools:
  - Read
  - Write
  - Edit
---

将用户提供的 RSS/Atom 源添加到 `~/.claude/feeds.local.md` 配置文件。

## 执行步骤

1. 解析用户输入的 URL 和可选名称
2. 读取 `~/.claude/feeds.local.md`（如不存在则创建）
3. 在 YAML frontmatter 的 feeds 数组中添加新条目
4. 保存文件

## 配置文件格式

```markdown
---
feeds:
  - url: https://example.com/feed.rss
    name: Example Site
  - url: https://another.com/atom.xml
---

# 我的订阅源

这里可以添加备注。
```

## 示例

用户输入: `/feeds:add https://linux.do/latest.rss Linux.do`

添加后:
```yaml
feeds:
  - url: https://linux.do/latest.rss
    name: Linux.do
```

## 注意

- 如果 URL 已存在，提示用户并询问是否更新名称
- 验证 URL 格式（必须是 http/https 开头）
- 如果用户未提供名称，name 字段留空（获取时自动识别）
