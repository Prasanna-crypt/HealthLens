import sys
import os
from pathlib import Path

# Add backend directory to sys.path so 'app' imports resolve properly
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ["VERCEL"] = "1"

from app.main import app as fastapi_app

# Pure ASGI entrypoint: strips /api/index.py prefix if added by Vercel serverless routing
async def app(scope, receive, send):
    if scope["type"] == "http":
        path = scope.get("path", "")
        if path.startswith("/api/index.py"):
            sub = path[len("/api/index.py"):]
            scope["path"] = sub if sub else "/"
            
    await fastapi_app(scope, receive, send)
