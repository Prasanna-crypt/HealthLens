from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth, database

router = APIRouter(prefix="/api/results", tags=["results"])

@router.get("/trends/{test_name}", response_model=List[schemas.TrendDataPoint])
def get_trends(test_name: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # Find all test results for this user with this test_name, ordered by report date
    reports = db.query(models.Report).filter(models.Report.user_id == current_user.id).all()
    report_ids = [r.id for r in reports]
    
    if not report_ids:
        return []

    results = db.query(models.TestResult).filter(
        models.TestResult.report_id.in_(report_ids),
        models.TestResult.test_name == test_name
    ).all()

    # Join with report to get date and filename
    # Doing it in python for simplicity since datasets are small
    data = []
    for r in results:
        rep = next(rep for rep in reports if rep.id == r.report_id)
        data.append({
            "date": rep.report_date or rep.upload_date.strftime("%Y-%m-%d"),
            "value": r.value,
            "report_id": rep.id,
            "filename": rep.filename,
            "reference_low": r.reference_low,
            "reference_high": r.reference_high
        })

    # Sort by date
    data.sort(key=lambda x: x["date"])
    return data

@router.get("/{id}", response_model=schemas.TestResult)
def get_result(id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    result = db.query(models.TestResult).join(models.Report).filter(
        models.TestResult.id == id,
        models.Report.user_id == current_user.id
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result
