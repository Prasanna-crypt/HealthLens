import sys
import os
import urllib.parse
from pathlib import Path

# Add backend directory to sys.path so 'app' imports resolve properly
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ["VERCEL"] = "1"

from app.main import app as fastapi_app

# Pure ASGI entrypoint: maps Vercel serverless rewrites to FastAPI paths
async def app(scope, receive, send):
    if scope["type"] == "http":
        query_bytes = scope.get("query_string", b"")
        query_str = query_bytes.decode("utf-8", errors="ignore")
        params = urllib.parse.parse_qs(query_str, keep_blank_values=True)
        
        captured_path = None
        for key in ["__path", "path", "match"]:
            if key in params and params[key]:
                captured_path = params.pop(key)[0]
                break
                
        if captured_path is not None:
            clean_path = urllib.parse.unquote(captured_path).strip()
            scope["path"] = "/" + clean_path.lstrip("/")
            # Re-encode query string without the captured routing parameter
            scope["query_string"] = urllib.parse.urlencode(params, doseq=True).encode("utf-8")
        elif scope.get("path", "").startswith("/api/index.py"):
            sub = scope["path"][len("/api/index.py"):]
            scope["path"] = sub if sub else "/"
            
    await fastapi_app(scope, receive, send)
