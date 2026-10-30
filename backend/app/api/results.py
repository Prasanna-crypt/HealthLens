from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.test_result import TestResult
from ..models.report import Report
from ..schemas.test_result import TestResultResponse
from ..utils.security import get_current_user
from ..services.pattern_service import get_user_patterns
from ..services.comparison_service import get_user_changes

router = APIRouter()

@router.get("/patterns")
def get_patterns(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patterns = get_user_patterns(current_user.id, db)
    return patterns

@router.get("/changes")
def get_changes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    changes = get_user_changes(current_user.id, db)
    return changes

# Get Result Endpoint: Get details of a single test result (e.g., just the Hemoglobin)
@router.get("/{result_id}", response_model=TestResultResponse)
def get_result(result_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = db.query(TestResult).join(Report).filter(TestResult.id == result_id, Report.user_id == current_user.id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result

# Get Unique Tests Endpoint: Get a list of all unique test names the user has in all their reports
@router.get("/user/unique-tests", response_model=List[str])
def get_unique_tests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tests = db.query(TestResult.test_name).join(Report).filter(Report.user_id == current_user.id).distinct().all()
    return sorted([t[0] for t in tests])
