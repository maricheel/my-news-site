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
WORDPRESS_URL = os.getenv('WORDPRESS_URL', 'https://thuyance.com')

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
def get_last_published_wp_id() -> int:
    """
    Check our own API for the highest WordPress post ID already published.
    Works in GitHub Actions where the filesystem is wiped between runs.
    """
    try:
        r = requests.get(f'{WEBSITE_URL}/api/posts?limit=20&sort=newest', timeout=15)
        if r.status_code == 200:
            for post in r.json().get('posts', []):
                wp_id = post.get('metadata', {}).get('wp_post_id', 0)
                if wp_id:
                    return int(wp_id)
    except Exception:
        pass
    return 0


# ── WordPress fetcher ─────────────────────────────────────────────────────────
def get_wordpress_post():
    """Fetch the latest post from WordPress with embedded image and categories."""
    try:
        print(f"📥 Fetching latest post from: {WORDPRESS_URL}")

        url = f'{WORDPRESS_URL}/wp-json/wp/v2/posts?per_page=1&order=desc&_embed'
        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            print(f"❌ Failed to fetch from WordPress: {response.status_code}")
            return None

        posts = response.json()
        if not posts:
            print("ℹ️ No posts found")
            return None

        post = posts[0]
        wp_post_id = post['id']

        last_id = get_last_published_wp_id()
        if wp_post_id <= last_id:
            print(f"ℹ️ Post {wp_post_id} already published (last known: {last_id}). Nothing new.")
            return None

        # Title — decode HTML entities (e.g. &#8211; → –)
        title = html.unescape(post['title']['rendered'])

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

        excerpt = re.sub(r'<[^>]+>', '', post.get('excerpt', {}).get('rendered', '')).strip()

        print(f"✅ Found post #{wp_post_id}: {title}")
        print(f"   Categories: {category_names}")
        print(f"   Thumbnail:  {'yes' if thumbnail_url else 'none'}")

        return {
            'wp_post_id':       wp_post_id,
            'title':            title,
            'content':          content,
            'rumble_link':      rumble_link,
            'thumbnail_url':    thumbnail_url,
            'categories':       category_names,
            'featured_image_id': post.get('featured_media', 0),
            'metadata': {
                'wp_post_id':             wp_post_id,   # stored for duplicate detection
                'rank_math_description':  excerpt,
                'focus_keyword':          category_names[0] if category_names else 'news',
            },
        }

    except Exception as e:
        print(f"❌ ERROR fetching WordPress: {e}")
        return None


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

    post_data = get_wordpress_post()
    if not post_data:
        return False

    success = send_post_to_website(post_data)
    print("\n✅ Done!\n" if success else "\n❌ Failed. Check URL and API key.\n")
    return success


if __name__ == '__main__':
    main()
