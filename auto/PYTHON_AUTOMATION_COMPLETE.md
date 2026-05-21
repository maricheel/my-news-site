# Complete Python Automation Script for Your Website

This Python script replaces your Google Apps Script automation. It will:
1. Fetch posts from WordPress (or your data source)
2. Extract necessary information
3. Send to your custom website API
4. Run on a schedule (every 45 minutes)

---

## What You Need

1. **Python 3.7+** installed on your computer
2. **Your website URL** (from Vercel)
3. **Your API key** (from Vercel)
4. **Source data** (WordPress API, Google Sheet, etc.)

---

## Installation

### Step 1: Create a Folder

```bash
mkdir wordpress-automation
cd wordpress-automation
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install requests schedule python-dotenv
```

---

## Create .env File

Create a file named `.env` in your project folder:

```
# Your Website
WEBSITE_URL=https://your-domain.vercel.app
API_KEY=your_api_key_from_vercel

# Optional: If fetching from WordPress
WORDPRESS_URL=https://thuyance.com
WORDPRESS_API_KEY=your_wordpress_key

# Optional: If fetching from Google Sheets
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_API_KEY=your_google_key
```

---

## Python Script - Simple Version (Copy & Use)

Create a file named `automate.py`:

```python
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

WEBSITE_URL = os.getenv('WEBSITE_URL')
API_KEY = os.getenv('API_KEY')

def send_post_to_website(post_data):
    """
    Send a post to your website API
    
    post_data should be a dict with:
    {
        'title': 'Post Title',
        'content': '<p>HTML content</p>',
        'rumble_link': 'https://rumble.com/embed/xxx/',
        'categories': [24, 39],
        'featured_image_id': 100,
        'metadata': {
            'rank_math_description': '...',
            'focus_keyword': '...'
        }
    }
    """
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f'{WEBSITE_URL}/api/posts',
            headers=headers,
            json=post_data
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ SUCCESS! Post created. ID: {result['id']}")
            return True
        else:
            print(f"❌ FAILED. Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_post():
    """Send a test post to your website"""
    
    test_data = {
        'title': f'Test Post - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        'content': '<p>This is a test post from Python automation</p>',
        'rumble_link': 'https://rumble.com/embed/test/',
        'categories': [24, 39],
        'featured_image_id': 100,
        'metadata': {
            'rank_math_description': 'Test post description',
            'focus_keyword': 'test'
        }
    }
    
    print("Sending test post...")
    return send_post_to_website(test_data)


if __name__ == '__main__':
    # Run the test
    test_post()
```

---

## To Run the Script

```bash
# Make sure virtual environment is activated
python automate.py
```

You should see:
```
✅ SUCCESS! Post created. ID: 1
```

---

## For Real Data: Fetch from WordPress

```python
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import re

load_dotenv()

WEBSITE_URL = os.getenv('WEBSITE_URL')
API_KEY = os.getenv('API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL')


def get_latest_wordpress_post():
    """Fetch the latest post from WordPress"""
    
    try:
        # Get latest post from WordPress
        url = f'{WORDPRESS_URL}/wp-json/wp/v2/posts?per_page=1&order=desc'
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch from WordPress")
            return None
        
        posts = response.json()
        if not posts:
            print("No posts found")
            return None
        
        post = posts[0]
        
        # Extract data
        title = post['title']['rendered']
        content = post['content']['rendered']
        
        # Extract Rumble link from content (adjust regex as needed)
        rumble_match = re.search(r'https://rumble\.com/embed/([a-zA-Z0-9]+)', content)
        rumble_link = f'https://rumble.com/embed/{rumble_match.group(1)}/' if rumble_match else ''
        
        # Get category IDs
        categories = post.get('categories', [])
        
        # Get featured image ID
        featured_image_id = post.get('featured_media', '')
        
        # Build metadata
        metadata = {
            'rank_math_description': post.get('excerpt', {}).get('rendered', ''),
            'focus_keyword': 'news'  # You can extract this if available
        }
        
        return {
            'title': title,
            'content': content,
            'rumble_link': rumble_link,
            'categories': categories,
            'featured_image_id': featured_image_id,
            'metadata': metadata
        }
    
    except Exception as e:
        print(f"❌ Error fetching WordPress post: {e}")
        return None


def send_post_to_website(post_data):
    """Send post to your website"""
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f'{WEBSITE_URL}/api/posts',
            headers=headers,
            json=post_data
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ SUCCESS! Post created. ID: {result['id']}")
            return True
        else:
            print(f"❌ FAILED. Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Main automation"""
    
    print(f"[{datetime.now()}] Starting automation...")
    
    # Fetch latest post
    post_data = get_latest_wordpress_post()
    
    if not post_data:
        print("No post to send")
        return
    
    # Send to website
    send_post_to_website(post_data)
    
    print("Done!")


if __name__ == '__main__':
    main()
```

---

## Run on Schedule (Every 45 Minutes)

```python
import schedule
import time
from automate import main

# Schedule the job
schedule.every(45).minutes.do(main)

print("Scheduler started. Running every 45 minutes...")
print("Press Ctrl+C to stop")

# Keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(60)
```

Save as `scheduler.py` and run:

```bash
python scheduler.py
```

---

## Deploy on Cloud (Always Running)

For always-running automation, deploy to:

### Option 1: Heroku (Free Tier)

