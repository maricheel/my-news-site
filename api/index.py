import os
import traceback
from flask import Flask, jsonify

_steps = []
_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Step 1: Flask with template + static folders
try:
    app = Flask(
        __name__,
        template_folder=os.path.join(_base_dir, 'templates'),
        static_folder=os.path.join(_base_dir, 'static'),
    )
    _steps.append('OK: Flask init with template_folder + static_folder')
except BaseException:
    app = Flask(__name__)
    _steps.append('FAIL: Flask init\n' + traceback.format_exc())

# Step 2: dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    _steps.append('OK: dotenv')
except BaseException:
    _steps.append('FAIL: dotenv\n' + traceback.format_exc())

# Step 3: filesystem info
_steps.append(f'__file__ = {__file__}')
_steps.append(f'_base_dir = {_base_dir}')
_steps.append(f'templates/ exists = {os.path.isdir(os.path.join(_base_dir, "templates"))}')
_steps.append(f'static/ exists   = {os.path.isdir(os.path.join(_base_dir, "static"))}')

# Step 4: after_request decorator
try:
    @app.after_request
    def _cors(r):
        r.headers['Access-Control-Allow-Origin'] = '*'
        return r
    _steps.append('OK: after_request')
except BaseException:
    _steps.append('FAIL: after_request\n' + traceback.format_exc())

# Step 5: before_request decorator
try:
    @app.before_request
    def _ping():
        pass
    _steps.append('OK: before_request')
except BaseException:
    _steps.append('FAIL: before_request\n' + traceback.format_exc())

# Step 6: env vars
_steps.append(f'DATABASE_URL set = {bool(os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL"))}')

@app.route('/')
def index():
    return '<br>'.join(_steps), 200

@app.route('/api/health')
def health():
    return jsonify({'steps': _steps})
