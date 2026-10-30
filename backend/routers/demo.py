from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import models, auth, database

router = APIRouter(prefix="/api/demo", tags=["demo"])

@router.post("/load")
def load_demo(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # Check if demo data already exists
    existing = db.query(models.Report).filter(models.Report.user_id == current_user.id, models.Report.is_demo == True).first()
    if existing:
        return {"message": "Demo data already loaded"}

    reports_data = [
        {
            "filename": "annual_blood_test_2023.pdf",
            "date": "2023-01-15",
            "tests": [
                {"name": "Hemoglobin", "unit": "g/dL", "val": 14.2, "low": 13.0, "high": 17.0, "status": "NORMAL"},
                {"name": "WBC", "unit": "x10^3/uL", "val": 6.5, "low": 4.5, "high": 11.0, "status": "NORMAL"},
                {"name": "Cholesterol", "unit": "mg/dL", "val": 210, "low": 0, "high": 200, "status": "HIGH"},
                {"name": "Glucose", "unit": "mg/dL", "val": 85, "low": 70, "high": 99, "status": "NORMAL"}
            ]
        },
        {
            "filename": "annual_blood_test_2024.pdf",
            "date": "2024-01-20",
            "tests": [
                {"name": "Hemoglobin", "unit": "g/dL", "val": 14.5, "low": 13.0, "high": 17.0, "status": "NORMAL"},
                {"name": "WBC", "unit": "x10^3/uL", "val": 7.1, "low": 4.5, "high": 11.0, "status": "NORMAL"},
                {"name": "Cholesterol", "unit": "mg/dL", "val": 195, "low": 0, "high": 200, "status": "NORMAL"},
                {"name": "Glucose", "unit": "mg/dL", "val": 90, "low": 70, "high": 99, "status": "NORMAL"}
            ]
        }
    ]

    for rd in reports_data:
        rep = models.Report(
            user_id=current_user.id,
            filename=rd["filename"],
            report_date=rd["date"],
            patient_name=current_user.full_name,
            ai_summary="This is a demo report showing mock data for demonstration purposes.",
            is_demo=True,
            total_tests=len(rd["tests"]),
            normal_count=sum(1 for t in rd["tests"] if t["status"] == "NORMAL"),
            low_count=sum(1 for t in rd["tests"] if t["status"] == "LOW"),
            high_count=sum(1 for t in rd["tests"] if t["status"] == "HIGH")
        )
        db.add(rep)
        db.commit()
        db.refresh(rep)

        for t in rd["tests"]:
            tr = models.TestResult(
                report_id=rep.id,
                test_name=t["name"],
                value=t["val"],
                unit=t["unit"],
                reference_low=t["low"],
                reference_high=t["high"],
                status=t["status"],
                ai_explanation="Demo explanation.",
                category="General"
            )
            db.add(tr)
        db.commit()

    return {"message": "Demo data loaded successfully"}
