# Complete Guide: Build Custom Website from Scratch with Python Flask

## Overview
You're building a **Python Flask web application** that replaces WordPress. Your automation script will send posts to your website's API, which stores them in SQLite and displays them on a beautiful frontend.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Step 1: Local Setup](#step-1-local-setup)
4. [Step 2: Backend (Flask API)](#step-2-backend-flask-api)
5. [Step 3: Frontend (HTML/CSS/JS)](#step-3-frontend)
6. [Step 4: Database](#step-4-database)
7. [Step 5: Deployment to Vercel](#step-5-deployment)
8. [Step 6: Connect Your Automation](#step-6-connect-automation)
9. [Testing](#testing)

---

## Prerequisites

You'll need:
- **Python 3.8+** installed (download from python.org)
- **Git** (for version control and deployment)
- **GitHub account** (free at github.com)
- **Vercel account** (free at vercel.com)
- **A code editor** (VS Code recommended, free)

Check if Python is installed:
```bash
python --version
pip --version
```

---

## Project Structure

```
wordpress-replacement/
├── app.py                 # Flask backend (API server)
├── requirements.txt       # Python dependencies
├── database.db           # SQLite database (auto-created)
├── .env                  # Environment variables (API key, secret)
├── .gitignore           # Git ignore file
├── vercel.json          # Deployment config
├── api/
│   └── index.py         # For Vercel deployment
├── static/
│   ├── style.css        # Website styling
│   └── script.js        # Frontend JavaScript
└── templates/
    ├── base.html        # Base template (header, footer)
    ├── index.html       # Homepage (post list)
    ├── post.html        # Single post page
    ├── admin.html       # Admin dashboard
    └── search.html      # Search results
```

---

## Step 1: Local Setup

### 1.1 Create Project Directory

```bash
# Create and navigate to project folder
mkdir wordpress-replacement
cd wordpress-replacement

# Initialize Git
git init
```

### 1.2 Create Virtual Environment

```bash
# Create virtual environment (isolates Python packages)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

After activation, you should see `(venv)` in your terminal.

### 1.3 Install Dependencies

Create `requirements.txt`:
```
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
requests==2.31.0
```

Install them:
```bash
pip install -r requirements.txt
```

---

## Step 2: Backend (Flask API)

### 2.1 Create `.env` File

This stores your secret API key. Create file named `.env`:
```
FLASK_ENV=development
API_KEY=your_secret_api_key_12345
SECRET_KEY=your_flask_secret_key_xyz
```

Replace these with random secure strings. You can use: https://randomkeygen.com/

### 2.2 Create `.gitignore` File

Never commit secrets to Git. Create `.gitignore`:
```
venv/
.env
database.db
__pycache__/
*.pyc
.DS_Store
node_modules/
.vercel/
```

### 2.3 Create Main Flask App (`app.py`)

See the `app.py` file in this guide (provided separately).

This file contains:
- Flask app setup
- SQLite database connection
- API endpoints (POST, GET, DELETE, SEARCH)
- Authentication (API key validation)
- Error handling
- CORS (allow frontend to call API)

### 2.4 Test Locally

```bash
# Run Flask development server
python app.py

# You should see:
# Running on http://127.0.0.1:5000
```

**Test the API** (in another terminal):
```bash
# Create a test post
curl -X POST http://localhost:5000/api/posts \
  -H "Authorization: Bearer your_secret_api_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Post",
    "content": "<p>This is a test</p>",
    "rumble_link": "https://rumble.com/embed/test/",
    "categories": [24, 39],
    "featured_image_id": 1832
  }'

# Get all posts
curl http://localhost:5000/api/posts

# Get single post (replace 1 with actual ID)
curl http://localhost:5000/api/posts/1
```

---

## Step 3: Frontend

### 3.1 Create HTML Templates

Templates use **Jinja2** (Flask's template language). Create `templates/` folder.

See separate files:
- `templates/base.html` — Header, footer, navigation
- `templates/index.html` — Homepage with post grid
- `templates/post.html` — Single post detail page
- `templates/admin.html` — Admin dashboard
- `templates/search.html` — Search results

### 3.2 Create CSS (`static/style.css`)

Modern, responsive design using CSS Grid and Flexbox.

See separate `static/style.css` file.

### 3.3 Create JavaScript (`static/script.js`)

Handles:
- Fetch posts from API
- Search functionality
- Filter by category
- Pagination
- Delete posts (admin)

See separate `static/script.js` file.

---

## Step 4: Database

### 4.1 How It Works

SQLite is a file-based database (no setup needed). Your `app.py` automatically creates `database.db` when you first run it.

### 4.2 Database Schema

The database has one main table: `posts`

```sql
CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  rumble_link TEXT,
  featured_image_id INTEGER,
  categories TEXT,  -- Stored as JSON string: '[24, 39, 100]'
  metadata TEXT,     -- Stored as JSON: '{"keyword": "...", "description": "..."}'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  source TEXT        -- 'automation' or 'manual'
);
```

Your `app.py` creates this automatically.

### 4.3 View Database (Optional)

Install DB Browser for SQLite (optional, for inspection):
https://sqlitebrowser.org/

---

## Step 5: Deployment to Vercel

### 5.1 Push to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: Flask website"

# Create GitHub repo, then:
git remote add origin https://github.com/YOUR_USERNAME/wordpress-replacement.git
git branch -M main
git push -u origin main
```

### 5.2 Deploy to Vercel

1. Go to **vercel.com** and sign in with GitHub
2. Click **"New Project"**
3. Select your `wordpress-replacement` repo
4. Click **"Import"**
5. **Environment Variables:**
   - Add `API_KEY` = your secret key
   - Add `SECRET_KEY` = random string
6. Click **"Deploy"**

Vercel will give you a URL like: `https://wordpress-replacement-abc123.vercel.app`

### 5.3 Create `vercel.json`

Create file named `vercel.json` in root:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHONUNBUFFERED": "1"
  }
}
```

### 5.4 Create `api/index.py`

For Vercel deployment, create `api/index.py`:
```python
from app import app

# This is the entry point for Vercel

def handler(request):
    return app(request.environ, request.start_response)
```

---

## Step 6: Connect Your Automation

### 6.1 Modify Google Apps Script

In your Google Apps Script (the automation part), change the WordPress endpoint to your new website:

**Old code (WordPress):**
```javascript
const url = "https://thuyance.com/wp-json/wp/v2/posts";
```

**New code (Your Website):**
```javascript
const url = "https://wordpress-replacement-abc123.vercel.app/api/posts";
// Replace abc123 with your actual Vercel domain
```

### 6.2 Update the Payload

Keep the same data structure:
```javascript
const payload = {
  title: "{{ $('get link ok').item.json.title }} latest msnbc news",
  content: "<p><iframe class=\"rumble\" src=\"{{ rumble_link }}\" ...></p>",
  rumble_link: "https://rumble.com/embed/VIDEO_ID/",
  categories: [24, 39, {{ category_id }}],
  featured_image_id: {{ image_id }},
  metadata: {
    rank_math_description: "...",
    focus_keyword: "..."
  }
};

const options = {
  method: "POST",
  headers: {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
  },
  payload: JSON.stringify(payload)
};

const response = UrlFetchApp.fetch(url, options);
```

### 6.3 Update the API Key

Use the same `API_KEY` you set in Vercel environment variables.

---

## Testing

### 7.1 Test API Endpoints

**Create a test post:**
```bash
curl -X POST https://your-vercel-domain.vercel.app/api/posts \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Post",
    "content": "<p>Hello World</p>",
    "rumble_link": "https://rumble.com/embed/test/",
    "categories": [24],
    "featured_image_id": 100
  }'
```

**Get all posts:**
```bash
curl https://your-vercel-domain.vercel.app/api/posts
```

**Search posts:**
```bash
curl "https://your-vercel-domain.vercel.app/api/posts/search?q=test"
```

### 7.2 Test Frontend

Visit `https://your-vercel-domain.vercel.app/` in browser.

You should see:
- Homepage with grid of posts
- Search bar
- Category filters
- Click on post to see full detail
- Admin dashboard link

### 7.3 Check Logs

In Vercel dashboard:
- Click your project
- Go to **"Deployments"** → latest deploy
- Click **"Runtime Logs"** to see errors

---

## Troubleshooting

### "API Key Invalid"
- Check `API_KEY` in Vercel environment variables
- Make sure it matches the key in your Google Apps Script
- Restart the deployment after changing env vars

### "Posts not showing"
- Check browser console (F12 → Console tab) for JavaScript errors
- Check Vercel logs for backend errors
- Make sure database has posts: visit `/api/posts` directly

### "Can't connect to API from local frontend"
- Make sure Flask is running: `python app.py`
- Check CORS is enabled in `app.py`
- Use `http://localhost:5000` not `http://127.0.0.1:5000`

### "Vercel deployment failed"
- Check that `vercel.json` and `api/index.py` exist
- Make sure `requirements.txt` is in root directory
- Check build logs in Vercel dashboard

---

## Next Steps

1. **Custom domain:** In Vercel, add your domain (optional)
2. **HTTPS:** Auto-enabled by Vercel
3. **Email notifications:** Add when new posts arrive
4. **Analytics:** Track views with Vercel Analytics
5. **Admin auth:** Add login for admin dashboard
6. **Images:** Upload featured images, store on Cloudinary (free)

---

## File Checklist

Before deploying, make sure you have:
- [ ] `app.py` — Flask backend
- [ ] `requirements.txt` — Dependencies
- [ ] `.env` — Local environment variables
- [ ] `.gitignore` — Exclude secrets
- [ ] `vercel.json` — Deployment config
- [ ] `api/index.py` — Vercel entry point
- [ ] `templates/base.html` — Base template
- [ ] `templates/index.html` — Homepage
- [ ] `templates/post.html` — Post detail
- [ ] `templates/admin.html` — Admin dashboard
- [ ] `static/style.css` — Styling
- [ ] `static/script.js` — Frontend logic
- [ ] GitHub repo created and pushed
- [ ] Vercel project deployed

---

## Support

If you get stuck:
1. Check the file examples provided
2. Look at Vercel logs
3. Check browser console for frontend errors
4. Test API directly with curl
5. Read Flask documentation: flask.palletsprojects.com

Good luck! 🚀
