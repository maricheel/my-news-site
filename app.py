from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Resolve paths relative to this file so Flask finds templates/static
# whether running locally or from api/index.py on Vercel
_base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(_base_dir, 'templates'),
    static_folder=os.path.join(_base_dir, 'static'),
)
CORS(app)

# Security
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
API_KEY = os.getenv('API_KEY', 'your-api-key-change-this')

# Vercel's filesystem is read-only except /tmp
DATABASE = '/tmp/database.db' if os.getenv('VERCEL') else os.path.join(_base_dir, 'database.db')

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            rumble_link TEXT,
            featured_image_id INTEGER,
            categories TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'automation',
            thumbnail_url TEXT
        )
    ''')
    # Migrate existing databases that don't have thumbnail_url yet
    try:
        c.execute('ALTER TABLE posts ADD COLUMN thumbnail_url TEXT')
    except Exception:
        pass
    conn.commit()
    conn.close()

# Helper: Get database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Helper: Convert database row to dictionary
def row_to_dict(row):
    if row is None:
        return None
    return {
        'id': row[0],
        'title': row[1],
        'content': row[2],
        'rumble_link': row[3],
        'featured_image_id': row[4],
        'categories': json.loads(row[5]) if row[5] else [],
        'metadata': json.loads(row[6]) if row[6] else {},
        'created_at': row[7],
        'source': row[8],
        'thumbnail_url': row[9] if len(row) > 9 else None
    }

# Decorator: Require API key for protected endpoints
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Missing API key'}), 401
        
        # Format: "Bearer YOUR_API_KEY"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return jsonify({'error': 'Invalid authorization format'}), 401
        
        token = parts[1]
        if token != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# ============= ROUTES =============

# Homepage - Render HTML (not API)
@app.route('/')
def index():
    """Homepage with post grid"""
    return render_template('index.html')

# Single post page
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    """Display single post"""
    return render_template('post.html', post_id=post_id)

# Admin dashboard
@app.route('/admin')
def admin_dashboard():
    """Admin panel (no authentication yet, add later)"""
    return render_template('admin.html')

# Search page
@app.route('/search')
def search():
    """Search results page"""
    query = request.args.get('q', '')
    return render_template('search.html', query=query)

# ============= API ENDPOINTS =============

# API: Get all posts (paginated)
@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Get paginated list of posts
    Query params: ?page=1&limit=10&category=24&sort=newest
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        category = request.args.get('category')
        sort = request.args.get('sort', 'newest')  # newest or oldest
        
        offset = (page - 1) * limit
        
        conn = get_db()
        c = conn.cursor()
        
        # Build query
        query = 'SELECT * FROM posts'
        params = []
        
        # Filter by category if provided
        if category:
            query += ' WHERE categories LIKE ?'
            params.append(f'%{category}%')
        
        # Sort
        if sort == 'oldest':
            query += ' ORDER BY created_at ASC'
        else:
            query += ' ORDER BY created_at DESC'
        
        # Pagination
        query += ' LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        # Execute query
        c.execute(query, params)
        rows = c.fetchall()
        
        # Get total count (for pagination)
        count_query = 'SELECT COUNT(*) FROM posts'
        if category:
            count_query += ' WHERE categories LIKE ?'
            c.execute(count_query, [f'%{category}%'] if category else [])
        else:
            c.execute(count_query)
        
        total = c.fetchone()[0]
        conn.close()
        
        # Convert rows to dictionaries
        posts = []
        for row in rows:
            posts.append(row_to_dict(row))
        
        return jsonify({
            'posts': posts,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get single post by ID
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get a single post by ID"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Post not found'}), 404
        
        post = row_to_dict(row)
        return jsonify(post), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Create new post (from automation)
@app.route('/api/posts', methods=['POST'])
@require_api_key
def create_post():
    """
    Create a new post
    Requires: Authorization: Bearer API_KEY header
    Body: JSON with title, content, rumble_link, categories, featured_image_id, metadata
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('content'):
            return jsonify({'error': 'Title and content are required'}), 400
        
        # Extract fields
        title = data.get('title')
        content = data.get('content')
        rumble_link = data.get('rumble_link', '')
        featured_image_id = data.get('featured_image_id')
        categories = data.get('categories', [])
        metadata = data.get('metadata', {})
        source = data.get('source', 'automation')
        thumbnail_url = data.get('thumbnail_url', '')

        # Convert lists/dicts to JSON strings for storage
        categories_json = json.dumps(categories)
        metadata_json = json.dumps(metadata)

        # Insert into database
        conn = get_db()
        c = conn.cursor()

        c.execute('''
            INSERT INTO posts (title, content, rumble_link, featured_image_id, categories, metadata, source, thumbnail_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, content, rumble_link, featured_image_id, categories_json, metadata_json, source, thumbnail_url))
        
        post_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': post_id,
            'message': 'Post created successfully'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Search posts
@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search posts by title or content
    Query params: ?q=search_term&limit=10
    """
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify({'error': 'Search term required'}), 400
        
        if len(query) < 2:
            return jsonify({'error': 'Search term must be at least 2 characters'}), 400
        
        conn = get_db()
        c = conn.cursor()
        
        search_term = f'%{query}%'
        c.execute('''
            SELECT * FROM posts 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (search_term, search_term, limit))
        
        rows = c.fetchall()
        conn.close()
        
        posts = [row_to_dict(row) for row in rows]
        
        return jsonify({
            'posts': posts,
            'count': len(posts),
            'query': query
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Delete post (admin only)
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@require_api_key
def delete_post(post_id):
    """Delete a post by ID (requires API key)"""
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Check if post exists
        c.execute('SELECT id FROM posts WHERE id = ?', (post_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'error': 'Post not found'}), 404
        
        # Delete
        c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Post deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get stats (for admin dashboard)
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about posts"""
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Total posts
        c.execute('SELECT COUNT(*) FROM posts')
        total_posts = c.fetchone()[0]
        
        # Posts by source
        c.execute('SELECT source, COUNT(*) FROM posts GROUP BY source')
        sources = c.fetchall()
        
        # Most recent post
        c.execute('SELECT created_at FROM posts ORDER BY created_at DESC LIMIT 1')
        last_post = c.fetchone()
        
        conn.close()
        
        sources_dict = {row[0]: row[1] for row in sources}
        
        return jsonify({
            'total_posts': total_posts,
            'by_source': sources_dict,
            'last_post': last_post[0] if last_post else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# ============= MAIN =============

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run Flask dev server
    app.run(debug=True, host='127.0.0.1', port=5000)
