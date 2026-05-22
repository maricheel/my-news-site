#!/usr/bin/env python3
"""
WordPress → Custom Website Automation
Fetches latest post (with thumbnail + category names) and publishes it.
"""

import requests
import json
import re
import os
import html
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

WEBSITE_URL  = os.getenv('WEBSITE_URL', 'https://your-domain.vercel.app')
API_KEY      = os.getenv('API_KEY', 'your_api_key_here')
WORDPRESS_URL = os.getenv('WORDPRESS_URL', 'https://topnewsshow.com')

# ── Show detection ────────────────────────────────────────────────────────────
# Maps lowercase keywords (from the title) → canonical show name.
# Used as fallback when WordPress categories are missing or wrong.
SHOW_KEYWORDS = [
    ('morning joe',              'Morning Joe'),
    ('jansing',                  'Chris Jansing Reports'),
    ('katy tur',                 'Katy Tur Reports'),
    ('deadline',                 'Deadline: White House'),
    ('ari melber',               'The Beat With Ari Melber'),
    ('the beat',                 'The Beat With Ari Melber'),
    ('weeknight',                'The Weeknight'),
    ('all in',                   'All In with Chris Hayes'),
    ('chris hayes',              'All In with Chris Hayes'),
    ('maddow',                   'The Rachel Maddow Show'),
    ('rachel maddow',            'The Rachel Maddow Show'),
    ('jen psaki',                'The Briefing with Jen Psaki'),
    ('briefing',                 'The Briefing with Jen Psaki'),
    ('lawrence',                 'The Last Word with Lawrence O\'Donnell'),
    ('last word',                'The Last Word with Lawrence O\'Donnell'),
    ('11th hour',                'The 11th Hour with Stephanie Ruhle'),
    ('stephanie ruhle',          'The 11th Hour with Stephanie Ruhle'),
    ('velshi',                   'Velshi'),
    ('alex witt',                'Alex Witt Reports'),
    ('al sharpton',              'PoliticsNation with Al Sharpton'),
    ('politicsnation',           'PoliticsNation with Al Sharpton'),
    ('the weekend',              'The Weekend'),
]

KNOWN_SHOW_NAMES = {v for _, v in SHOW_KEYWORDS}


def detect_show_from_title(title: str) -> str | None:
    """Return the canonical show name based on keywords in the title."""
    t = title.lower()
    for keyword, show in SHOW_KEYWORDS:
        if keyword in t:
            return show
    return None


def clean_categories(raw: list[str], title: str) -> list[str]:
    """
    Filter out numeric IDs and generic tags; fall back to title detection.
    """
    good = [
        c for c in raw
        if c and not c.strip().isdigit() and c.upper() not in ('UNCATEGORIZED',)
    ]
    # If the only category is a generic/wrong one, prefer title detection
    show = detect_show_from_title(title)
    if show and (not good or good[0] not in KNOWN_SHOW_NAMES):
        return [show]
    return good if good else ([show] if show else [])


# ── Duplicate detection via our own database ──────────────────────────────────
def already_published(wp_post_id: int, title: str) -> bool:
    """
    Return True if this WordPress post has already been published.
    Strategy:
      1. Search the DB by title (uses the /search endpoint — always scans all rows).
      2. Fall back to scanning the full post list for an exact wp_post_id match.
    """
    clean_title = html.unescape(title).strip()

    # ── 1. Title search (most reliable — searches entire DB) ──────────────────
    try:
        r = requests.get(
            f'{WEBSITE_URL}/api/posts/search',
            params={'q': clean_title[:80], 'limit': 10},
            timeout=15,
        )
        if r.status_code == 200:
            for post in r.json().get('posts', []):
                stored = html.unescape(post.get('title', '')).strip()
                if stored.lower() == clean_title.lower():
                    print(f"ℹ️  Duplicate via title search: '{clean_title}'")
                    return True
    except Exception as e:
        print(f"[WARN] Title search failed: {e}")

    # ── 2. Exact wp_post_id match across all stored posts ────────────────────
    try:
        page = 1
        while True:
            r = requests.get(
                f'{WEBSITE_URL}/api/posts',
                params={'page': page, 'limit': 100, 'sort': 'newest'},
                timeout=15,
            )
            if r.status_code != 200:
                break
            data  = r.json()
            posts = data.get('posts', [])
            if not posts:
                break
            for post in posts:
                stored_id = post.get('metadata', {}).get('wp_post_id')
                if stored_id and int(stored_id) == wp_post_id:
                    print(f"ℹ️  Duplicate via wp_post_id={wp_post_id}")
                    return True
            # Stop if we've seen all pages
            if page >= data.get('pages', 1):
                break
            page += 1
    except Exception as e:
        print(f"[WARN] wp_post_id scan failed: {e}")

    return False


