import os
from pathlib import Path
from dotenv import load_dotenv

# load up env vars with robust path resolution
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    # hacky fix for now: default secret key should be changed before going live
    SECRET_KEY = os.environ.get('SECRET_KEY', 'healthlens-dev-secret-key-change-in-production')
    
    # default to local sqlite inside backend directory
    DATABASE_URL = os.environ.get('DATABASE_URL', f"sqlite:///{BASE_DIR / 'healthlens.db'}")
    
    # OpenAI API for AI features
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    
    # NVIDIA endpoints for AI features (kept as fallback)
    NVIDIA_API_KEY = os.environ.get('NVIDIA_API_KEY', '')
    NVIDIA_BASE_URL = os.environ.get('NVIDIA_BASE_URL', 'https://integrate.api.nvidia.com/v1')
    
    # Default model for NVIDIA NIM
    NVIDIA_MODEL = os.environ.get('NVIDIA_MODEL', 'nvidia/nemotron-3.5-bolt-e4b')
    
    UPLOAD_DIR = os.environ.get('UPLOAD_DIR', 'uploads')

settings = Settings()
