---
description: Promote an open source project to tech weeklies
allowed-tools: Bash, Read, WebSearch, WebFetch, TodoWrite
---

# Promote OSS Project

Batch submit an open source project to multiple tech weeklies.

## Input

User provides a GitHub repo URL, e.g.:
- `https://github.com/ourines/worktree-task-plugin`
- `ourines/worktree-task-plugin`

## Execution Steps

### Step 1: Extract Repo Info

```bash
gh repo view <owner/repo> --json name,description,url,stargazerCount,homepageUrl,repositoryTopics
```

Also fetch README for feature extraction:
```bash
gh repo view <owner/repo> --json readme
```

### Step 2: Load Weeklies Config

Read the config file:
```bash
cat ${CLAUDE_PLUGIN_ROOT}/config/weeklies.json
```

### Step 3: Generate & Submit

For each enabled weekly:

1. Generate title from `title_template`:
   - `{name}` → repo name
   - `{short_description}` → first sentence of description

2. Generate body (Chinese template):
```markdown
## 项目介绍

[{name}]({url}) - {description}

## 核心功能

- Feature 1 (from README)
- Feature 2
- Feature 3

## 使用示例

\`\`\`bash
# Example from README
\`\`\`

## 链接

- GitHub: {url}
```

3. Submit based on type:

For `type: "issue"`:
```bash
gh issue create --repo <weekly_repo> \
  --title "<title>" \
  --body "<body>"
```

For `type: "comment"`:
```bash
gh issue comment <issue_number> --repo <weekly_repo> \
  --body "<body>"
```

### Step 4: Report Results

Create a summary table:

| Weekly | Status | Link |
|--------|--------|------|
| 科技爱好者周刊 | ✅ Created | https://github.com/... |
| 前端精读周刊 | ✅ Commented | https://github.com/... |
| ... | ... | ... |

## Options

- `--dry-run`: Show what would be submitted without actually creating issues
- `--filter <category>`: Only submit to weeklies matching the category
- `--skip <id>`: Skip specific weeklies by ID

## Error Handling

- If `gh` command fails, log the error and continue with next weekly
- If rate limited, wait and retry
- Track all results in TodoWrite for visibility
