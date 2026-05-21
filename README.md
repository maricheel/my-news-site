# Custom News Website - WordPress Replacement

A complete Python Flask web application that replaces WordPress. Your automation script sends posts to this website's API, which stores them in SQLite and displays them with a modern, responsive UI.

## Features

✅ **REST API** - POST endpoint for automated content  
✅ **SQLite Database** - File-based, no setup needed  
✅ **Responsive Design** - Mobile-friendly frontend  
✅ **Post Management** - View, search, filter, delete posts  
✅ **Admin Dashboard** - Statistics and post management  
✅ **Search Functionality** - Full-text search by title  
✅ **Category Filtering** - Filter posts by categories  
✅ **Pagination** - Handle large post lists efficiently  
✅ **Free Hosting** - Deploy to Vercel with free tier  
✅ **SEO Ready** - Meta tags, structured data  

---

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/wordpress-replacement.git
cd wordpress-replacement
```

### 2. Setup Python (Windows)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Python (Mac/Linux)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Create `.env` File
```bash
# Create .env with:
FLASK_ENV=development
API_KEY=your_secret_key_here
SECRET_KEY=your_secret_here
```

### 5. Run Locally
```bash
python app.py
# Visit http://localhost:5000
```

### 6. Deploy to Vercel
```bash
git add .
git commit -m "Deploy"
git push origin main
```

Then use Vercel dashboard to deploy.

---

## Architecture

### Backend (app.py)
- Flask REST API
- SQLite database
- API key authentication
- CORS enabled for frontend

### API Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/posts` | No | List all posts (paginated) |
| GET | `/api/posts/<id>` | No | Get single post |
| POST | `/api/posts` | Yes* | Create new post |
| GET | `/api/posts/search?q=...` | No | Search posts |
| DELETE | `/api/posts/<id>` | Yes* | Delete post |
| GET | `/api/stats` | No | Get statistics |

*Requires: `Authorization: Bearer YOUR_API_KEY`

### Frontend
- HTML5/CSS3/JavaScript
- Responsive grid layout
- Real-time search
- Category filtering
- Pagination controls

### Database Schema
```sql
CREATE TABLE posts (
  id INTEGER PRIMARY KEY,
  title TEXT,
  content TEXT,
  rumble_link TEXT,
  featured_image_id INTEGER,
  categories TEXT,  -- JSON: [24, 39, 100]
  metadata TEXT,    -- JSON: {keyword, description}
  created_at TIMESTAMP,
  source TEXT       -- 'automation' or 'manual'
)
```

---

## Integration with Automation

### Update Google Apps Script

Change the WordPress endpoint to your new API:

```javascript
// Old (WordPress)
const url = "https://thuyance.com/wp-json/wp/v2/posts";

// New (Your Website)
const url = "https://your-vercel-domain.vercel.app/api/posts";
```

### Send Data

```javascript
const payload = {
  title: "Post Title",
  content: "<p><iframe src='...'>",
  rumble_link: "https://rumble.com/embed/xxx/",
  categories: [24, 39, 100],
  featured_image_id: 1832,
  metadata: {
    rank_math_description: "...",
    focus_keyword: "..."
  }
};

const options = {
  method: "POST",
  headers: {
    "Authorization": "Bearer YOUR_API_KEY",  // From .env
    "Content-Type": "application/json"
  },
  payload: JSON.stringify(payload)
};

UrlFetchApp.fetch(url, options);
```

---

## Deployment Steps

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/wordpress-replacement.git
git push -u origin main
```

### 2. Create Vercel Account
Go to **vercel.com** and sign in with GitHub

### 3. Create New Project
1. Click "New Project"
2. Select your GitHub repository
3. Click "Import"

### 4. Add Environment Variables
1. Click "Environment Variables"
2. Add:
   - `API_KEY` = your secret key
   - `SECRET_KEY` = your flask secret
3. Click "Deploy"

### 5. Get Your URL
Vercel gives you a URL like:
`https://wordpress-replacement-abc123.vercel.app`

---

## File Structure

