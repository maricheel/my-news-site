import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app, init_db
    try:
        init_db()
    except Exception as db_err:
        print(f"[WARN] init_db error: {db_err}")
except Exception as import_err:
    # If the app fails to import, return a diagnostic page instead of crashing
    import flask
    _tb = traceback.format_exc()
    app = flask.Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def _show_error(path):
        return f'<pre style="padding:2rem;font-size:14px;background:#111;color:#f88">{_tb}</pre>', 500