1. Create `Procfile`:
```
worker: python scheduler.py
```

2. Create `requirements.txt`:
```
requests
schedule
python-dotenv
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Option 2: PythonAnywhere (Free)

1. Sign up at pythonanywhere.com
2. Upload your Python files
3. Set up a scheduled task to run daily

### Option 3: AWS Lambda + CloudWatch

1. Package your Python code
2. Create Lambda function
3. Set CloudWatch to trigger every 45 minutes

### Option 4: Digital Ocean (Cheap)

1. Create a $5/month droplet
2. SSH into it
3. Install Python and run your script
4. Use `cron` to schedule it

---

## Complete Production Script

```python
#!/usr/bin/env python3
"""
Complete WordPress → Custom Website Automation
Fetches posts from WordPress and sends to your custom website
"""

import requests
import json
import re
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
load_dotenv()

# Configuration
WEBSITE_URL = os.getenv('WEBSITE_URL')
API_KEY = os.getenv('API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL')

# Logging
LOG_FILE = 'automation.log'


def log(message):
    """Log messages to file and console"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_message + '\n')


def get_latest_wordpress_post():
    """Fetch latest WordPress post"""
    try:
        log("Fetching latest post from WordPress...")
        
        url = f'{WORDPRESS_URL}/wp-json/wp/v2/posts?per_page=1&order=desc'
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            log(f"❌ WordPress request failed: {response.status_code}")
            return None
        
        posts = response.json()
        if not posts:
            log("No posts found on WordPress")
            return None
        
        post = posts[0]
        
        # Extract data
        title = post['title']['rendered']
        content = post['content']['rendered']
        
        # Extract Rumble link
        rumble_match = re.search(r'https://rumble\.com/embed/([a-zA-Z0-9]+)', content)
        rumble_link = f'https://rumble.com/embed/{rumble_match.group(1)}/' if rumble_match else ''
        
        # Categories
        categories = post.get('categories', [])
        
        # Featured image
        featured_image_id = post.get('featured_media', '')
        
        # Metadata
        metadata = {
            'rank_math_description': post.get('excerpt', {}).get('rendered', ''),
            'focus_keyword': 'news'
        }
        
        log(f"✅ Fetched post: {title}")
        
        return {
            'title': title,
            'content': content,
            'rumble_link': rumble_link,
            'categories': categories,
            'featured_image_id': featured_image_id,
            'metadata': metadata
        }
    
    except Exception as e:
        log(f"❌ Error fetching WordPress: {e}")
        return None


def send_to_website(post_data):
    """Send post to your website"""
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{WEBSITE_URL}/api/posts',
            headers=headers,
            json=post_data,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            log(f"✅ Post sent successfully! ID: {result['id']}")
            return True
        else:
            log(f"❌ Failed to send post. Status: {response.status_code}")
            log(f"Response: {response.text}")
            return False
    
    except Exception as e:
        log(f"❌ Error sending to website: {e}")
        return False


def job():
    """The job to run on schedule"""
    try:
        log("Starting automation job...")
        
        # Fetch post
        post_data = get_latest_wordpress_post()
        
        if not post_data:
            log("Skipping - no post to send")
            return
        
        # Send to website
        send_to_website(post_data)
    
    except Exception as e:
        log(f"❌ Job failed: {e}")


def start_scheduler():
    """Start the scheduler"""
    log("Starting scheduler...")
    
    # Run every 45 minutes
    schedule.every(45).minutes.do(job)
    
    # Run once at startup
    job()
    
    log("Scheduler is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        log("Scheduler stopped by user")


def run_once():
    """Run the automation once"""
    log("Running automation once...")
    job()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        # Run once
        run_once()
    else:
        # Run scheduler
        start_scheduler()
```

---

## Usage

### Run Once
```bash
python automate.py once
```

### Run on Schedule
```bash
python automate.py
```

### View Logs
```bash
tail automation.log
```

---

## Testing

### Test 1: Send a test post
```bash
python -c "from automate import send_to_website; send_to_website({'title': 'Test', 'content': '<p>Test</p>', 'categories': [24], 'featured_image_id': 100, 'metadata': {}})"
```

### Test 2: Fetch from WordPress
```bash
python -c "from automate import get_latest_wordpress_post; print(get_latest_wordpress_post())"
```

### Test 3: Full automation
```bash
python automate.py once
```

---

## Advantages of Python

✅ **Better than Google Apps Script:**
- More powerful
- Easier to maintain
- Better error handling
- Can run on any server
- Easy to test locally
- Better debugging
- Can handle complex logic

✅ **Easy to schedule:**
- Run locally on your computer
- Run on a cheap VPS
- Run on cloud (Heroku, AWS, etc.)
- Run with cron jobs

✅ **Flexible:**
- Can fetch from any source
- Can transform data any way you want
- Can handle multiple sources

---

## Next Steps

1. **Create the Python script** (use the code above)
2. **Test it locally** (run once)
3. **Verify it works** (check your website for posts)
4. **Set up scheduling** (run every 45 minutes)
5. **Deploy to cloud** (optional - for always running)

---

## Need Help?

- Can't install Python? Tell me your OS
- Script doesn't work? Send me the error message
- Want to fetch from different source? Tell me which
- Want to deploy to cloud? I can help with Heroku/AWS setup

You're now ready to use Python for your automation! 🚀