# ── WordPress fetcher ─────────────────────────────────────────────────────────
def parse_wp_post(post) -> dict | None:
    """Convert a raw WordPress post object into a publishable dict, or None to skip."""
    wp_post_id = post['id']
    title_raw  = post['title']['rendered']
    title      = html.unescape(title_raw)

    if already_published(wp_post_id, title):
        return None

    content = post['content']['rendered']

    # Rumble embed
    rumble_link = ''
    m = re.search(r'https://rumble\.com/embed/([a-zA-Z0-9]+)', content)
    if m:
        rumble_link = f'https://rumble.com/embed/{m.group(1)}/'

    # Thumbnail from embedded media
    thumbnail_url = ''
    try:
        media  = post['_embedded']['wp:featuredmedia'][0]
        sizes  = media.get('media_details', {}).get('sizes', {})
        thumbnail_url = (
            sizes.get('medium_large', {}).get('source_url') or
            sizes.get('large',        {}).get('source_url') or
            sizes.get('medium',       {}).get('source_url') or
            media.get('source_url', '')
        )
    except (KeyError, IndexError, TypeError):
        pass

    # Category names from embedded terms
    raw_categories = []
    try:
        for term in post['_embedded']['wp:term'][0]:
            if term.get('taxonomy') == 'category':
                raw_categories.append(html.unescape(term.get('name', '')))
    except (KeyError, IndexError, TypeError):
        pass

    category_names = clean_categories(raw_categories, title)

    # Reject posts with no recognised show category
    if not category_names or category_names[0] not in KNOWN_SHOW_NAMES:
        print(f"⏭️  Skipping #{wp_post_id} — no recognised show "
              f"(got: {category_names}) | {title[:60]}")
        return None

    excerpt = re.sub(r'<[^>]+>', '', post.get('excerpt', {}).get('rendered', '')).strip()

    print(f"✅ New post #{wp_post_id}: {title}")
    print(f"   Categories: {category_names} | Thumbnail: {'yes' if thumbnail_url else 'none'}")

    return {
        'wp_post_id':        wp_post_id,
        'title':             title,
        'content':           content,
        'rumble_link':       rumble_link,
        'thumbnail_url':     thumbnail_url,
        'categories':        category_names,
        'featured_image_id': post.get('featured_media', 0),
        'metadata': {
            'wp_post_id':            wp_post_id,
            'rank_math_description': excerpt,
            'focus_keyword':         category_names[0] if category_names else 'news',
        },
    }


def get_wordpress_posts(per_page: int = 20) -> list[dict]:
    """
    Fetch the latest `per_page` posts from WordPress and return all that
    haven't been published yet (oldest-first so the feed stays in order).
    """
    print(f"📥 Fetching up to {per_page} latest posts from: {WORDPRESS_URL}")
    try:
        url = (f'{WORDPRESS_URL}/wp-json/wp/v2/posts'
               f'?per_page={per_page}&order=desc&_embed')
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            print(f"❌ WordPress returned {response.status_code}")
            return []

        raw_posts = response.json()
        if not raw_posts:
            print("ℹ️  No posts on WordPress yet.")
            return []

        print(f"   WordPress returned {len(raw_posts)} posts — checking each…")
        to_publish = []
        for raw in raw_posts:
            parsed = parse_wp_post(raw)
            if parsed:
                to_publish.append(parsed)

        # Publish oldest first so the timeline is correct
        to_publish.reverse()
        print(f"\n📋 {len(to_publish)} new post(s) to publish.\n")
        return to_publish

    except Exception as e:
        print(f"❌ ERROR fetching WordPress: {e}")
        return []


# ── Publisher ─────────────────────────────────────────────────────────────────
def send_post_to_website(post_data):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type':  'application/json',
    }
    payload = {k: v for k, v in post_data.items() if k != 'wp_post_id'}

    try:
        print(f"📤 Sending to: {WEBSITE_URL}/api/posts")
        r = requests.post(
            f'{WEBSITE_URL}/api/posts',
            headers=headers,
            json=payload,
            timeout=15,
        )
        if r.status_code == 201:
            print(f"✅ Published! Site post ID: {r.json()['id']}")
            return True
        else:
            print(f"❌ Failed! Status: {r.status_code} — {r.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR sending post: {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*50)
    print(f"⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Automation running")
    print("="*50 + "\n")

    posts = get_wordpress_posts(per_page=20)
    if not posts:
        print("ℹ️  Nothing new to publish.\n")
        return True

    published = 0
    failed    = 0
    for post_data in posts:
        ok = send_post_to_website(post_data)
        if ok:
            published += 1
        else:
            failed += 1

    print(f"\n{'='*50}")
    print(f"✅ Published: {published}  |  ❌ Failed: {failed}")
    print(f"{'='*50}\n")
    return failed == 0


if __name__ == '__main__':
    main()
