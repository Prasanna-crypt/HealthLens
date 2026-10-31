from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json

from .database import engine, Base, SessionLocal
from .models.reference_range import ReferenceRange
from .api import auth, reports, results, demo, ai, profile

# create tables if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HealthLens API")

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

@app.api_route("/", methods=["GET", "POST", "OPTIONS"])
@app.api_route("/api", methods=["GET", "POST", "OPTIONS"])
@app.api_route("/api/index.py", methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"])
def root():
    return {"status": "ok", "service": "HealthLens Backend API"}

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "ok"}
