import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_app   = None
_error = None

try:
    from app import app as _app, init_db
    try:
        init_db()
    except Exception as e:
        print(f"[WARN] init_db: {traceback.format_exc()}")
except Exception:
    _error = traceback.format_exc()
    print(f"[FATAL] import failed:\n{_error}")

if _app is None:
    # Show the real error in the browser instead of a blank Vercel crash page
    from flask import Flask as _Flask
    app = _Flask(__name__)
    _msg = _error or "Unknown startup error"

    @app.route("/", defaults={"p": ""})
    @app.route("/<path:p>")
    def _err(p):
        return (
            f'<html><body style="background:#111;color:#f66;font-family:monospace;padding:2rem">'
            f'<h2>Startup error</h2><pre>{_msg}</pre></body></html>',
            500,
        )
else:
    app = _app
