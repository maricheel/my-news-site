import sys
import os
import traceback
from flask import Flask

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_import_error = None
_real_app = None
try:
    from app import app as _real_app
except Exception:
    _import_error = traceback.format_exc()

# app must be an unconditional top-level name for Vercel's static check
app = _real_app if _real_app is not None else Flask(__name__)

if _import_error:
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def _show_error(path=''):
        return f'<pre style="white-space:pre-wrap">{_import_error}</pre>', 500
