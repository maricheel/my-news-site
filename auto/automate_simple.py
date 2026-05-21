#!/usr/bin/env python3
"""
WordPress → Custom Website Automation
Fetches latest post (with thumbnail + category names) and publishes it every 45 minutes.
"""

import requests
import json
import re
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

WEBSITE_URL = os.getenv('WEBSITE_URL', 'https://your-domain.vercel.app')
API_KEY = os.getenv('API_KEY', 'your_api_key_here')
WORDPRESS_URL = os.getenv('WORDPRESS_URL', 'https://thuyance.com')

# Track last published post ID to avoid duplicates
LAST_ID_FILE = '/tmp/last_post_id.txt' if os.getenv('VERCEL') else 'last_post_id.txt'


def get_last_published_id():
    try:
        with open(LAST_ID_FILE, 'r') as f:
            return int(f.read().strip())
    except Exception:
        return 0


def save_last_published_id(post_id):
    try:
        with open(LAST_ID_FILE, 'w') as f:
            f.write(str(post_id))
    except Exception:
        pass


def get_wordpress_post():
    """Fetch the latest post from WordPress with embedded image and categories."""
    try:
        print(f"📥 Fetching latest post from: {WORDPRESS_URL}")

        # _embed gives us featured image URL and category names in one request
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

        # Skip if already published
        if wp_post_id <= get_last_published_id():
            print(f"ℹ️ Post {wp_post_id} already published. Nothing new.")
            return None

        # Title and content
        title = post['title']['rendered']
        content = post['content']['rendered']

        # Rumble embed link
        rumble_link = ''
        rumble_match = re.search(r'https://rumble\.com/embed/([a-zA-Z0-9]+)', content)
        if rumble_match:
            rumble_link = f'https://rumble.com/embed/{rumble_match.group(1)}/'

        # Thumbnail URL from embedded media
        thumbnail_url = ''
        try:
            media = post['_embedded']['wp:featuredmedia'][0]
            # Prefer medium_large, fall back to full
            sizes = media.get('media_details', {}).get('sizes', {})
            thumbnail_url = (
                sizes.get('medium_large', {}).get('source_url') or
                sizes.get('large', {}).get('source_url') or
                sizes.get('medium', {}).get('source_url') or
                media.get('source_url', '')
            )
        except (KeyError, IndexError, TypeError):
            pass

        # Category names from embedded terms
        category_names = []
        try:
            for term in post['_embedded']['wp:term'][0]:
                if term.get('taxonomy') == 'category' and term.get('name') != 'Uncategorized':
                    category_names.append(term['name'])
        except (KeyError, IndexError, TypeError):
            pass

        # Excerpt for metadata
        excerpt = re.sub(r'<[^>]+>', '', post.get('excerpt', {}).get('rendered', '')).strip()

        print(f"✅ Found post: {title}")
        print(f"   Categories: {category_names}")
        print(f"   Thumbnail: {'yes' if thumbnail_url else 'none'}")

        return {
            'wp_post_id': wp_post_id,
            'title': title,
            'content': content,
            'rumble_link': rumble_link,
            'thumbnail_url': thumbnail_url,
            'categories': category_names,
            'featured_image_id': post.get('featured_media', 0),
            'metadata': {
                'rank_math_description': excerpt,
                'focus_keyword': category_names[0] if category_names else 'news'
            }
        }

    except Exception as e:
        print(f"❌ ERROR fetching WordPress: {e}")
        return None


def send_post_to_website(post_data):
    """Send a post to your website API."""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {k: v for k, v in post_data.items() if k != 'wp_post_id'}

    try:
        print(f"📤 Sending to: {WEBSITE_URL}/api/posts")
        response = requests.post(
            f'{WEBSITE_URL}/api/posts',
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code == 201:
            result = response.json()
            print(f"✅ Published! Site post ID: {result['id']}")
            return True
        else:
            print(f"❌ Failed! Status: {response.status_code} — {response.text}")
            return False

    except Exception as e:
        print(f"❌ ERROR sending post: {e}")
        return False


def main():
    print("\n" + "="*50)
    print(f"⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Automation running")
    print("="*50 + "\n")

    post_data = get_wordpress_post()

    if not post_data:
        return False

    success = send_post_to_website(post_data)

    if success:
        save_last_published_id(post_data['wp_post_id'])
        print("\n✅ Done!\n")
    else:
        print("\n❌ Failed. Check URL and API key.\n")

    return success


if __name__ == '__main__':
    main()