```
wordpress-replacement/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (local only)
├── .env.example          # Template for .env
├── .gitignore           # Git ignore patterns
├── vercel.json          # Vercel deployment config
├── api/
│   └── index.py         # Vercel entry point
├── templates/           # HTML templates
│   ├── base.html        # Base layout
│   ├── index.html       # Homepage
│   ├── post.html        # Post detail page
│   ├── admin.html       # Admin dashboard
│   └── search.html      # Search results
├── static/              # CSS and JavaScript
│   ├── style.css        # Styling
│   └── (script.js handled by templates)
├── database.db          # SQLite database (auto-created)
├── SETUP_GUIDE.md       # Detailed setup instructions
├── QUICK_START.md       # Quick start guide
└── README.md            # This file
```

---

## API Examples

### Create a Post
```bash
curl -X POST https://your-domain.vercel.app/api/posts \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Post",
    "content": "<p>Hello World</p>",
    "rumble_link": "https://rumble.com/embed/abc/",
    "categories": [24, 39],
    "featured_image_id": 100
  }'
```

### Get All Posts
```bash
curl https://your-domain.vercel.app/api/posts?page=1&limit=10
```

### Search Posts
```bash
curl "https://your-domain.vercel.app/api/posts/search?q=latest&limit=20"
```

### Get Single Post
```bash
curl https://your-domain.vercel.app/api/posts/1
```

### Delete Post
```bash
curl -X DELETE https://your-domain.vercel.app/api/posts/1 \
  -H "Authorization: Bearer your_api_key"
```

### Get Statistics
```bash
curl https://your-domain.vercel.app/api/stats
```

---

## Customization

### Change Website Title
In `templates/base.html`:
```html
<h1>📺 Your Site Name</h1>
```

### Change Colors
In `static/style.css`:
```css
--primary-color: #your-color;
--primary-dark: #darker-color;
```

### Add More Pages
1. Create new route in `app.py`:
```python
@app.route('/my-page')
def my_page():
    return render_template('my-page.html')
```

2. Create `templates/my-page.html`

3. Add link in `templates/base.html`

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `FLASK_ENV` | Flask mode | `development` or `production` |
| `FLASK_DEBUG` | Debug mode | `True` or `False` |
| `API_KEY` | Secret key for API | `mysecretkey123` |
| `SECRET_KEY` | Flask secret | `anotherkey456` |

**Never commit `.env` to Git!** It's in `.gitignore`.

---

## Troubleshooting

### "Module not found" Error
```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Port 5000 Already in Use
```bash
python app.py --port 5001
```

### Database Issues
```bash
# Delete database to reset
rm database.db

# Re-run Flask to create fresh database
python app.py
```

### API Key Invalid
- Check `.env` file exists
- Check `API_KEY` value matches
- Restart Flask after changing `.env`

---

## Performance Tips

1. **Database:** SQLite works great for <100k posts
2. **Images:** Use placeholder service or Cloudinary (free)
3. **Caching:** Add Redis for production (optional)
4. **CDN:** Vercel includes CDN automatically

---

## Security

- API key required for writes
- CORS enabled only for own domain
- Input validation on all endpoints
- HTTPS automatically enabled
- No hardcoded secrets in code

---

## Monitoring

### Vercel Dashboard
- View deployments
- Check runtime logs
- Monitor performance
- See error traces

### Local Testing
```bash
# View Flask debug logs
FLASK_DEBUG=True python app.py

# Check database
sqlite3 database.db "SELECT COUNT(*) FROM posts;"
```

---

## License

MIT - Feel free to use for any purpose

---

## Support

For issues:
1. Check `QUICK_START.md`
2. Check `SETUP_GUIDE.md`
3. Check Vercel logs
4. Check Flask console output

---

## Next Steps

- [ ] Add authentication to admin panel
- [ ] Add featured image upload
- [ ] Add email notifications
- [ ] Add analytics (Vercel Analytics)
- [ ] Add custom domain
- [ ] Add social media sharing
- [ ] Add comments system
- [ ] Add email subscriptions

---

Built with ❤️ using Flask and Vercel
