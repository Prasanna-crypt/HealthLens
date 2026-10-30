from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AssistantRequest(BaseModel):
    question: str

class AssistantResponse(BaseModel):
    answer: str

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    sex: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    blood_group: Optional[str] = None
    known_allergies: Optional[str] = None
    existing_conditions: Optional[str] = None
    current_medications: Optional[str] = None
