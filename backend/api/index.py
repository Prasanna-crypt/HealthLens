import sys
import os
from pathlib import Path

# Add backend directory to sys.path so 'app' imports resolve properly
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ["VERCEL"] = "1"

from app.main import app as fastapi_app

# Pure ASGI entrypoint: modifies ASGI scope before FastAPI router evaluates methods & paths
async def app(scope, receive, send):
    if scope["type"] == "http":
        headers = dict(scope.get("headers", []))
        
        # When Vercel rewrites to /api/index.py, the client's actual request URL is in x-matched-path
        matched = headers.get(b"x-matched-path")
        if matched:
            scope["path"] = matched.decode("utf-8")
        elif scope.get("path", "").startswith("/api/index.py"):
            sub = scope["path"][len("/api/index.py"):]
            scope["path"] = sub if sub else "/"
            
    await fastapi_app(scope, receive, send)
