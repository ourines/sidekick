# OSS Promoter

> Claude Code plugin for batch promoting open source projects to tech weeklies and communities.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Plugin-blue)](https://claude.ai)

## Features

- **Batch Submit**: Submit your project to multiple tech weeklies with one command
- **Smart Templates**: Auto-generate tailored content for each weekly's format
- **Weekly Discovery**: Search for new weeklies to add to your promotion list
- **Progress Tracking**: Track submission status with TodoWrite

## Installation

```bash
/plugin install oss-promoter@oss-promoter
```

Or install from GitHub:

```bash
/plugin install https://github.com/ourines/oss-promoter
```

## Usage

### Promote a Project

```bash
/oss-promoter:promote https://github.com/yourname/your-project
```

This will:

1. Extract project info from GitHub
2. Generate submission content
3. Create issues/comments on all enabled weeklies
4. Report results

### Search for Weeklies

```bash
/oss-promoter:search
```

Find new tech weeklies with >100 stars that accept submissions.

### List Configured Weeklies

```bash
/oss-promoter:list
```

Show all weeklies in the config with their status.

## Configuration

Edit `config/weeklies.json` to:

- Enable/disable specific weeklies
- Add new weeklies
- Customize title templates

### Weekly Config Format

```json
{
  "id": "weekly-id",
  "name": "Weekly Name",
  "repo": "owner/repo",
  "stars": 1000,
  "language": "zh",
  "type": "issue",
  "title_template": "{name} - {short_description}",
  "categories": ["tech", "tools"],
  "enabled": true
}
```

## Supported Weeklies

| Weekly | Stars | Language | Status |
|--------|-------|----------|--------|
| 科技爱好者周刊 | 79.7k | 中文 | Enabled |
| HelloGitHub 月刊 | 95k | 中文 | Enabled |
| 前端精读周刊 | 30.6k | 中文 | Enabled |
| 独立开发变现周刊 | 3.6k | 中文 | Enabled |
| DevWeekly | 1.9k | 中文 | Enabled |
| Github精选周刊 | 1.4k | 中文 | Enabled |
| 老胡的信息技术周刊 | 977 | 中文 | Enabled |
| 二丫讲梵学习周刊 | 500 | 中文 | Enabled |

> Run `/oss-promoter:list` to see the full list with current status.

## Requirements

- `gh` (GitHub CLI) - authenticated
- Claude Code with WebSearch enabled

## Author

**ourines** - [GitHub](https://github.com/ourines)

## License

[MIT](LICENSE)
