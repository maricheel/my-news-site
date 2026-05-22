# msnow.click — Full Maintenance Guide

> **Read this first if you are new to this project.**  
> Everything you need to run, fix, and extend this website is in this document.

---

## Table of Contents

1. [What this website is](#1-what-this-website-is)
2. [Tech stack at a glance](#2-tech-stack-at-a-glance)
3. [File structure](#3-file-structure)
4. [Environment variables](#4-environment-variables)
5. [How to run locally](#5-how-to-run-locally)
6. [How deployment works (Vercel)](#6-how-deployment-works-vercel)
7. [Database](#7-database)
8. [All API endpoints](#8-all-api-endpoints)
9. [Automation — WordPress → site sync](#9-automation--wordpress--site-sync)
10. [Admin panel](#10-admin-panel)
11. [Premium / freemium system](#11-premium--freemium-system)
12. [User registration & approval flow](#12-user-registration--approval-flow)
13. [PWA (Android app)](#13-pwa-android-app)
14. [Common problems & fixes](#14-common-problems--fixes)
15. [How to add a new show](#15-how-to-add-a-new-show)
16. [Key contacts & credentials locations](#16-key-contacts--credentials-locations)

---

## 1. What this website is

**msnow.click** is a news video archive site. It shows daily political TV shows (Morning Joe, Rachel Maddow, Chris Hayes, etc.) as video cards. Videos are automatically pulled from a WordPress site (`topnewsshow.com`) that embeds Rumble video players.

**Business model:**
- Free users can watch ~20% of daily shows (random selection, stable all day)
- Premium users pay $9.99/month and get access to all shows
- Admin manually approves accounts after payment via WhatsApp or email

---

## 2. Tech stack at a glance

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 · Flask 2.3.3 |
| Hosting | Vercel (serverless, `@vercel/python`) |
| Database | Neon PostgreSQL (production) · SQLite (local dev) |
| DB driver | pg8000 (pure Python, no C deps — required for Vercel) |
| Frontend | React 18 SPA (CDN, no build step) · Babel standalone |
| CSS | Tailwind CSS (CDN) |
| Fonts | Geist · Instrument Serif · JetBrains Mono (Google Fonts) |
| Video | Rumble embed iframes |
| PWA | Web App Manifest + Service Worker |
| Automation | Python script triggered by cron-job.org |

> **Important:** There is NO build step. React JSX is transpiled in the browser by Babel CDN. Everything is one `index.html` file with inline JavaScript.

---

## 3. File structure

```
plan/
├── api/
│   └── index.py          ← ENTIRE backend (Flask app, all routes, DB logic)
├── templates/
│   ├── index.html        ← ENTIRE frontend (React SPA, 1300+ lines)
│   ├── admin.html        ← Admin dashboard (Vanilla JS)
│   └── login.html        ← Admin Google login page
├── static/
│   ├── images/
│   │   ├── favicon.png   ← Site icon (also used as PWA icon)
│   │   └── logo.png      ← Header logo
│   ├── manifest.json     ← PWA manifest
│   ├── sw.js             ← Service Worker (offline support)
│   └── style.css         ← (minimal, most styles are Tailwind inline)
├── auto/
│   └── automate_simple.py  ← WordPress → site automation script
├── vercel.json           ← Vercel deployment config + routing
├── requirements.txt      ← Python dependencies
├── .env                  ← Local dev secrets (never commit this)
└── MAINTENANCE.md        ← This file
```

---

## 4. Environment variables

Set these in **Vercel → Project → Settings → Environment Variables**.

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ | Flask session signing key. Use a long random string. |
| `API_KEY` | ✅ | Bearer token for the automation cron endpoint. |
| `DATABASE_URL` | ✅ | Neon PostgreSQL connection string (starts with `postgresql://`) |
| `GOOGLE_CLIENT_ID` | ✅ | Google OAuth client ID for admin login |
| `WORDPRESS_URL` | ❌ | WordPress source URL. Default: `https://topnewsshow.com` |

**For local development**, create a `.env` file in the project root:
```env
SECRET_KEY=any-random-string-here
API_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host/dbname
GOOGLE_CLIENT_ID=xxxxxx.apps.googleusercontent.com
WORDPRESS_URL=https://topnewsshow.com
```

---

## 5. How to run locally

```bash
# 1. Clone the repo
git clone https://github.com/maricheel/my-news-site.git
cd my-news-site

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (see section 4 above)

# 5. Run the Flask development server
python api/index.py
```

The site runs at `http://127.0.0.1:5000`.  
When running locally, it uses **SQLite** at `database.db` (auto-created on first run).  
On Vercel (production), it uses **PostgreSQL** via the `DATABASE_URL` env var.

---

## 6. How deployment works (Vercel)

Every `git push` to the `main` branch **automatically deploys** to `https://msnow.click`.

Vercel reads `vercel.json`:
```json
{
  "builds": [{ "src": "api/index.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "api/index.py" }]
}
```
This means **all routes** go to `api/index.py`. Flask handles them.

**Deploy time:** ~60–90 seconds after push.

**To check deployment status:** Go to `https://vercel.com` → your project → Deployments tab.

**To check function logs:** Vercel dashboard → Functions tab → click any invocation.

---

## 7. Database

### Production: Neon PostgreSQL
- Provider: [neon.tech](https://neon.tech) (free tier)
- Access: Neon dashboard → your project → connection string
- The connection string goes in the `DATABASE_URL` env var

### Tables

#### `posts` — video content
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Auto-increment primary key |
| title | TEXT | Show title (e.g. "Morning Joe – 5/21/26") |
| content | TEXT | Full HTML content from WordPress |
| rumble_link | TEXT | Rumble embed URL (e.g. `https://rumble.com/embed/abc123/`) |
| thumbnail_url | TEXT | Image URL from WordPress featured media |
| categories | TEXT | JSON array (e.g. `["Morning Joe"]`) |
| metadata | TEXT | JSON object — always contains `wp_post_id` |
| source | TEXT | Always `"automation"` |
| created_at | TIMESTAMP | When the post was added to our DB |

#### `settings` — key/value config
| Key | Value | Description |
|-----|-------|-------------|
| `premium_mode` | `"true"` / `"false"` | Whether premium mode is active |
| `admin_whatsapp` | phone number | Admin WhatsApp number for invoice requests |

#### `users` — registered users
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Auto-increment |
| email | TEXT | User email (unique) |
| password_hash | TEXT | Werkzeug hashed password |
| password_plain | TEXT | Plain text (for admin reference only) |
| status | TEXT | `"pending"` / `"approved"` / `"rejected"` |
| created_at | TIMESTAMP | Registration date |

### Running manual SQL queries
Connect via the Neon dashboard SQL editor, or use psql:
```bash
psql "postgresql://user:pass@host/dbname?sslmode=require"
```

---

## 8. All API endpoints

### Public endpoints (no auth required)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/posts` | List posts. Params: `page`, `limit`, `category`, `sort`, `search` |
| GET | `/api/posts/<id>` | Single post by ID |
| GET | `/api/posts/search?q=...` | Full-text search |
| GET | `/api/settings/premium` | Returns `{"premium": true/false}` |
| GET | `/api/settings/contact` | Returns admin WhatsApp + email |
| GET | `/api/stats` | Total post count + breakdown by source |
| POST | `/api/auth/register` | Register new user → status `pending` |
| POST | `/api/auth/user-login` | User login |
| POST | `/api/auth/user-logout` | User logout |
| GET | `/api/auth/user-status` | Current session user + status |

### Automation endpoint (requires `Authorization: Bearer API_KEY` header OR `?key=API_KEY`)

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/api/cron` | Fetch WP posts, publish new ones to DB |
| POST | `/api/posts` | Create a single post |
| DELETE | `/api/posts/<id>` | Delete a post |

### Admin endpoints (requires admin session via Google login)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/admin/users` | List all registered users |
| POST | `/api/admin/users/<id>/approve` | Approve a user |
| POST | `/api/admin/users/<id>/reject` | Reject a user |
| POST | `/api/admin/users/create` | Create a pre-approved user |
| POST | `/api/admin/settings` | Save settings (e.g. WhatsApp number) |
| POST | `/api/settings/premium` | Toggle premium mode on/off |

### Admin login flow (Google OAuth)
1. Go to `/auth/login`
2. Click "Sign in with Google"
3. Only the email `hicham1elbanaji@gmail.com` is accepted
4. Session is stored in a signed Flask cookie (30-day expiry)

---

## 9. Automation — WordPress → site sync

### How it works
1. **cron-job.org** (free external cron) calls `POST https://msnow.click/api/cron?key=API_KEY` every 10 minutes
2. The `/api/cron` endpoint fetches the 10 latest posts from `https://topnewsshow.com/wp-json/wp/v2/posts?per_page=10&order=desc&_embed`
3. For each post, it checks if `metadata.wp_post_id` already exists in our database (direct DB query — no HTTP roundtrips)
4. New posts are parsed (title, Rumble embed URL, thumbnail, categories) and inserted
5. Returns `{"published": N, "skipped": N, "failed": N}`

### Show detection
Posts are matched to shows by keywords in the title. See `_CRON_SHOW_KEYWORDS` in `api/index.py`. If no known show is detected, the post is skipped.

Known shows:
- Morning Joe
- Chris Jansing Reports
- Katy Tur Reports
- Deadline: White House
- The Beat With Ari Melber
- The Weeknight
- All In with Chris Hayes
- The Rachel Maddow Show
- The Briefing with Jen Psaki
- The Last Word with Lawrence O'Donnell
- The 11th Hour with Stephanie Ruhle
- Velshi
- Alex Witt Reports
- PoliticsNation with Al Sharpton
- The Weekend

### cron-job.org setup
1. Go to [cron-job.org](https://cron-job.org) → sign in → **Create cronjob**
2. URL: `https://msnow.click/api/cron?key=YOUR_API_KEY`
3. Schedule: every **10 minutes**
4. Request method: `GET` (or `POST`)
5. Save + Enable

### Running the automation manually
```bash
cd auto
pip install requests python-dotenv
python automate_simple.py
```
Or trigger via cron-job.org → Execute now button.

### WordPress source
- URL: `https://topnewsshow.com`
- API used: WordPress REST API v2
- No authentication needed (posts are public)

---

## 10. Admin panel

Access at: `https://msnow.click/admin`  
Login required: Google account `hicham1elbanaji@gmail.com`

### What you can do in the admin panel:

**Premium toggle**
- Switch the entire site between free and premium mode
- When premium is ON: non-approved users can only watch ~20% of daily shows

**WhatsApp number**
- Set the admin phone number used in the invoice request button
- Format: international, no spaces (e.g. `12125551234`)

**Users table**
- See all registered users with email, password (plain), status, and registration date
- Approve → user gets full access
- Reject → user sees "rejected" message

---

## 11. Premium / freemium system

### Modes
- **Premium OFF**: everyone can watch everything for free
- **Premium ON**: access is gated

### Access levels (when premium is ON)
| User type | Access |
|-----------|--------|
| Not logged in | Free 20% of today's shows |
| Logged in, status = `pending` | Free 20% of today's shows |
| Logged in, status = `rejected` | Free 20% of today's shows |
| Logged in, status = `approved` | All shows, full access |

### Free 20% selection
- Computed using a **date-seeded shuffle** (LCG algorithm)
- Seed = `YYYYMMDD` → same result all day, changes at midnight
- Refreshing the page does NOT change which shows are free
- Located in `index.html` → `useFreeIds()` function

---

## 12. User registration & approval flow

1. User clicks **Sign In** → modal opens
2. User fills email + password → clicks **"Create account for $9.99/month"**
3. Account created with `status = 'pending'`
4. Modal shows **pending screen** with two buttons:
   - **WhatsApp** → opens WhatsApp with pre-filled message: `"Hello, I want the invoice please. My email is user@example.com"`
   - **Email** → opens mail client with same message
5. Admin receives the message, processes payment
6. Admin goes to `/admin` → Users table → clicks **Approve**
7. User clicks **"Pending"** badge in header → app re-fetches status → badge turns into full access

### Manually creating an approved account
In the admin panel, or via API:
```bash
curl -X POST https://msnow.click/api/admin/users/create \
  -H "Content-Type: application/json" \
  -H "Cookie: session=ADMIN_SESSION_COOKIE" \
  -d '{"email": "user@example.com", "password": "pass123"}'
```

---

## 13. PWA (Android app)

The site is a Progressive Web App. Users can install it on Android as a home screen app:

1. Open `https://msnow.click` in Chrome on Android
2. Tap the three-dot menu → **"Add to Home Screen"**
3. Tap **Install**

**PWA files:**
- `static/manifest.json` — app name, colors, icons
- `static/sw.js` — service worker (offline caching strategy)

**Service worker behavior:**
- API routes (`/api/`, `/auth/`) → always network, never cached
- Everything else → network first, fall back to cache
- Pre-caches: `/`, favicon, logo on install

---

## 14. Common problems & fixes

### Site shows old content after a push
Vercel deployment takes ~90 seconds. Wait and hard-refresh (Ctrl+Shift+R).

### New WordPress posts not appearing
1. Check cron-job.org → last execution status should be 200
2. Check the response body: `{"published": 0, "skipped": 10, ...}` — if all skipped, the posts might not match any known show keyword
3. Go to `https://topnewsshow.com` and check the post titles — add new keywords to `_CRON_SHOW_KEYWORDS` in `api/index.py` if needed

### Admin login stopped working
- Check Google OAuth credentials are still valid at [console.cloud.google.com](https://console.cloud.google.com)
- Make sure `GOOGLE_CLIENT_ID` env var in Vercel matches your OAuth client
- Make sure `hicham1elbanaji@gmail.com` is the account you're logging in with

### Database errors after schema change
Postgres uses `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` to safely add columns.  
SQLite uses `try/except` around ALTER TABLE.  
Never use plain `ALTER TABLE` without `IF NOT EXISTS` on Postgres — it will abort the transaction.

### 500 errors on Vercel
- Go to Vercel → Functions tab → click the failed invocation to see the full traceback
- Most common cause: missing environment variable

### Users can't log in (password rejected)
Passwords are hashed with Werkzeug's `generate_password_hash`. Plain text is stored separately in `password_plain` for admin reference only. Do not edit `password_hash` manually.

### Video doesn't play
- Videos are Rumble embeds. If Rumble is down, videos won't play — nothing to fix on our side.
- Check the `rumble_link` column in the DB for that post.

### Free 20% changes unexpectedly
It should not — it's seeded by today's date. If it seems to change:
- Check the browser clock
- The seed formula is: `YYYYMMDD` as integer → LCG shuffle of all video IDs

---

## 15. How to add a new show

**Step 1 — Add show keyword** in `api/index.py`, find `_CRON_SHOW_KEYWORDS` and add:
```python
('keyword from title', 'Official Show Name'),
```

**Step 2 — Add the same keyword** in `auto/automate_simple.py`, find `SHOW_KEYWORDS`:
```python
('keyword from title', 'Official Show Name'),
```

**Step 3 — Add host mapping** in `templates/index.html`, find `const HOSTS = {`:
```javascript
'Official Show Name': 'Host Full Name',
```

**Step 4** — Push to git. Done.

---

## 16. Key contacts & credentials locations

| Item | Location |
|------|----------|
| Vercel project | vercel.com → login with project owner account |
| Neon database | neon.tech → login to see connection string |
| Google OAuth client | console.cloud.google.com |
| cron-job.org account | cron-job.org → manages the 10-min automation trigger |
| WordPress source | topnewsshow.com (read-only, no credentials needed) |
| GitHub repo | github.com/maricheel/my-news-site |
| Live site | https://msnow.click |
| Admin panel | https://msnow.click/admin |

### To change the admin email
In `api/index.py`, line:
```python
ALLOWED_EMAIL = 'hicham1elbanaji@gmail.com'
```
Change it to the new email. Push to git.

---

*Last updated: May 2026*
