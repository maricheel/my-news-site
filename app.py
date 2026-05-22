from flask import Flask, render_template, request, jsonify
import json
import os
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

_base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(_base_dir, 'templates'),
    static_folder=os.path.join(_base_dir, 'static'),
)

@app.after_request
def _cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-secret')
API_KEY = os.getenv('API_KEY', 'change-this-key')

# ── Database backend selection ──────────────────────────────────────────────
_raw_db_url  = (os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
                or os.getenv('POSTGRES_PRISMA_URL') or os.getenv('POSTGRES_URL_NON_POOLING'))
USE_POSTGRES = bool(_raw_db_url)
PH = '%s' if USE_POSTGRES else '?'

# SQLite path (only used when not on Postgres)
_sqlite_path = '/tmp/database.db' if os.getenv('VERCEL') else os.path.join(_base_dir, 'database.db')


def get_db():
    if USE_POSTGRES:
        # Imports inside function — never crash at module load time
        import pg8000.dbapi
        import ssl
        from urllib.parse import urlparse
        u = urlparse(_raw_db_url)
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        return pg8000.dbapi.connect(
            host=u.hostname,
            port=u.port or 5432,
            user=u.username,
            password=u.password,
            database=u.path.lstrip('/').split('?')[0],
            ssl_context=ssl_ctx,
        )
    else:
        import sqlite3
        conn = sqlite3.connect(_sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn


def get_cursor(conn):
    return conn.cursor()


def fetchall(cursor):
    if USE_POSTGRES:
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
    else:
        return [dict(r) for r in cursor.fetchall()]


def fetchone(cursor):
    if USE_POSTGRES:
        if not cursor.description:
            return None
        cols = [d[0] for d in cursor.description]
        row  = cursor.fetchone()
        return dict(zip(cols, row)) if row else None
    else:
        row = cursor.fetchone()
        return dict(row) if row else None


# ── Schema ──────────────────────────────────────────────────────────────────
def init_db():
    conn = get_db()  # get_db() handles all imports internally
    c = get_cursor(conn)

    if USE_POSTGRES:
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id               SERIAL PRIMARY KEY,
                title            TEXT NOT NULL,
                content          TEXT NOT NULL,
                rumble_link      TEXT,
                featured_image_id INTEGER,
                categories       TEXT,
                metadata         TEXT,
                created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source           TEXT DEFAULT 'automation',
                thumbnail_url    TEXT
            )
        ''')
    else:
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                title            TEXT NOT NULL,
                content          TEXT NOT NULL,
                rumble_link      TEXT,
                featured_image_id INTEGER,
                categories       TEXT,
                metadata         TEXT,
                created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source           TEXT DEFAULT 'automation',
                thumbnail_url    TEXT
            )
        ''')
        # migrate older local databases
        try:
            c.execute('ALTER TABLE posts ADD COLUMN thumbnail_url TEXT')
        except Exception:
            pass

    conn.commit()
    conn.close()


def row_to_dict(row):
    if row is None:
        return None
    return {
        'id':               row['id'],
        'title':            row['title'],
        'content':          row['content'],
        'rumble_link':      row['rumble_link'],
        'featured_image_id':row['featured_image_id'],
        'categories':       json.loads(row['categories']) if row['categories'] else [],
        'metadata':         json.loads(row['metadata'])   if row['metadata']   else {},
        'created_at':       str(row['created_at']),
        'source':           row['source'],
        'thumbnail_url':    row['thumbnail_url'],
    }


# ── Auth ─────────────────────────────────────────────────────────────────────
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        parts = auth.split()
        if len(parts) != 2 or parts[0] != 'Bearer' or parts[1] != API_KEY:
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated


# ── Page routes ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    return render_template('post.html', post_id=post_id)

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/search')
def search():
    return render_template('search.html', query=request.args.get('q', ''))


