#!/usr/bin/env python3
"""
Deep search across multiple sources using Tavily/Exa APIs and site-specific adapters.

Usage:
    python deep_search.py --config <config.json> --query "your question"
    python deep_search.py --tavily-key <key> --query "your question"
    python deep_search.py --exa-key <key> --query "your question"

Output: JSON with search results from all sources, ready for Claude to analyze.
"""

import sys
import json
import argparse
import subprocess
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode, quote_plus
import re


def fetch_with_curl(url, headers=None, method='GET', data=None):
    """Fetch URL using curl (works with TUN/system proxy)."""
    cmd = ['curl', '-sS', '-L', '--connect-timeout', '15', '--max-time', '30']

    if headers:
        for k, v in headers.items():
            cmd.extend(['-H', f'{k}: {v}'])

    if method == 'POST':
        cmd.extend(['-X', 'POST'])
        if data:
            cmd.extend(['-d', json.dumps(data)])
            cmd.extend(['-H', 'Content-Type: application/json'])

    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")
    return result.stdout


# =============================================================================
# Search Engine Adapters
# =============================================================================

def search_tavily(query, api_key, max_results=10):
    """
    Search using Tavily API.
    https://docs.tavily.com/
    """
    try:
        url = "https://api.tavily.com/search"
        data = {
            "api_key": api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": False,
            "max_results": max_results,
        }

        response = fetch_with_curl(url, method='POST', data=data)
        result = json.loads(response)

        results = []
        for item in result.get('results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'content': item.get('content', '')[:500],
                'score': item.get('score', 0),
                'source': 'tavily',
                'published_date': item.get('published_date', ''),
            })

        return {
            'engine': 'tavily',
            'success': True,
            'answer': result.get('answer', ''),
            'results': results,
            'result_count': len(results),
        }
    except Exception as e:
        return {
            'engine': 'tavily',
            'success': False,
            'error': str(e),
            'results': [],
        }


def search_exa(query, api_key, max_results=10):
    """
    Search using Exa API.
    https://docs.exa.ai/
    """
    try:
        url = "https://api.exa.ai/search"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }
        data = {
            "query": query,
            "type": "neural",
            "useAutoprompt": True,
            "numResults": max_results,
            "contents": {
                "text": {"maxCharacters": 500}
            }
        }

        response = fetch_with_curl(url, headers=headers, method='POST', data=data)
        result = json.loads(response)

        results = []
        for item in result.get('results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'content': item.get('text', '')[:500],
                'score': item.get('score', 0),
                'source': 'exa',
                'published_date': item.get('publishedDate', ''),
            })

        return {
            'engine': 'exa',
            'success': True,
            'results': results,
            'result_count': len(results),
        }
    except Exception as e:
        return {
            'engine': 'exa',
            'success': False,
            'error': str(e),
            'results': [],
        }


# =============================================================================
# Site-Specific Adapters
# =============================================================================

def search_discourse(base_url, query, name=None, max_results=20):
    """
    Search Discourse forum using API.
    Works with linux.do, meta.discourse.org, etc.
    """
    try:
        search_url = f"{base_url.rstrip('/')}/search.json?{urlencode({'q': query})}"
        response = fetch_with_curl(search_url)
        data = json.loads(response)

        results = []
        topics = data.get('topics', [])
        posts = data.get('posts', [])

        # Build topic lookup
        topic_map = {t['id']: t for t in topics}

        for post in posts[:max_results]:
            topic_id = post.get('topic_id')
            topic = topic_map.get(topic_id, {})

            results.append({
                'title': topic.get('title', post.get('name', '')),
                'url': f"{base_url.rstrip('/')}/t/{topic.get('slug', 'topic')}/{topic_id}",
                'content': post.get('blurb', '')[:500],
                'score': post.get('score', 0),
                'source': name or base_url,
                'source_type': 'discourse',
                'author': post.get('username', ''),
                'published_date': topic.get('created_at', ''),
                'reply_count': topic.get('reply_count', 0),
                'like_count': topic.get('like_count', 0),
            })

        return {
            'site': base_url,
            'site_type': 'discourse',
            'success': True,
            'results': results,
            'result_count': len(results),
        }
    except Exception as e:
        return {
            'site': base_url,
            'site_type': 'discourse',
            'success': False,
            'error': str(e),
            'results': [],
        }


