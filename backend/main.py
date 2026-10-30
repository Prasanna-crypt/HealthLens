from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, reports, results, demo

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HealthLens API")

# Setup CORS to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(results.router)
app.include_router(demo.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to HealthLens API"}
