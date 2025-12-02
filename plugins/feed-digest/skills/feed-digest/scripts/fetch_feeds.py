#!/usr/bin/env python3
"""
Fetch and parse multiple RSS/Atom feeds.
Returns structured JSON with posts from all configured sources.

Usage:
    python fetch_feeds.py <feeds_config.json>
    python fetch_feeds.py --urls "url1,url2,url3"

Output: JSON with all posts merged, ready for Claude to classify and score.
"""

import sys
import os
import json
import argparse
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def strip_html(html_text):
    """Remove HTML tags and decode entities."""
    if not html_text:
        return ""
    text = re.sub(r'<[^>]+>', '', html_text)
    return unescape(text).strip()

def parse_date(date_str):
    """Parse various date formats from RSS/Atom feeds."""
    if not date_str:
        return None
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",      # RSS
        "%a, %d %b %Y %H:%M:%S %Z",      # RSS with timezone name
        "%Y-%m-%dT%H:%M:%S%z",           # Atom ISO
        "%Y-%m-%dT%H:%M:%SZ",            # Atom UTC
        "%Y-%m-%d %H:%M:%S",             # Simple
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None

def fetch_with_curl(url):
    """Fetch URL using curl (works with TUN/system proxy)."""
    result = subprocess.run(
        ['curl', '-sS', '-L', '--connect-timeout', '15', '--max-time', '30', url],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")
    return result.stdout

def detect_feed_type(root):
    """Detect if feed is RSS or Atom."""
    tag = root.tag.lower()
    if 'feed' in tag:
        return 'atom'
    return 'rss'

def parse_rss(root, source_name, source_url):
    """Parse RSS 2.0 format."""
    channel = root.find('channel')
    if channel is None:
        return []

    feed_title = channel.findtext('title', source_name)
    posts = []

    for item in channel.findall('item'):
        title = item.findtext('title', '')
        link = item.findtext('link', '')
        description = strip_html(item.findtext('description', ''))
        pub_date_str = item.findtext('pubDate', '')
        pub_date = parse_date(pub_date_str)

        categories = [cat.text for cat in item.findall('category') if cat.text]
        creator = item.findtext('{http://purl.org/dc/elements/1.1/}creator', '')

        posts.append({
            'title': title,
            'link': link,
            'description': description[:800] if description else '',
            'pub_date': pub_date.isoformat() if pub_date else pub_date_str,
            'categories': categories,
            'creator': creator,
            'source': feed_title,
            'source_url': source_url,
        })

    return posts

def parse_atom(root, source_name, source_url):
    """Parse Atom format."""
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    # Handle namespace
    if root.tag.startswith('{'):
        ns_uri = root.tag.split('}')[0] + '}'
        entries = root.findall(f'{ns_uri}entry')
        feed_title = root.findtext(f'{ns_uri}title', source_name)
    else:
        entries = root.findall('entry', ns) or root.findall('entry')
        feed_title = root.findtext('title', source_name)

    posts = []
    for entry in entries:
        # Handle namespaced or non-namespaced
        if root.tag.startswith('{'):
            title = entry.findtext(f'{ns_uri}title', '')
            link_elem = entry.find(f'{ns_uri}link')
            content = entry.findtext(f'{ns_uri}content', '') or entry.findtext(f'{ns_uri}summary', '')
            updated = entry.findtext(f'{ns_uri}updated', '') or entry.findtext(f'{ns_uri}published', '')
            author_elem = entry.find(f'{ns_uri}author')
            creator = author_elem.findtext(f'{ns_uri}name', '') if author_elem is not None else ''
        else:
            title = entry.findtext('title', '')
            link_elem = entry.find('link')
            content = entry.findtext('content', '') or entry.findtext('summary', '')
            updated = entry.findtext('updated', '') or entry.findtext('published', '')
            author_elem = entry.find('author')
            creator = author_elem.findtext('name', '') if author_elem is not None else ''

        link = link_elem.get('href', '') if link_elem is not None else ''
        description = strip_html(content)
        pub_date = parse_date(updated)

        posts.append({
            'title': title,
            'link': link,
            'description': description[:800] if description else '',
            'pub_date': pub_date.isoformat() if pub_date else updated,
            'categories': [],
            'creator': creator,
            'source': feed_title,
            'source_url': source_url,
        })

    return posts

def fetch_and_parse_feed(url, name=None):
    """Fetch a single feed and parse it."""
    try:
        xml_content = fetch_with_curl(url)
        root = ET.fromstring(xml_content)

        feed_type = detect_feed_type(root)
        source_name = name or url

        if feed_type == 'atom':
            posts = parse_atom(root, source_name, url)
        else:
            posts = parse_rss(root, source_name, url)

        return {
            'url': url,
            'name': name,
            'success': True,
            'post_count': len(posts),
            'posts': posts
        }
    except Exception as e:
        return {
            'url': url,
            'name': name,
            'success': False,
            'error': str(e),
            'posts': []
        }

def fetch_all_feeds(feeds):
    """Fetch all feeds concurrently."""
    results = []
    all_posts = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_feed = {
            executor.submit(fetch_and_parse_feed, f['url'], f.get('name')): f
            for f in feeds
        }

        for future in as_completed(future_to_feed):
            result = future.result()
            results.append({
                'url': result['url'],
                'name': result.get('name'),
                'success': result['success'],
                'post_count': result.get('post_count', 0),
                'error': result.get('error')
            })
            all_posts.extend(result['posts'])

    # Sort by date (newest first)
    all_posts.sort(key=lambda x: x.get('pub_date', ''), reverse=True)

    return {
        'fetched_at': datetime.now(timezone.utc).isoformat(),
        'feed_results': results,
        'total_posts': len(all_posts),
        'posts': all_posts
    }

def main():
    parser = argparse.ArgumentParser(description='Fetch multiple RSS/Atom feeds')
    parser.add_argument('config', nargs='?', help='JSON config file with feeds array')
    parser.add_argument('--urls', help='Comma-separated list of feed URLs')
    parser.add_argument('--filter', help='Comma-separated keywords to filter posts')
    args = parser.parse_args()

    feeds = []

    if args.urls:
        feeds = [{'url': url.strip()} for url in args.urls.split(',')]
    elif args.config:
        with open(args.config) as f:
            data = json.load(f)
            feeds = data.get('feeds', [])
    else:
        # Read from stdin
        data = json.load(sys.stdin)
        feeds = data.get('feeds', [])

    if not feeds:
        print(json.dumps({'error': 'No feeds provided'}), file=sys.stderr)
        sys.exit(1)

    result = fetch_all_feeds(feeds)

    # Apply keyword filter if specified
    if args.filter:
        keywords = [k.strip().lower() for k in args.filter.split(',')]
        filtered_posts = []
        for post in result['posts']:
            text = f"{post['title']} {post['description']}".lower()
            if any(kw in text for kw in keywords):
                filtered_posts.append(post)
        result['posts'] = filtered_posts
        result['total_posts'] = len(filtered_posts)
        result['filter_applied'] = keywords

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
