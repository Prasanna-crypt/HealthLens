from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, TokenResponse
from ..utils.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
@router.post("/register/", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    clean_email = user.email.strip().lower()
    existing = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if existing:
        # If user already registered, update their password so they don't get permanently locked out
        existing.hashed_password = hash_password(user.password)
        if user.full_name:
            existing.full_name = user.full_name.strip()
        db.commit()
        db.refresh(existing)
        return existing
    
    new_user = User(
        email=clean_email,
        full_name=user.full_name.strip() if user.full_name else "",
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/reset-password")
@router.post("/reset-password/")
async def reset_password(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    email = str(body.get("email", "")).strip().lower()
    new_password = str(body.get("new_password", "")).strip()
    
    if not email or not new_password:
        raise HTTPException(status_code=400, detail="Email and new password are required")
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user:
        # Create user if not present
        user = User(email=email, full_name="User", hashed_password=hash_password(new_password))
        db.add(user)
    else:
        user.hashed_password = hash_password(new_password)
        
    db.commit()
    return {"message": "Password successfully reset. You can now log in."}

@router.post("/login", response_model=TokenResponse)
@router.post("/login/", response_model=TokenResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    username = None
    password = None

    # Support JSON request bodies
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            username = body.get("username") or body.get("email")
            password = body.get("password")
        except Exception:
            pass

    # Support form-urlencoded request bodies
    if not username or not password:
        try:
            form = await request.form()
            username = form.get("username") or form.get("email")
            password = form.get("password")
        except Exception:
            pass

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username/email and password are required"
        )

    clean_email = str(username).strip().lower()
    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    
    if not user or not verify_password(str(password), user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/demo-login", response_model=TokenResponse)
@router.post("/demo-login/", response_model=TokenResponse)
def demo_login(db: Session = Depends(get_db)):
    demo_email = "demo@healthlens.app"
    user = db.query(User).filter(func.lower(User.email) == demo_email).first()
    if not user:
        user = User(
            email=demo_email,
            full_name="Alex Mercer (Demo)",
            hashed_password=hash_password("DemoPassword123!")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Auto-seed demo reports for this demo user
        try:
            from .demo import load_demo_data
            load_demo_data(current_user=user, db=db)
        except Exception:
            pass

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
@router.get("/me/", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
