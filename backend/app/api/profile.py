from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.health import HealthProfile
from ..utils.security import get_current_user
from ..schemas.ai_profile import ProfileUpdate

router = APIRouter()

@router.get("/")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        profile = HealthProfile(user_id=current_user.id, full_name=current_user.full_name)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/")
def update_profile(update_data: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(profile, key, value)
        
    db.commit()
    db.refresh(profile)
    return profile
