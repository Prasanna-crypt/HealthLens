from sqlalchemy.orm import Session
from ..models.health import HealthChange
from ..models.report import Report
from ..models.test_result import TestResult

def calculate_changes(current_report_id: int, user_id: int, db: Session):
    current_report = db.query(Report).filter(Report.id == current_report_id).first()
    if not current_report:
        return
        
    previous_report = db.query(Report).filter(
        Report.user_id == user_id, 
        Report.id < current_report_id
    ).order_by(Report.report_date.desc()).first()
    
    if not previous_report:
        return
        
    curr_tests = {t.test_name: t for t in db.query(TestResult).filter(TestResult.report_id == current_report_id).all()}
    prev_tests = {t.test_name: t for t in db.query(TestResult).filter(TestResult.report_id == previous_report.id).all()}
    
    for name, curr_t in curr_tests.items():
        if name in prev_tests:
            prev_t = prev_tests[name]
            abs_change = round(curr_t.value - prev_t.value, 3)
            pct_change = round((abs_change / prev_t.value * 100), 3) if prev_t.value != 0 else 0.0
            
            if abs_change > 0:
                direction = "Increased"
            elif abs_change < 0:
                direction = "Decreased"
            else:
                direction = "Stable"
                
            hc = HealthChange(
                user_id=user_id,
                report_id=current_report_id,
                test_name=name,
                previous_value=round(prev_t.value, 3) if prev_t.value is not None else None,
                current_value=round(curr_t.value, 3) if curr_t.value is not None else None,
                absolute_change=abs_change,
                percentage_change=pct_change,
                direction=direction,
                previous_status=prev_t.status,
                current_status=curr_t.status
            )
            db.add(hc)
    db.commit()

def get_user_changes(user_id: int, db: Session):
    changes = db.query(HealthChange).filter(HealthChange.user_id == user_id).all()
    for c in changes:
        if c.absolute_change is not None:
            c.absolute_change = round(c.absolute_change, 3)
        if c.percentage_change is not None:
            c.percentage_change = round(c.percentage_change, 3)
        if c.previous_value is not None:
            c.previous_value = round(c.previous_value, 3)
        if c.current_value is not None:
            c.current_value = round(c.current_value, 3)
    return changes
