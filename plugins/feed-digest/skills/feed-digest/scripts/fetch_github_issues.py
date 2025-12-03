#!/usr/bin/env python3
"""
Fetch GitHub Issues from configured repositories.
Returns structured JSON compatible with feed-digest scoring.

Usage:
    python fetch_github_issues.py --repos "owner/repo1,owner/repo2"
    python fetch_github_issues.py --repos "ruanyf/weekly" --search "Claude"
    python fetch_github_issues.py --repos "ruanyf/weekly" --days 7

Environment:
    GITHUB_TOKEN: Optional. Increases rate limit from 60 to 5000 req/hour.
"""

import sys
import os
import json
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
from html import unescape
import re


def strip_html(text):
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return unescape(text).strip()


def truncate(text, max_len=800):
    """Truncate text to max length."""
    if not text:
        return ""
    text = strip_html(text)
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def github_api(endpoint, token=None):
    """Call GitHub API using curl."""
    url = f"https://api.github.com{endpoint}"
    cmd = [
        'curl', '-sS', '-L',
        '--connect-timeout', '15',
        '--max-time', '30',
        '-H', 'Accept: application/vnd.github.v3+json',
        '-H', 'User-Agent: feed-digest-bot'
    ]
    if token:
        cmd.extend(['-H', f'Authorization: token {token}'])
    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")

    return json.loads(result.stdout)


def search_issues(repo, query, token=None):
    """Search issues in a repo."""
    # GitHub search API
    search_query = f"{query} repo:{repo} is:issue"
    endpoint = f"/search/issues?q={search_query.replace(' ', '+')}&sort=created&order=desc&per_page=50"

    try:
        data = github_api(endpoint, token)
        return data.get('items', [])
    except Exception as e:
        print(f"Search error for {repo}: {e}", file=sys.stderr)
        return []


def list_issues(repo, days=7, token=None):
    """List recent issues from a repo."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    endpoint = f"/repos/{repo}/issues?state=open&sort=created&direction=desc&per_page=100&since={since}"

    try:
        data = github_api(endpoint, token)
        # Filter out pull requests (they also appear in issues endpoint)
        return [issue for issue in data if 'pull_request' not in issue]
    except Exception as e:
        print(f"List error for {repo}: {e}", file=sys.stderr)
        return []


def issue_to_post(issue, repo_name):
    """Convert GitHub issue to standard post format."""
    # Extract reactions count for scoring bonus
    reactions = issue.get('reactions', {})
    reaction_count = sum([
        reactions.get('+1', 0),
        reactions.get('heart', 0),
        reactions.get('hooray', 0),
        reactions.get('rocket', 0),
    ])

    labels = [label.get('name', '') for label in issue.get('labels', [])]

    return {
        'title': issue.get('title', ''),
        'link': issue.get('html_url', ''),
        'description': truncate(issue.get('body', '')),
        'pub_date': issue.get('created_at', ''),
        'categories': labels,
        'creator': issue.get('user', {}).get('login', ''),
        'source': repo_name,
        'source_url': f"https://github.com/{repo_name}",
        # GitHub-specific fields for scoring
        'reactions': reaction_count,
        'comments': issue.get('comments', 0),
        'issue_number': issue.get('number', 0),
    }


def fetch_all_repos(repos, search_query=None, days=7, token=None):
    """Fetch issues from all configured repos."""
    all_posts = []
    results = []

    for repo_config in repos:
        if isinstance(repo_config, str):
            repo = repo_config
            name = repo_config
        else:
            repo = repo_config.get('repo', '')
            name = repo_config.get('name', repo)

        if not repo:
            continue

        try:
            if search_query:
                issues = search_issues(repo, search_query, token)
            else:
                issues = list_issues(repo, days, token)

            posts = [issue_to_post(issue, name) for issue in issues]
            all_posts.extend(posts)

            results.append({
                'repo': repo,
                'name': name,
                'success': True,
                'issue_count': len(issues),
            })
        except Exception as e:
            results.append({
                'repo': repo,
                'name': name,
                'success': False,
                'error': str(e),
            })

    # Sort by date (newest first), then by reactions
    all_posts.sort(key=lambda x: (x.get('pub_date', ''), x.get('reactions', 0)), reverse=True)

    return {
        'fetched_at': datetime.now(timezone.utc).isoformat(),
        'mode': 'search' if search_query else 'digest',
        'search_query': search_query,
        'days': days if not search_query else None,
        'repo_results': results,
        'total_posts': len(all_posts),
        'posts': all_posts,
    }


def main():
    parser = argparse.ArgumentParser(description='Fetch GitHub Issues')
    parser.add_argument('--repos', required=True, help='Comma-separated repos (owner/repo)')
    parser.add_argument('--search', help='Search query (optional)')
    parser.add_argument('--days', type=int, default=7, help='Days to look back (default: 7)')
    parser.add_argument('--token', help='GitHub token (or use GITHUB_TOKEN env)')
    args = parser.parse_args()

    # Parse repos
    repos = [r.strip() for r in args.repos.split(',') if r.strip()]

    # Get token
    token = args.token or os.environ.get('GITHUB_TOKEN')

    if not repos:
        print(json.dumps({'error': 'No repos provided'}), file=sys.stderr)
        sys.exit(1)

    result = fetch_all_repos(repos, args.search, args.days, token)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
