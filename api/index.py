from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect
import json, os, traceback, re, html as _html, requests as http_req
from functools import wraps
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# app must be the very first assignment — Vercel static check
app = Flask(__name__)

load_dotenv()
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.template_folder = os.path.join(_base_dir, 'templates')
app.static_folder   = os.path.join(_base_dir, 'static')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-secret')
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 30  # 30 days
API_KEY          = os.getenv('API_KEY', 'change-this-key')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
ALLOWED_EMAIL    = 'hicham1elbanaji@gmail.com'

# ── Database ──────────────────────────────────────────────────────────────────
_raw_db_url = (os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
               or os.getenv('POSTGRES_PRISMA_URL') or os.getenv('POSTGRES_URL_NON_POOLING'))
USE_POSTGRES = bool(_raw_db_url)
PH = '%s' if USE_POSTGRES else '?'
_sqlite_path = '/tmp/database.db' if os.getenv('VERCEL') else os.path.join(_base_dir, 'database.db')


def get_db():
    if USE_POSTGRES:
        import pg8000.dbapi, ssl
        from urllib.parse import urlparse
        u = urlparse(_raw_db_url)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return pg8000.dbapi.connect(
            host=u.hostname, port=u.port or 5432,
            user=u.username, password=u.password,
            database=u.path.lstrip('/').split('?')[0],
            ssl_context=ctx,
        )
    else:
        import sqlite3
        conn = sqlite3.connect(_sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn


def get_cursor(conn):  return conn.cursor()


def fetchall(cursor):
    if USE_POSTGRES:
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, r)) for r in cursor.fetchall()]
    return [dict(r) for r in cursor.fetchall()]


def fetchone(cursor):
    if USE_POSTGRES:
        if not cursor.description: return None
        cols = [d[0] for d in cursor.description]
        row  = cursor.fetchone()
        return dict(zip(cols, row)) if row else None
    row = cursor.fetchone()
    return dict(row) if row else None


def init_db():
    conn = get_db(); c = get_cursor(conn)
    if USE_POSTGRES:
        c.execute('''CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL,
            rumble_link TEXT, featured_image_id INTEGER, categories TEXT,
            metadata TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'automation', thumbnail_url TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, password_plain TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        # IF NOT EXISTS avoids aborting the Postgres transaction on duplicate columns
        c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending'")
        c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_plain TEXT DEFAULT ''")
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL,
            rumble_link TEXT, featured_image_id INTEGER, categories TEXT,
            metadata TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'automation', thumbnail_url TEXT)''')
        try: c.execute('ALTER TABLE posts ADD COLUMN thumbnail_url TEXT')
        except Exception: pass
        c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, password_plain TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        try: c.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'pending'")
        except Exception: pass
        try: c.execute("ALTER TABLE users ADD COLUMN password_plain TEXT DEFAULT ''")
        except Exception: pass
    conn.commit(); conn.close()


# ── Settings helpers ──────────────────────────────────────────────────────────
def get_setting(key, default=''):
    try:
        conn = get_db(); c = get_cursor(conn)
        c.execute(f'SELECT value FROM settings WHERE key={PH}', (key,))
        row = fetchone(c); conn.close()
        return row['value'] if row else default
    except Exception: return default

def set_setting(key, value):
    conn = get_db(); c = get_cursor(conn)
    if USE_POSTGRES:
        c.execute('INSERT INTO settings(key,value) VALUES(%s,%s) ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value', (key, value))
    else:
        c.execute('INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)', (key, value))
    conn.commit(); conn.close()


def row_to_dict(row):
    if row is None: return None
    return {
        'id': row['id'], 'title': row['title'], 'content': row['content'],
        'rumble_link': row['rumble_link'], 'featured_image_id': row['featured_image_id'],
        'categories':  json.loads(row['categories']) if row['categories'] else [],
        'metadata':    json.loads(row['metadata'])   if row['metadata']   else {},
        'created_at':  str(row['created_at']), 'source': row['source'],
        'thumbnail_url': row['thumbnail_url'],
    }


