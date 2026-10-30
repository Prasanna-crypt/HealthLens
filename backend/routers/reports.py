from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import random
from datetime import datetime
import models, schemas, auth, database

router = APIRouter(prefix="/api/reports", tags=["reports"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=schemas.Report)
async def upload_report(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Mocking AI extraction for now
    # We will generate some realistic mock results
    tests = [
        {"name": "Hemoglobin", "unit": "g/dL", "low": 13.0, "high": 17.0},
        {"name": "WBC", "unit": "x10^3/uL", "low": 4.5, "high": 11.0},
        {"name": "Platelets", "unit": "x10^3/uL", "low": 150.0, "high": 400.0},
        {"name": "Cholesterol", "unit": "mg/dL", "low": 0.0, "high": 200.0},
        {"name": "Glucose", "unit": "mg/dL", "low": 70.0, "high": 99.0},
    ]

    report = models.Report(
        user_id=current_user.id,
        filename=file.filename,
        report_date=datetime.utcnow().strftime("%Y-%m-%d"),
        patient_name=current_user.full_name,
        ai_summary="The overall health profile looks normal. However, consider monitoring your cholesterol levels as they are slightly elevated. Maintain a healthy diet and regular exercise.",
        is_demo=False
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    normal_c, low_c, high_c = 0, 0, 0

    for t in tests:
        # Generate a random value near the range
        val = round(random.uniform(t["low"] * 0.8, t["high"] * 1.2), 1)
        if val < t["low"]:
            status = "LOW"
            low_c += 1
            expl = f"Your {t['name']} is slightly lower than the standard range. This might indicate a minor deficiency."
        elif val > t["high"]:
            status = "HIGH"
            high_c += 1
            expl = f"Your {t['name']} is elevated. Consider dietary adjustments."
        else:
            status = "NORMAL"
            normal_c += 1
            expl = f"Your {t['name']} is within the normal range."

        tr = models.TestResult(
            report_id=report.id,
            test_name=t["name"],
            value=val,
            unit=t["unit"],
            reference_low=t["low"],
            reference_high=t["high"],
            status=status,
            ocr_confidence=0.98,
            ai_explanation=expl,
            category="Blood"
        )
        db.add(tr)
    
    report.total_tests = len(tests)
    report.normal_count = normal_c
    report.low_count = low_c
    report.high_count = high_c
    
    db.commit()
    db.refresh(report)
    return report

@router.get("/", response_model=List[schemas.ReportListItem])
def list_reports(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    return db.query(models.Report).filter(models.Report.user_id == current_user.id).order_by(models.Report.upload_date.desc()).all()

@router.get("/compare", response_model=schemas.ReportComparison)
def compare_reports(
    report1_id: int, 
    report2_id: int, 
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(database.get_db)
):
    r1 = db.query(models.Report).filter(models.Report.id == report1_id, models.Report.user_id == current_user.id).first()
    r2 = db.query(models.Report).filter(models.Report.id == report2_id, models.Report.user_id == current_user.id).first()
    
    if not r1 or not r2:
        raise HTTPException(status_code=404, detail="One or both reports not found")

    comparisons = []
    
    # Simple inner join on test name
    r2_tests = {t.test_name: t for t in r2.test_results}
    
    for t1 in r1.test_results:
        if t1.test_name in r2_tests:
            t2 = r2_tests[t1.test_name]
            change = t2.value - t1.value
            comparisons.append({
                "test_name": t1.test_name,
                "report1_value": t1.value,
                "report1_unit": t1.unit,
                "report1_status": t1.status,
                "report2_value": t2.value,
                "report2_unit": t2.unit,
                "report2_status": t2.status,
                "change": round(change, 2)
            })

    return {
        "report1": r1,
        "report2": r2,
        "comparisons": comparisons
    }

@router.get("/{id}", response_model=schemas.Report)
def get_report(id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    report = db.query(models.Report).filter(models.Report.id == id, models.Report.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.delete("/{id}")
def delete_report(id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    report = db.query(models.Report).filter(models.Report.id == id, models.Report.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return {"message": "Deleted"}
