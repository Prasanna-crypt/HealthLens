from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TestResultBase(BaseModel):
    test_name: str
    value: float
    unit: str
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    status: str
    ocr_confidence: Optional[float] = None
    ai_explanation: Optional[str] = None
    category: Optional[str] = None

class TestResultCreate(TestResultBase):
    pass

class TestResult(TestResultBase):
    id: int
    report_id: int

    class Config:
        orm_mode = True

class ReportBase(BaseModel):
    filename: str
    report_date: Optional[str] = None
    patient_name: Optional[str] = None
    ai_summary: Optional[str] = None
    total_tests: int = 0
    normal_count: int = 0
    low_count: int = 0
    high_count: int = 0
    is_demo: bool = False

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: int
    user_id: int
    upload_date: datetime
    test_results: List[TestResult] = []

    class Config:
        orm_mode = True

class ReportListItem(ReportBase):
    id: int
    upload_date: datetime

    class Config:
        orm_mode = True

class ComparisonResult(BaseModel):
    test_name: str
    report1_value: float
    report1_unit: str
    report1_status: str
    report2_value: float
    report2_unit: str
    report2_status: str
    change: float

class ReportComparison(BaseModel):
    report1: ReportListItem
    report2: ReportListItem
    comparisons: List[ComparisonResult]

class TrendDataPoint(BaseModel):
    date: str
    value: float
    report_id: int
    filename: str
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