# ── Google auth helpers ───────────────────────────────────────────────────────
def verify_google_token(token):
    """Call Google's tokeninfo endpoint to validate an ID token."""
    try:
        r = http_req.get(
            'https://oauth2.googleapis.com/tokeninfo',
            params={'id_token': token}, timeout=10
        )
        if r.status_code != 200:
            return None
        info = r.json()
        if str(info.get('email_verified')).lower() != 'true':
            return None
        if GOOGLE_CLIENT_ID and info.get('aud') != GOOGLE_CLIENT_ID:
            return None
        return info.get('email')
    except Exception:
        return None


def require_admin(f):
    """Redirect to login page (or return 401 for API calls) if not authenticated as admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('admin_email') != ALLOWED_EMAIL:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Admin authentication required'}), 401
            return redirect('/auth/login')
        return f(*args, **kwargs)
    return decorated


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth  = request.headers.get('Authorization', '')
        parts = auth.split()
        if len(parts) != 2 or parts[0] != 'Bearer' or parts[1] != API_KEY:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated


# ── CORS + Security + Cache headers ───────────────────────────────────────────
@app.after_request
def _headers(response):
    # CORS
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options']        = 'SAMEORIGIN'
    response.headers['X-XSS-Protection']       = '1; mode=block'
    response.headers['Referrer-Policy']        = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy']     = 'camera=(), microphone=(), geolocation=()'
    # Cache static assets aggressively; API + HTML never cached
    path = request.path
    if path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    elif path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    else:
        response.headers['Cache-Control'] = 'public, max-age=60, stale-while-revalidate=300'
    return response


# ── Global error handler — prevents FUNCTION_INVOCATION_FAILED ───────────────
@app.errorhandler(Exception)
def _global_error(e):
    return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


# ── robots.txt ────────────────────────────────────────────────────────────────
@app.route('/robots.txt')
def robots_txt():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        "Disallow: /auth/\n"
        "Disallow: /api/\n"
        "\n"
        "Sitemap: https://msnow.click/sitemap.xml\n"
    )
    return app.response_class(body, mimetype='text/plain')


# ── sitemap.xml ───────────────────────────────────────────────────────────────
@app.route('/sitemap.xml')
def sitemap_xml():
    from datetime import timezone
    try:
        conn = get_db(); c = get_cursor(conn)
        c.execute('SELECT id, created_at FROM posts ORDER BY created_at DESC LIMIT 200')
        rows = fetchall(c); conn.close()
    except Exception:
        rows = []
    urls = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    # Homepage
    urls.append('<url><loc>https://msnow.click/</loc>'
                '<changefreq>hourly</changefreq><priority>1.0</priority></url>')
    for row in rows:
        dt = str(row.get('created_at',''))[:10]
        urls.append(f'<url>'
                    f'<loc>https://msnow.click/post/{row["id"]}</loc>'
                    f'<lastmod>{dt}</lastmod>'
                    f'<changefreq>never</changefreq>'
                    f'<priority>0.8</priority>'
                    f'</url>')
    urls.append('</urlset>')
    return app.response_class('\n'.join(urls), mimetype='application/xml')


# ── Page routes ───────────────────────────────────────────────────────────────
@app.route('/')
def index():
    # index.html is a React SPA — serve raw, skip Jinja2 (JSX {{ }} breaks Jinja)
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    return render_template('post.html', post_id=post_id)

@app.route('/admin')
@require_admin
def admin_dashboard():
    return render_template('admin.html')

@app.route('/auth/login')
def auth_login():
    if session.get('admin_email') == ALLOWED_EMAIL:
        return redirect('/admin')
    return render_template('login.html', google_client_id=GOOGLE_CLIENT_ID)

@app.route('/api/auth/verify', methods=['POST'])
def auth_verify():
    token = (request.get_json() or {}).get('token', '')
    email = verify_google_token(token)
    if email == ALLOWED_EMAIL:
        session.permanent = True
        session['admin_email'] = email
        return jsonify({'ok': True})
    return jsonify({'error': 'Access denied. This account is not authorised.'}), 403

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    session.clear()
    return jsonify({'ok': True})


# ── API: premium toggle ───────────────────────────────────────────────────
@app.route('/api/settings/premium', methods=['GET'])
def get_premium():
    return jsonify({'premium': get_setting('premium_mode') == 'true'})

@app.route('/api/settings/premium', methods=['POST'])
@require_admin
def set_premium():
    data = request.get_json() or {}
    enabled = bool(data.get('enabled', False))
    set_setting('premium_mode', 'true' if enabled else 'false')
    return jsonify({'premium': enabled})


# ── API: user registration / login / logout / status ──────────────────────
@app.route('/api/auth/register', methods=['POST'])
def user_register():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    try:
        conn = get_db(); c = get_cursor(conn)
        c.execute(f'SELECT id FROM users WHERE email={PH}', (email,))
        if fetchone(c):
            conn.close()
            return jsonify({'error': 'An account with this email already exists'}), 409
        pw_hash = generate_password_hash(password)
        c.execute(f'INSERT INTO users (email, password_hash, password_plain) VALUES ({PH},{PH},{PH})', (email, pw_hash, password))
        conn.commit(); conn.close()
        session.permanent = True
        session['user_email'] = email
        return jsonify({'ok': True, 'email': email, 'status': 'pending'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/user-login', methods=['POST'])
def user_login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    try:
        conn = get_db(); c = get_cursor(conn)
        c.execute(f'SELECT password_hash, status FROM users WHERE email={PH}', (email,))
        row = fetchone(c); conn.close()
        if not row or not check_password_hash(row['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        session.permanent = True
        session['user_email'] = email
        status = row.get('status') or 'pending'
        return jsonify({'ok': True, 'email': email, 'status': status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/user-logout', methods=['POST'])
def user_logout():
    session.pop('user_email', None)
    return jsonify({'ok': True})

@app.route('/api/auth/user-status', methods=['GET'])
def user_status():
    email = session.get('user_email')
    if not email:
        return jsonify({'logged_in': False, 'email': '', 'status': ''})
    try:
        conn = get_db(); c = get_cursor(conn)
        c.execute(f'SELECT status FROM users WHERE email={PH}', (email,))
        row = fetchone(c); conn.close()
        status = (row.get('status') or 'pending') if row else 'pending'
        return jsonify({'logged_in': True, 'email': email, 'status': status})
    except Exception:
        return jsonify({'logged_in': True, 'email': email, 'status': 'pending'})

# ── API: contact info (public) ────────────────────────────────────────────
@app.route('/api/settings/contact', methods=['GET'])
def get_contact():
    return jsonify({
        'whatsapp': get_setting('admin_whatsapp', ''),
        'email': ALLOWED_EMAIL,
    })

# ── API: admin — update settings ──────────────────────────────────────────
@app.route('/api/admin/settings', methods=['POST'])
@require_admin
def update_admin_settings():
    data = request.get_json() or {}
    allowed_keys = {'admin_whatsapp'}
    for key, val in data.items():
        if key in allowed_keys:
            set_setting(key, str(val).strip())
    return jsonify({'ok': True})

# ── API: admin — user management ──────────────────────────────────────────
@app.route('/api/admin/users', methods=['GET'])
@require_admin
def admin_list_users():
    try:
        conn = get_db(); c = get_cursor(conn)
        c.execute('SELECT id, email, password_plain, status, created_at FROM users ORDER BY created_at DESC')
        rows = fetchall(c); conn.close()
        return jsonify({'users': [dict(r) for r in rows]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/approve', methods=['POST'])
@require_admin
def admin_approve_user(user_id):
    try:
        conn = get_db(); c = get_cursor(conn)
        c.execute(f"UPDATE users SET status='approved' WHERE id={PH}", (user_id,))
        conn.commit(); conn.close()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/reject', methods=['POST'])
@require_admin
def admin_reject_user(user_id):
    try:
        conn = get_db(); c = get_cursor(conn)
        c.execute(f"UPDATE users SET status='rejected' WHERE id={PH}", (user_id,))
        conn.commit(); conn.close()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/create', methods=['POST'])
@require_admin
def admin_create_user():
    """Admin manually creates an approved account after payment."""
    data = request.get_json() or {}
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    try:
        pw_hash = generate_password_hash(password)
        conn = get_db(); c = get_cursor(conn)
        c.execute(f'SELECT id FROM users WHERE email={PH}', (email,))
        if fetchone(c):
            # Update existing (e.g. pending) user → approved + new password
            c.execute(f"UPDATE users SET status='approved', password_hash={PH}, password_plain={PH} WHERE email={PH}",
                      (pw_hash, password, email))
        else:
            c.execute(f"INSERT INTO users (email, password_hash, password_plain, status) VALUES ({PH},{PH},{PH},'approved')",
                      (email, pw_hash, password))
        conn.commit(); conn.close()
        return jsonify({'ok': True, 'email': email})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search')
def search():
    return render_template('search.html', query=request.args.get('q', ''))


# ── API: list posts ───────────────────────────────────────────────────────────
@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        page=int(request.args.get('page',1)); limit=int(request.args.get('limit',12))
        category=request.args.get('category','').strip(); sort=request.args.get('sort','newest')
        offset=(page-1)*limit; like_op='ILIKE' if USE_POSTGRES else 'LIKE'
        conn=get_db(); c=get_cursor(conn)
        where=f'WHERE categories {like_op} {PH}' if category else ''
        params=[f'%{category}%'] if category else []
        order='ASC' if sort=='oldest' else 'DESC'
        c.execute(f'SELECT * FROM posts {where} ORDER BY created_at {order} LIMIT {PH} OFFSET {PH}',params+[limit,offset])
        rows=fetchall(c)
        c.execute(f'SELECT COUNT(*) FROM posts {where}',params)
        total=list(fetchone(c).values())[0]; conn.close()
        return jsonify({'posts':[row_to_dict(r) for r in rows],'total':total,'page':page,'limit':limit,'pages':max(1,(total+limit-1)//limit)}),200
    except Exception as e: return jsonify({'error':str(e)}),500


# ── API: single post ──────────────────────────────────────────────────────────
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        conn=get_db(); c=get_cursor(conn)
        c.execute(f'SELECT * FROM posts WHERE id={PH}',(post_id,))
        row=fetchone(c); conn.close()
        if not row: return jsonify({'error':'Post not found'}),404
        return jsonify(row_to_dict(row)),200
    except Exception as e: return jsonify({'error':str(e)}),500


# ── API: create post ──────────────────────────────────────────────────────────
@app.route('/api/posts', methods=['POST'])
@require_api_key
def create_post():
    try:
        data=request.get_json()
        if not data.get('title') or not data.get('content'):
            return jsonify({'error':'title and content are required'}),400
        title=data['title']; content=data['content']
        rumble_link=data.get('rumble_link',''); featured_image_id=data.get('featured_image_id')
        categories=json.dumps(data.get('categories',[])); metadata=json.dumps(data.get('metadata',{}))
        source=data.get('source','automation'); thumbnail_url=data.get('thumbnail_url','')
        conn=get_db(); c=get_cursor(conn)
        if USE_POSTGRES:
            c.execute('INSERT INTO posts (title,content,rumble_link,featured_image_id,categories,metadata,source,thumbnail_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id',
                      (title,content,rumble_link,featured_image_id,categories,metadata,source,thumbnail_url))
            post_id=fetchone(c)['id']
        else:
            c.execute('INSERT INTO posts (title,content,rumble_link,featured_image_id,categories,metadata,source,thumbnail_url) VALUES (?,?,?,?,?,?,?,?)',
                      (title,content,rumble_link,featured_image_id,categories,metadata,source,thumbnail_url))
            post_id=c.lastrowid
        conn.commit(); conn.close()
        return jsonify({'id':post_id,'message':'Post created successfully'}),201
    except Exception as e: return jsonify({'error':str(e)}),500


# ── API: search posts ─────────────────────────────────────────────────────────
@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    try:
        q=request.args.get('q','').strip(); limit=int(request.args.get('limit',24))
        if len(q)<2: return jsonify({'error':'Search term must be at least 2 characters'}),400
        like_op='ILIKE' if USE_POSTGRES else 'LIKE'; term=f'%{q}%'
        conn=get_db(); c=get_cursor(conn)
        c.execute(f'SELECT * FROM posts WHERE title {like_op} {PH} OR content {like_op} {PH} ORDER BY created_at DESC LIMIT {PH}',(term,term,limit))
        rows=fetchall(c); conn.close()
        return jsonify({'posts':[row_to_dict(r) for r in rows],'count':len(rows),'query':q}),200
    except Exception as e: return jsonify({'error':str(e)}),500


# ── API: delete post ──────────────────────────────────────────────────────────
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@require_api_key
def delete_post(post_id):
    try:
        conn=get_db(); c=get_cursor(conn)
        c.execute(f'SELECT id FROM posts WHERE id={PH}',(post_id,))
        if not fetchone(c): conn.close(); return jsonify({'error':'Post not found'}),404
        c.execute(f'DELETE FROM posts WHERE id={PH}',(post_id,))
        conn.commit(); conn.close()
        return jsonify({'message':'Post deleted'}),200
    except Exception as e: return jsonify({'error':str(e)}),500


# ── API: stats ────────────────────────────────────────────────────────────────
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn=get_db(); c=get_cursor(conn)
        c.execute('SELECT COUNT(*) FROM posts')
        total=list(fetchone(c).values())[0]
        c.execute('SELECT source,COUNT(*) as cnt FROM posts GROUP BY source')
        sources={r['source']:r['cnt'] for r in fetchall(c)}
        c.execute('SELECT created_at FROM posts ORDER BY created_at DESC LIMIT 1')
        last=fetchone(c); conn.close()
        return jsonify({'total_posts':total,'by_source':sources,'last_post':str(last['created_at']) if last else None}),200
    except Exception as e: return jsonify({'error':str(e)}),500


# ── Cron: WordPress → site sync ───────────────────────────────────────────────
_CRON_SHOW_KEYWORDS = [
    ('morning joe','Morning Joe'),('jansing','Chris Jansing Reports'),
    ('katy tur','Katy Tur Reports'),('deadline','Deadline: White House'),
    ('ari melber','The Beat With Ari Melber'),('the beat','The Beat With Ari Melber'),
    ('weeknight','The Weeknight'),('all in','All In with Chris Hayes'),
    ('chris hayes','All In with Chris Hayes'),('maddow','The Rachel Maddow Show'),
    ('rachel maddow','The Rachel Maddow Show'),('jen psaki','The Briefing with Jen Psaki'),
    ('briefing','The Briefing with Jen Psaki'),
    ('lawrence',"The Last Word with Lawrence O'Donnell"),
    ('last word',"The Last Word with Lawrence O'Donnell"),
    ('11th hour','The 11th Hour with Stephanie Ruhle'),
    ('stephanie ruhle','The 11th Hour with Stephanie Ruhle'),
    ('velshi','Velshi'),('alex witt','Alex Witt Reports'),
    ('al sharpton','PoliticsNation with Al Sharpton'),
    ('politicsnation','PoliticsNation with Al Sharpton'),('the weekend','The Weekend'),
]
_CRON_KNOWN_SHOWS = {v for _,v in _CRON_SHOW_KEYWORDS}

def _cron_detect_show(title):
    t = title.lower()
    for kw, show in _CRON_SHOW_KEYWORDS:
        if kw in t: return show
    return None

def _cron_clean_cats(raw, title):
    good = [c for c in raw if c and not c.strip().isdigit() and c.upper() != 'UNCATEGORIZED']
    show = _cron_detect_show(title)
    if show and (not good or good[0] not in _CRON_KNOWN_SHOWS):
        return [show]
    return good if good else ([show] if show else [])

def _cron_load_existing_ids(conn):
    """
    Load ALL known WordPress post IDs from the DB into a Python set.
    One query up-front — avoids per-post queries and silent JSONB failures.
    Also loads titles for posts that may have been added before wp_post_id tracking.
    """
    existing_wp_ids = set()
    existing_titles = set()
    c = get_cursor(conn)
    try:
        if USE_POSTGRES:
            c.execute("SELECT metadata, title FROM posts WHERE metadata IS NOT NULL AND metadata != ''")
        else:
            c.execute("SELECT metadata, title FROM posts WHERE metadata IS NOT NULL AND metadata != ''")
        for row in fetchall(c):
            existing_titles.add((row.get('title') or '').strip().lower())
            try:
                m = json.loads(row.get('metadata') or '{}')
                wp_id = m.get('wp_post_id')
                if wp_id is not None:
                    existing_wp_ids.add(int(wp_id))
            except Exception:
                pass
    except Exception as e:
        print(f'[CRON] Warning loading existing IDs: {e}')
    return existing_wp_ids, existing_titles

def _cron_parse_wp_post(raw, existing_wp_ids, existing_titles):
    """Parse one WP post dict. Returns insert-ready dict or None if skip."""
    wp_id = raw['id']

    # Skip if already in DB by WP post ID
    if wp_id in existing_wp_ids:
        return None

    title = _html.unescape(raw['title']['rendered']).strip()

    # Skip if already in DB by title (safety net for legacy posts without wp_post_id)
    if title.lower() in existing_titles:
        print(f'[CRON] Skip #{wp_id} — title already exists: {title[:60]}')
        return None

    content = raw['content']['rendered']

    # Rumble embed
    rumble_link = ''
    m = re.search(r'https://rumble\.com/embed/([a-zA-Z0-9]+)', content)
    if m: rumble_link = f'https://rumble.com/embed/{m.group(1)}/'

    # Thumbnail
    thumbnail_url = ''
    try:
        media = raw['_embedded']['wp:featuredmedia'][0]
        sizes = media.get('media_details', {}).get('sizes', {})
        thumbnail_url = (
            sizes.get('medium_large', {}).get('source_url') or
            sizes.get('large',        {}).get('source_url') or
            sizes.get('medium',       {}).get('source_url') or
            media.get('source_url', '')
        )
    except Exception: pass

    # Categories
    raw_cats = []
    try:
        for term in raw['_embedded']['wp:term'][0]:
            if term.get('taxonomy') == 'category':
                raw_cats.append(_html.unescape(term.get('name', '')))
    except Exception: pass
    cats = _cron_clean_cats(raw_cats, title)

    if not cats or cats[0] not in _CRON_KNOWN_SHOWS:
        print(f'[CRON] Skip #{wp_id} — unrecognised show ({cats}) | {title[:60]}')
        return None

    excerpt = re.sub(r'<[^>]+>', '', raw.get('excerpt', {}).get('rendered', '')).strip()
    print(f'[CRON] New post #{wp_id}: {title[:70]}')
    return {
        'title': title, 'content': content,
        'rumble_link': rumble_link, 'thumbnail_url': thumbnail_url,
        'featured_image_id': raw.get('featured_media', 0),
        'categories': json.dumps(cats), 'source': 'automation',
        'metadata': json.dumps({'wp_post_id': wp_id,
                                'rank_math_description': excerpt,
                                'focus_keyword': cats[0]}),
    }

def _cron_insert_post(conn, p):
    c = get_cursor(conn)
    if USE_POSTGRES:
        c.execute(
            'INSERT INTO posts (title,content,rumble_link,featured_image_id,categories,metadata,source,thumbnail_url) '
            'VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id',
            (p['title'],p['content'],p['rumble_link'],p['featured_image_id'],
             p['categories'],p['metadata'],p['source'],p['thumbnail_url'])
        )
        return fetchone(c)['id']
    else:
        c.execute(
            'INSERT INTO posts (title,content,rumble_link,featured_image_id,categories,metadata,source,thumbnail_url) '
            'VALUES (?,?,?,?,?,?,?,?)',
            (p['title'],p['content'],p['rumble_link'],p['featured_image_id'],
             p['categories'],p['metadata'],p['source'],p['thumbnail_url'])
        )
        return c.lastrowid

@app.route('/api/cron', methods=['GET','POST'])
def run_cron():
    # Accept auth via Bearer header OR ?key= query param
    api_key = API_KEY
    auth  = request.headers.get('Authorization', '')
    parts = auth.split()
    key_from_header = parts[1] if len(parts) == 2 and parts[0] == 'Bearer' else ''
    key_from_query  = request.args.get('key', '')
    if key_from_header != api_key and key_from_query != api_key:
        return jsonify({'error': 'Unauthorized'}), 401

    # WORDPRESS_URL: env var first, then hardcoded fallback
    wp_url = (os.getenv('WORDPRESS_URL') or 'https://topnewsshow.com').rstrip('/')

    try:
        resp = http_req.get(
            f'{wp_url}/wp-json/wp/v2/posts',
            params={'per_page': 10, 'order': 'desc', '_embed': '1'},
            timeout=20
        )
        if resp.status_code != 200:
            return jsonify({'error': f'WordPress returned {resp.status_code}', 'wp_url': wp_url}), 502
        raw_posts = resp.json()
    except Exception as e:
        return jsonify({'error': f'WordPress fetch failed: {str(e)}', 'wp_url': wp_url}), 502

    # Oldest first so timeline stays correct
    raw_posts = list(reversed(raw_posts))

    try:
        conn = get_db()
    except Exception as e:
        return jsonify({'error': f'DB connection failed: {str(e)}'}), 500

    # Load ALL existing WP IDs + titles in ONE query — no per-post DB calls
    existing_wp_ids, existing_titles = _cron_load_existing_ids(conn)
    print(f'[CRON] DB has {len(existing_wp_ids)} tracked WP IDs, {len(existing_titles)} titles')

    published = 0; skipped = 0; failed = 0
    errors = []
    try:
        for raw in raw_posts:
            try:
                p = _cron_parse_wp_post(raw, existing_wp_ids, existing_titles)
                if p is None:
                    skipped += 1
                    continue
                _cron_insert_post(conn, p)
                conn.commit()
                # Add to sets so next post in same run won't duplicate
                existing_wp_ids.add(raw['id'])
                existing_titles.add(p['title'].lower())
                published += 1
            except Exception as e:
                err = f'Post #{raw.get("id","?")} failed: {str(e)}'
                print(f'[CRON] {err}')
                errors.append(err)
                failed += 1
    finally:
        conn.close()

    return jsonify({'published': published, 'skipped': skipped, 'failed': failed,
                    'wp_url': wp_url, 'errors': errors}), 200


# ── Lazy DB init ──────────────────────────────────────────────────────────────
_db_ready = False

@app.before_request
def _ensure_db():
    global _db_ready
    if not _db_ready:
        try:
            init_db()
            _db_ready = True
        except BaseException as e:
            print(f'[WARN] init_db: {e}')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
