#!/usr/bin/env python3
"""
Simple WordPress to Custom Website Automation
Send posts to your website every 45 minutes
"""

import requests
import json
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Load configuration from .env file
load_dotenv()

WEBSITE_URL = os.getenv('WEBSITE_URL', 'https://your-domain.vercel.app')
API_KEY = os.getenv('API_KEY', 'your_api_key_here')
WORDPRESS_URL = os.getenv('WORDPRESS_URL', 'https://thuyance.com')


def send_post_to_website(post_data):
    """Send a post to your website API"""
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"📤 Sending post to: {WEBSITE_URL}/api/posts")
        
        response = requests.post(
            f'{WEBSITE_URL}/api/posts',
            headers=headers,
            json=post_data,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ SUCCESS! Post created with ID: {result['id']}")
            return True
        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def get_wordpress_post():
    """Fetch latest post from WordPress"""
    
    try:
        print(f"📥 Fetching post from: {WORDPRESS_URL}")
        
        # Get latest post from WordPress API
        url = f'{WORDPRESS_URL}/wp-json/wp/v2/posts?per_page=1&order=desc'
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch from WordPress: {response.status_code}")
            return None
        
        posts = response.json()
        if not posts:
            print("ℹ️ No posts found")
            return None
        
        post = posts[0]
        
        # Extract title
        title = post['title']['rendered']
        
        # Extract content
        content = post['content']['rendered']
        
        # Extract Rumble link using regex
        rumble_link = ''
        rumble_match = re.search(r'https://rumble\.com/embed/([a-zA-Z0-9]+)', content)
        if rumble_match:
            rumble_link = f'https://rumble.com/embed/{rumble_match.group(1)}/'
        
        # Get categories
        categories = post.get('categories', [])
        
        # Get featured image ID
        featured_image_id = post.get('featured_media', 0)
        
        # Extract excerpt for metadata
        excerpt = post.get('excerpt', {}).get('rendered', '').replace('<p>', '').replace('</p>', '')
        
        print(f"✅ Found post: {title}")
        
        return {
            'title': title,
            'content': content,
            'rumble_link': rumble_link,
            'categories': categories,
            'featured_image_id': featured_image_id,
            'metadata': {
                'rank_math_description': excerpt,
                'focus_keyword': 'news'
            }
        }
    
    except Exception as e:
        print(f"❌ ERROR fetching WordPress: {e}")
        return None


def send_test_post():
    """Send a test post to verify everything works"""
    
    test_post = {
        'title': f'Test Post - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        'content': '<p><iframe src="https://rumble.com/embed/test/"></iframe></p>',
        'rumble_link': 'https://rumble.com/embed/test/',
        'categories': [24, 39],
        'featured_image_id': 100,
        'metadata': {
            'rank_math_description': 'Test post from Python automation',
            'focus_keyword': 'test'
        }
    }
    
    print("📝 Sending test post...")
    return send_post_to_website(test_post)


def main():
    """Main automation function"""
    
    print("\n" + "="*50)
    print(f"⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting automation")
    print("="*50 + "\n")
    
    # Fetch latest WordPress post
    post_data = get_wordpress_post()
    
    if not post_data:
        print("\n❌ Could not fetch post. Check your WordPress URL and API access.\n")
        return False
    
    # Send to your website
    success = send_post_to_website(post_data)
    
    if success:
        print("\n✅ Automation completed successfully!\n")
    else:
        print("\n❌ Automation failed. Check your website URL and API key.\n")
    
    return success


if __name__ == '__main__':
    main()
