import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db

try:
    init_db()
except Exception as e:
    print(f"[WARN] init_db: {e}")

# Vercel uses `app`
