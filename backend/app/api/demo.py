from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import os

from ..database import get_db
from ..models.user import User
from ..models.report import Report
from ..models.test_result import TestResult
from ..utils.security import get_current_user

router = APIRouter()

def _get_explanation(test_name: str, status: str, value: float, unit: str, ref_low: float, ref_high: float) -> str:
    if status == "NORMAL":
        return f"The {test_name} result of {value} {unit} falls within the reference range of {ref_low}–{ref_high} {unit}. This is a normal finding."
    elif status == "LOW":
        return f"The {test_name} result of {value} {unit} is below the reference range of {ref_low}–{ref_high} {unit}. This finding should be interpreted together with other results and clinical information. Please consult a healthcare professional."
    elif status == "HIGH":
        return f"The {test_name} result of {value} {unit} is above the reference range of {ref_low}–{ref_high} {unit}. This finding should be interpreted together with other results and clinical information. Please consult a healthcare professional."
    
    return f"The {test_name} result is {value} {unit}. Reference range information is not available for comparison."

@router.post("/load")
def load_demo_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_demos = db.query(Report).filter(
        Report.user_id == current_user.id,
        Report.is_demo == True,
    ).count()
    
    if existing_demos > 0:
        return {"message": f"Demo data already loaded ({existing_demos} reports).", "count": existing_demos}

    demo_file = os.path.join(os.path.dirname(__file__), '..', 'seed', 'demo_data.json')
    if not os.path.exists(demo_file):
        raise HTTPException(status_code=500, detail="Demo data file not found")

    with open(demo_file, 'r', encoding='utf-8') as f:
        demo_reports = json.load(f)

    created_count = 0
    for report_data in demo_reports:
        tests = report_data['tests']
        
        report = Report(
            user_id=current_user.id,
            filename=report_data['title'],
            report_date=report_data['date'],
            patient_name=report_data['patient'],
            ai_summary=report_data['summary'],
            total_tests=len(tests),
            normal_count=sum(1 for t in tests if t['status'] == 'NORMAL'),
            low_count=sum(1 for t in tests if t['status'] == 'LOW'),
            high_count=sum(1 for t in tests if t['status'] == 'HIGH'),
            is_demo=True,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        for test_data in tests:
            test_result_record = TestResult(
                report_id=report.id,
                test_name=test_data['test_name'],
                value=test_data['value'],
                unit=test_data['unit'],
                reference_low=test_data.get('ref_low'),
                reference_high=test_data.get('ref_high'),
                status=test_data['status'],
                ai_explanation=_get_explanation(
                    test_data['test_name'], 
                    test_data['status'], 
                    test_data['value'], 
                    test_data['unit'], 
                    test_data.get('ref_low', 0), 
                    test_data.get('ref_high', 0)
                ),
                category=test_data.get('category'),
            )
            db.add(test_result_record)
        
        db.commit()
        from ..services.comparison_service import calculate_changes
        calculate_changes(report.id, current_user.id, db)
        created_count += 1

    return {"message": f"Successfully loaded {created_count} demo reports", "count": created_count}

@router.delete("/clear")
def clear_demo_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    demo_reports = db.query(Report).filter(
        Report.user_id == current_user.id,
        Report.is_demo == True,
    ).all()
    
    count = len(demo_reports)
    for report in demo_reports:
        db.delete(report)
    db.commit()
    
    return {"message": f"Deleted {count} demo reports", "count": count}