def search_hackernews(query, max_results=20):
    """
    Search Hacker News using Algolia API.
    https://hn.algolia.com/api
    """
    try:
        url = f"https://hn.algolia.com/api/v1/search?{urlencode({'query': query, 'hitsPerPage': max_results})}"
        response = fetch_with_curl(url)
        data = json.loads(response)

        results = []
        for hit in data.get('hits', []):
            object_id = hit.get('objectID', '')
            results.append({
                'title': hit.get('title') or hit.get('story_title', ''),
                'url': hit.get('url') or f"https://news.ycombinator.com/item?id={object_id}",
                'content': hit.get('comment_text', hit.get('story_text', ''))[:500] if hit.get('comment_text') or hit.get('story_text') else '',
                'score': hit.get('points', 0),
                'source': 'Hacker News',
                'source_type': 'hackernews',
                'author': hit.get('author', ''),
                'published_date': hit.get('created_at', ''),
                'num_comments': hit.get('num_comments', 0),
            })

        return {
            'site': 'https://news.ycombinator.com',
            'site_type': 'hackernews',
            'success': True,
            'results': results,
            'result_count': len(results),
        }
    except Exception as e:
        return {
            'site': 'https://news.ycombinator.com',
            'site_type': 'hackernews',
            'success': False,
            'error': str(e),
            'results': [],
        }


def search_v2ex(query, max_results=20):
    """
    Search V2EX using SOV2EX (third-party search).
    Note: V2EX official API doesn't support search.
    """
    try:
        # Use Google site search as fallback
        url = f"https://www.sov2ex.com/api/search?q={quote_plus(query)}&size={max_results}"
        response = fetch_with_curl(url)
        data = json.loads(response)

        results = []
        for hit in data.get('hits', []):
            source = hit.get('_source', {})
            results.append({
                'title': source.get('title', ''),
                'url': f"https://www.v2ex.com/t/{source.get('id', '')}",
                'content': source.get('content', '')[:500],
                'score': hit.get('_score', 0),
                'source': 'V2EX',
                'source_type': 'v2ex',
                'author': source.get('member', ''),
                'published_date': source.get('created', ''),
                'reply_count': source.get('replies', 0),
            })

        return {
            'site': 'https://v2ex.com',
            'site_type': 'v2ex',
            'success': True,
            'results': results,
            'result_count': len(results),
        }
    except Exception as e:
        return {
            'site': 'https://v2ex.com',
            'site_type': 'v2ex',
            'success': False,
            'error': str(e),
            'results': [],
        }


# =============================================================================
# Main Search Orchestrator
# =============================================================================

def deep_search(query, config):
    """
    Perform deep search across all configured sources.

    Config structure:
    {
        "search": {
            "tavily": {"api_key": "..."},
            "exa": {"api_key": "..."}
        },
        "sites": [
            {"url": "https://linux.do", "type": "discourse", "name": "Linux.do"},
            {"url": "https://news.ycombinator.com", "type": "hackernews"},
            {"url": "https://v2ex.com", "type": "v2ex"}
        ]
    }
    """
    results = {
        'query': query,
        'searched_at': datetime.now(timezone.utc).isoformat(),
        'engines': [],
        'sites': [],
        'all_results': [],
    }

    search_config = config.get('search', {})
    sites = config.get('sites', [])

    futures = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit search engine queries
        tavily_key = search_config.get('tavily', {}).get('api_key', '')
        if tavily_key:
            futures.append(('engine', executor.submit(search_tavily, query, tavily_key)))

        exa_key = search_config.get('exa', {}).get('api_key', '')
        if exa_key:
            futures.append(('engine', executor.submit(search_exa, query, exa_key)))

        # Submit site-specific queries
        for site in sites:
            site_type = site.get('type', '').lower()
            site_url = site.get('url', '')
            site_name = site.get('name')

            if site_type == 'discourse':
                futures.append(('site', executor.submit(search_discourse, site_url, query, site_name)))
            elif site_type == 'hackernews':
                futures.append(('site', executor.submit(search_hackernews, query)))
            elif site_type == 'v2ex':
                futures.append(('site', executor.submit(search_v2ex, query)))

        # Collect results
        for result_type, future in futures:
            try:
                result = future.result(timeout=30)
                if result_type == 'engine':
                    results['engines'].append(result)
                else:
                    results['sites'].append(result)

                # Merge all results
                results['all_results'].extend(result.get('results', []))
            except Exception as e:
                if result_type == 'engine':
                    results['engines'].append({'success': False, 'error': str(e)})
                else:
                    results['sites'].append({'success': False, 'error': str(e)})

    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for item in results['all_results']:
        url = item.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(item)

    # Sort by score
    unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)
    results['all_results'] = unique_results
    results['total_results'] = len(unique_results)

    return results


def main():
    parser = argparse.ArgumentParser(description='Deep search across multiple sources')
    parser.add_argument('--config', help='JSON config file with API keys and sites')
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--tavily-key', help='Tavily API key (overrides config)')
    parser.add_argument('--exa-key', help='Exa API key (overrides config)')
    parser.add_argument('--max-results', type=int, default=20, help='Max results per source')
    args = parser.parse_args()

    # Load config
    config = {'search': {}, 'sites': []}
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Override with CLI args
    if args.tavily_key:
        config.setdefault('search', {})['tavily'] = {'api_key': args.tavily_key}
    if args.exa_key:
        config.setdefault('search', {})['exa'] = {'api_key': args.exa_key}

    # Perform search
    results = deep_search(args.query, config)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
