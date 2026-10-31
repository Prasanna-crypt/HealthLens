import sys
import os
from pathlib import Path

# Add backend directory to sys.path so 'app' imports resolve properly
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ["VERCEL"] = "1"

from app.main import app
