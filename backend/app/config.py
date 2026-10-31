import os
from pathlib import Path
from dotenv import load_dotenv

# load up env vars with robust path resolution
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'healthlens-dev-secret-key-change-in-production')
    
    # default to local sqlite inside backend directory, or /tmp when running serverless on Vercel
    is_vercel = (
        os.environ.get("VERCEL") == "1"
        or os.environ.get("VERCEL_ENV") is not None
        or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
        or not os.access(str(BASE_DIR), os.W_OK)
        or "/vercel" in str(BASE_DIR)
    )
    default_db = "sqlite:////tmp/healthlens.db" if is_vercel else f"sqlite:///{BASE_DIR / 'healthlens.db'}"
    DATABASE_URL = os.environ.get('DATABASE_URL', default_db)
    
    # OpenAI API for AI features
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    
    # NVIDIA endpoints for AI features (kept as fallback)
    NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY', '')
    NVIDIA_BASE_URL = os.environ.get('NVIDIA_BASE_URL', 'https://integrate.api.nvidia.com/v1')
    
    # Default model for NVIDIA NIM
    NVIDIA_MODEL = os.environ.get('NVIDIA_MODEL', 'nvidia/nemotron-3.5-bolt-e4b')
    
    default_upload = "/tmp/uploads" if is_vercel else "uploads"
    UPLOAD_DIR = os.environ.get('UPLOAD_DIR', default_upload)

settings = Settings()
