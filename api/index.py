import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_import_error = None
try:
    from app import app as _real_app
except Exception:
    _import_error = traceback.format_exc()
    _real_app = None

from flask import Flask

if _real_app is not None:
    app = _real_app
else:
    app = Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def show_error(path=''):
        return (
            f'<h2>Import Error</h2><pre style="white-space:pre-wrap">{_import_error}</pre>',
            500,
        )
