import sys
import os
from pathlib import Path

# Add backend directory to sys.path so 'app' imports resolve cleanly
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent / "backend"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Ensure Vercel serverless flag is set
os.environ["VERCEL"] = "1"

# Import the FastAPI ASGI application
from app.main import app
