---
description: Search for new tech weeklies to add to config
allowed-tools: Bash, WebSearch, WebFetch, Read, Write
---

# Search for Tech Weeklies

Find new tech weeklies on GitHub that accept submissions.

## Execution Steps

### Step 1: Search GitHub

Use `gh` to search for weekly repositories with >100 stars:

```bash
# Search for "weekly" repos
gh search repos "weekly" --stars=">100" --limit=50 --json fullName,stargazersCount,description

# Search for "周刊" repos
gh search repos "周刊" --stars=">100" --limit=50 --json fullName,stargazersCount,description
```

### Step 2: Filter Results

Filter to find actual tech weeklies (not just repos with "weekly" in name):
- Must have issue submissions enabled
- Description mentions "周刊", "weekly", or "newsletter"
- Has recent activity

### Step 3: Check Submission Format

For each candidate, use WebFetch to check:
- Does the repo accept submissions via issues?
- What format do they expect?
- Are there any specific requirements?

```bash
gh repo view <repo> --json hasIssuesEnabled,readme
```

### Step 4: Update Config

If new weeklies are found, suggest additions to `weeklies.json`:

```json
{
  "id": "new-weekly-id",
  "name": "周刊名称",
  "repo": "owner/repo",
  "stars": 1000,
  "language": "zh",
  "type": "issue",
  "title_template": "【推荐】{name} - {short_description}",
  "categories": ["tech", "tools"],
  "enabled": true
}
```

### Step 5: Report Findings

Output a table of discovered weeklies:

| Repo | Stars | Description | Accepts Issues | Added |
|------|-------|-------------|----------------|-------|
| owner/repo | 1000 | Description | ✅ | ❌ New |

## Web Search Queries

If GitHub search is insufficient, use WebSearch:

- "GitHub 技术周刊 投稿"
- "开源项目周刊 issue 推荐"
- "tech weekly newsletter github submissions"