# ── API: list posts ──────────────────────────────────────────────────────────
@app.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        page     = int(request.args.get('page', 1))
        limit    = int(request.args.get('limit', 12))
        category = request.args.get('category', '').strip()
        sort     = request.args.get('sort', 'newest')
        offset   = (page - 1) * limit

        like_op = 'ILIKE' if USE_POSTGRES else 'LIKE'

        conn = get_db()
        c    = get_cursor(conn)

        where  = f'WHERE categories {like_op} {PH}' if category else ''
        params = [f'%{category}%'] if category else []

        order = 'ASC' if sort == 'oldest' else 'DESC'

        c.execute(
            f'SELECT * FROM posts {where} ORDER BY created_at {order} LIMIT {PH} OFFSET {PH}',
            params + [limit, offset]
        )
        rows = fetchall(c)

        c.execute(f'SELECT COUNT(*) FROM posts {where}', params)
        total = list(fetchone(c).values())[0]

        conn.close()

        return jsonify({
            'posts': [row_to_dict(r) for r in rows],
            'total': total,
            'page':  page,
            'limit': limit,
            'pages': max(1, (total + limit - 1) // limit),
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: single post ─────────────────────────────────────────────────────────
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        conn = get_db()
        c    = get_cursor(conn)
        c.execute(f'SELECT * FROM posts WHERE id = {PH}', (post_id,))
        row  = fetchone(c)
        conn.close()
        if not row:
            return jsonify({'error': 'Post not found'}), 404
        return jsonify(row_to_dict(row)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: create post ─────────────────────────────────────────────────────────
@app.route('/api/posts', methods=['POST'])
@require_api_key
def create_post():
    try:
        data = request.get_json()
        if not data.get('title') or not data.get('content'):
            return jsonify({'error': 'title and content are required'}), 400

        title             = data['title']
        content           = data['content']
        rumble_link       = data.get('rumble_link', '')
        featured_image_id = data.get('featured_image_id')
        categories        = json.dumps(data.get('categories', []))
        metadata          = json.dumps(data.get('metadata', {}))
        source            = data.get('source', 'automation')
        thumbnail_url     = data.get('thumbnail_url', '')

        conn = get_db()
        c    = get_cursor(conn)

        if USE_POSTGRES:
            c.execute('''
                INSERT INTO posts
                    (title, content, rumble_link, featured_image_id, categories, metadata, source, thumbnail_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
            ''', (title, content, rumble_link, featured_image_id, categories, metadata, source, thumbnail_url))
            post_id = fetchone(c)['id']
        else:
            c.execute('''
                INSERT INTO posts
                    (title, content, rumble_link, featured_image_id, categories, metadata, source, thumbnail_url)
                VALUES (?,?,?,?,?,?,?,?)
            ''', (title, content, rumble_link, featured_image_id, categories, metadata, source, thumbnail_url))
            post_id = c.lastrowid

        conn.commit()
        conn.close()
        return jsonify({'id': post_id, 'message': 'Post created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: search posts ─────────────────────────────────────────────────────────
@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    try:
        q     = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 24))

        if len(q) < 2:
            return jsonify({'error': 'Search term must be at least 2 characters'}), 400

        like_op = 'ILIKE' if USE_POSTGRES else 'LIKE'
        term    = f'%{q}%'

        conn = get_db()
        c    = get_cursor(conn)
        c.execute(
            f'SELECT * FROM posts WHERE title {like_op} {PH} OR content {like_op} {PH} ORDER BY created_at DESC LIMIT {PH}',
            (term, term, limit)
        )
        rows = fetchall(c)
        conn.close()

        return jsonify({'posts': [row_to_dict(r) for r in rows], 'count': len(rows), 'query': q}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: delete post ──────────────────────────────────────────────────────────
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@require_api_key
def delete_post(post_id):
    try:
        conn = get_db()
        c    = get_cursor(conn)
        c.execute(f'SELECT id FROM posts WHERE id = {PH}', (post_id,))
        if not fetchone(c):
            conn.close()
            return jsonify({'error': 'Post not found'}), 404
        c.execute(f'DELETE FROM posts WHERE id = {PH}', (post_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Post deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: stats ────────────────────────────────────────────────────────────────
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db()
        c    = get_cursor(conn)

        c.execute('SELECT COUNT(*) FROM posts')
        total = list(fetchone(c).values())[0]

        c.execute('SELECT source, COUNT(*) as cnt FROM posts GROUP BY source')
        sources = {r['source']: r['cnt'] for r in fetchall(c)}

        c.execute('SELECT created_at FROM posts ORDER BY created_at DESC LIMIT 1')
        last = fetchone(c)
        conn.close()

        return jsonify({
            'total_posts': total,
            'by_source':   sources,
            'last_post':   str(last['created_at']) if last else None,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ── Lazy DB init (runs on first real request, not at import time) ─────────────
_db_ready = False

@app.before_request
def _ensure_db():
    global _db_ready
    if not _db_ready:
        try:
            init_db()
            _db_ready = True
        except BaseException as e:
            print(f"[WARN] init_db: {e}")

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
