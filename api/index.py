import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
ls frontend/tailwind.config.js 2>/dev/null && echo "tailwind config EXISTS here"
grep -r "Calm routes" frontend/src 2>/dev/null | head -3