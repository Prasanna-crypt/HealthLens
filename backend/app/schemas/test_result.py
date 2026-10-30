from pydantic import BaseModel
from typing import Optional

# Defines what a test result looks like when we send it to the frontend
class TestResultResponse(BaseModel):
    id: int
    test_name: str
    value: float
    unit: str
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    status: str
    ocr_confidence: Optional[float] = None
    ai_explanation: Optional[str] = None
    category: Optional[str] = None
    
    class Config:
        from_attributes = True
