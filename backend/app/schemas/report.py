# TODO: Might need a cleanup later.

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .test_result import TestResultResponse

class ReportBase(BaseModel):
    filename: str
    report_date: Optional[str] = None
    patient_name: Optional[str] = None
    total_tests: int = 0
    normal_count: int = 0
    low_count: int = 0
    high_count: int = 0
    is_demo: bool = False

# Summary version used when listing many reports
class ReportListResponse(ReportBase):
    id: int
    upload_date: datetime
    
    class Config:
        from_attributes = True

# Detailed version that includes all the individual test results
class ReportResponse(ReportListResponse):
    ai_summary: Optional[str] = None
    test_results: List[TestResultResponse] = []

# Used for the side-by-side comparison feature
class ReportComparisonResponse(BaseModel):
    report1: ReportResponse
    report2: ReportResponse
    comparison_summary: Optional[str] = None
