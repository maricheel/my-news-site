# Quick Start Guide - Run These Commands Exactly

## Step 1: Clone or Create Project (Choose One)

### Option A: Create from Scratch
```bash
mkdir wordpress-replacement
cd wordpress-replacement
```

### Option B: Clone (if you have the files)
```bash
git clone https://github.com/YOUR_USERNAME/wordpress-replacement.git
cd wordpress-replacement
```

---

## Step 2: Python Setup (Windows, Mac, or Linux)

### Windows
```bash
# Create virtual environment
python -m venv venv

# Activate it (you should see (venv) in terminal)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Mac/Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate it (you should see (venv) in terminal)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Create .env File (DO THIS!)

Create a file named `.env` in the project root:

```
FLASK_ENV=development
FLASK_DEBUG=True
API_KEY=mysecret12345abc
SECRET_KEY=myflasksecret678xyz
```

**IMPORTANT:** Change the values above to something random. Use https://randomkeygen.com/ to generate secure keys.

---

## Step 4: Run Locally

```bash
# Make sure (venv) is active in terminal

# Run Flask
python app.py

# You should see:
# Running on http://127.0.0.1:5000
```

**Visit in browser:** http://localhost:5000

---

## Step 5: Test the API

Open another terminal (keep Flask running) and run:

```bash
# Test GET all posts
curl http://localhost:5000/api/posts

# Test CREATE a post
curl -X POST http://localhost:5000/api/posts \
  -H "Authorization: Bearer mysecret12345abc" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Test\",\"content\":\"<p>Hello</p>\",\"rumble_link\":\"https://rumble.com/embed/test/\",\"categories\":[24],\"featured_image_id\":100}"
```

If you get a success response, it's working!

---

## Step 6: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Flask website"

# Create GitHub repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/wordpress-replacement.git
git branch -M main
git push -u origin main
```

---

## Step 7: Deploy to Vercel

### Using Web Interface (Easiest)

1. Go to **vercel.com** and sign in with GitHub
2. Click **"New Project"**
3. Select your `wordpress-replacement` repository
4. Click **"Import"**
5. **Add Environment Variables:**
   - Click "Environment Variables"
   - Add `API_KEY` = your_secret_api_key_from_env
   - Add `SECRET_KEY` = your_flask_secret_from_env
6. Click **"Deploy"**

Vercel will give you a URL like:
`https://wordpress-replacement-abc123.vercel.app`

---

## Step 8: Update Google Apps Script

In your Google Apps Script automation, change:

```javascript
// OLD (WordPress)
const url = "https://thuyance.com/wp-json/wp/v2/posts";

// NEW (Your Website)
const url = "https://wordpress-replacement-abc123.vercel.app/api/posts";
```

Replace `abc123` with your actual Vercel domain.

Also update the API key:
```javascript
headers: {
    "Authorization": "Bearer mysecret12345abc",  // Same as your .env API_KEY
    "Content-Type": "application/json"
}
```

---

## File Structure Check

Before deploying, verify you have:

```
wordpress-replacement/
├── app.py                    ✓ Backend Flask app
├── requirements.txt          ✓ Dependencies
├── .env                      ✓ Local env vars (DON'T commit)
├── .env.example              ✓ Template for .env
├── .gitignore                ✓ Git ignore
├── vercel.json               ✓ Deployment config
├── api/
│   └── index.py              ✓ Vercel entry point
├── templates/
│   ├── base.html             ✓ Base layout
│   ├── index.html            ✓ Homepage
│   ├── post.html             ✓ Post detail
│   ├── admin.html            ✓ Admin dashboard
│   └── search.html           ✓ Search
└── static/
    └── style.css             ✓ Styling
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
# Make sure (venv) is activated, then:
pip install -r requirements.txt
```

### "Address already in use" on port 5000
```bash
# Kill the process or use different port:
python app.py --port 5001
```

### "Cannot find .env file"
- Create `.env` file in the project root
- Don't use `.env.example` - create actual `.env`
- Never commit `.env` to Git (it's in `.gitignore`)

### "API key invalid" when pushing from automation
- Check Vercel environment variables match your API_KEY in `.env`
- After changing env vars, redeploy Vercel
- Verify you're using correct URL (with https://)

### Posts not showing on website
- Visit `/api/posts` directly to see if data exists
- Check browser console (F12) for JavaScript errors
- Check Vercel logs for backend errors

---

## Useful Commands

```bash
# Stop Flask
Ctrl + C

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Deactivate virtual environment
deactivate

# View all files in project
ls -la              # Mac/Linux
dir                 # Windows

# View database (if you install this)
pip install sqlite-browser
```

---

## After Deployment

1. **Test the website:** Visit your Vercel URL
2. **Test API:** Try `/api/posts` on your URL
3. **Send test post:** From Google Apps Script
4. **Check admin:** Visit `/admin`
5. **View logs:** In Vercel dashboard → Deployments → Runtime Logs

---

## Summary of URLs

| What | URL |
|------|-----|
| Local website | http://localhost:5000 |
| Local API | http://localhost:5000/api/posts |
| Live website | https://your-vercel-domain.vercel.app |
| Live API | https://your-vercel-domain.vercel.app/api/posts |
| Admin dashboard | https://your-vercel-domain.vercel.app/admin |

---

## Next Steps

After everything works:
1. Add custom domain in Vercel (optional)
2. Add featured images upload
3. Add admin authentication
4. Add email notifications
5. Add analytics tracking

Congratulations! You've built a custom website! 🚀
