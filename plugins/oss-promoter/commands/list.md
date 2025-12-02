---
description: List all configured weeklies
allowed-tools: Bash, Read
---

# List Configured Weeklies

Show all weeklies in the config with their status.

## Execution

Read and display the weeklies config:

```bash
cat ${CLAUDE_PLUGIN_ROOT}/config/weeklies.json
```

## Output Format

Display as a formatted table:

| ID | Name | Repo | Stars | Type | Enabled |
|----|------|------|-------|------|---------|
| ruanyf-weekly | 科技爱好者周刊 | ruanyf/weekly | 79.7k | issue | ✅ |
| ascoders-weekly | 前端精读周刊 | ascoders/weekly | 30.6k | comment | ✅ |
| ... | ... | ... | ... | ... | ... |

## Summary Stats

- Total configured: X
- Enabled: Y
- Disabled: Z
- By language: zh: A, en: B
- By category: tech: C, frontend: D, ...
