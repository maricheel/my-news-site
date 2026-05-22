import os
import traceback
from flask import Flask, jsonify

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Unconditional top-level assignment — Vercel static check passes
app = Flask(__name__)

_steps = []

# Step 1: set template + static folders after init
try:
    app.template_folder = os.path.join(_base_dir, 'templates')
    app.static_folder   = os.path.join(_base_dir, 'static')
    _steps.append('OK: template_folder + static_folder')
except BaseException:
    _steps.append('FAIL: template/static\n' + traceback.format_exc())

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
_steps.append(f'DATABASE_URL set = {bool(os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL"))}')

# Step 4: decorators
try:
    @app.after_request
    def _cors(r):
        r.headers['Access-Control-Allow-Origin'] = '*'
        return r
    _steps.append('OK: after_request')
except BaseException:
    _steps.append('FAIL: after_request\n' + traceback.format_exc())

@app.route('/')
def index():
    return '<br>'.join(_steps), 200

@app.route('/api/health')
def health():
    return jsonify({'steps': _steps})
