from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send
import os
import json
import urllib.parse

from .database import engine, Base, SessionLocal
from .models.reference_range import ReferenceRange
from .api import auth, reports, results, demo, ai, profile

# create tables if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HealthLens API")

# Pure ASGI middleware: maps Vercel serverless rewrites to FastAPI paths
class VercelPathMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
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
                scope["query_string"] = urllib.parse.urlencode(params, doseq=True).encode("utf-8")
            elif scope.get("path", "").startswith("/api/index.py"):
                sub = scope["path"][len("/api/index.py"):]
                scope["path"] = sub if sub else "/"

        await self.app(scope, receive, send)

app.add_middleware(VercelPathMiddleware)

# Allow all origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Register all routers with both "/api" and direct prefixes for 100% routing resilience
for prefix in ["/api", ""]:
    app.include_router(auth.router, prefix=f"{prefix}/auth", tags=["auth"])
    app.include_router(reports.router, prefix=f"{prefix}/reports", tags=["reports"])
    app.include_router(results.router, prefix=f"{prefix}/results", tags=["results"])
    app.include_router(demo.router, prefix=f"{prefix}/demo", tags=["demo"])
    app.include_router(ai.router, prefix=f"{prefix}/ai", tags=["ai"])
    app.include_router(profile.router, prefix=f"{prefix}/profile", tags=["profile"])

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # Seed reference ranges if db is empty
        if db.query(ReferenceRange).count() == 0:
            seed_file = os.path.join(os.path.dirname(__file__), 'seed', 'reference_ranges.json')
            if os.path.exists(seed_file):
                with open(seed_file, 'r', encoding='utf-8') as f:
                    ranges = json.load(f)
                    for r in ranges:
                        aliases_str = json.dumps(r.get('aliases', []))
                        rr = ReferenceRange(
                            test_name=r['test_name'],
                            low=r['low'],
                            high=r['high'],
                            unit=r['unit'],
                            category=r['category'],
                            source=r['source'],
                            aliases=aliases_str
                        )
                        db.add(rr)
                    db.commit()
    except Exception as e:
        print(f"[HealthLens] Startup seed notice: {e}")
    finally:
        db.close()

@app.get("/")
@app.get("/api")
def root():
    return {"status": "ok", "service": "HealthLens Backend API"}

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Not Found",
            "scope_path": request.scope.get("path"),
            "scope_query": request.scope.get("query_string", b"").decode("latin1"),
            "headers": {k.decode("latin1"): v.decode("latin1") for k, v in request.scope.get("headers", [])}
        }
    )
