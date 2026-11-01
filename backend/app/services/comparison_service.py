from sqlalchemy.orm import Session
from ..models.health import HealthChange
from ..models.report import Report
from ..models.test_result import TestResult
from .classification_service import find_reference_range, classify_result

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

            curr_status = curr_t.status
            prev_status = prev_t.status

            # Ensure statuses are classified if missing or UNKNOWN
            if not curr_status or curr_status.upper() == 'UNKNOWN':
                ref = find_reference_range(name, db)
                if ref and curr_t.value is not None:
                    curr_status = classify_result(curr_t.value, ref.low, ref.high)
                    curr_t.status = curr_status

            if not prev_status or prev_status.upper() == 'UNKNOWN':
                ref = find_reference_range(name, db)
                if ref and prev_t.value is not None:
                    prev_status = classify_result(prev_t.value, ref.low, ref.high)
                    prev_t.status = prev_status
                
            hc = HealthChange(
                user_id=user_id,
                report_id=current_report_id,
                test_name=name,
                previous_value=round(prev_t.value, 3) if prev_t.value is not None else None,
                current_value=round(curr_t.value, 3) if curr_t.value is not None else None,
                absolute_change=abs_change,
                percentage_change=pct_change,
                direction=direction,
                previous_status=prev_status,
                current_status=curr_status
            )
            db.add(hc)
    db.commit()

def get_user_changes(user_id: int, db: Session):
    changes = db.query(HealthChange).filter(HealthChange.user_id == user_id).all()
    if not changes:
        user_reports = db.query(Report).filter(Report.user_id == user_id).order_by(Report.report_date.asc(), Report.id.asc()).all()
        if len(user_reports) >= 2:
            for rep in user_reports[1:]:
                calculate_changes(rep.id, user_id, db)
            changes = db.query(HealthChange).filter(HealthChange.user_id == user_id).all()

    results = []
    has_updates = False
    
    for c in changes:
        abs_c = round(c.absolute_change, 3) if c.absolute_change is not None else 0.0
        pct_c = round(c.percentage_change, 3) if c.percentage_change is not None else 0.0
        prev_v = round(c.previous_value, 3) if c.previous_value is not None else None
        curr_v = round(c.current_value, 3) if c.current_value is not None else None
        
        curr_st = c.current_status
        if not curr_st or curr_st.upper() == 'UNKNOWN':
            ref = find_reference_range(c.test_name, db)
            if ref and curr_v is not None:
                curr_st = classify_result(curr_v, ref.low, ref.high)
                c.current_status = curr_st
                has_updates = True
                
        prev_st = c.previous_status
        if not prev_st or prev_st.upper() == 'UNKNOWN':
            ref = find_reference_range(c.test_name, db)
            if ref and prev_v is not None:
                prev_st = classify_result(prev_v, ref.low, ref.high)
                c.previous_status = prev_st
                has_updates = True

        effective_status = curr_st if curr_st and curr_st.upper() != 'UNKNOWN' else "NORMAL"

        results.append({
            "id": c.id,
            "user_id": c.user_id,
            "report_id": c.report_id,
            "test_name": c.test_name,
            "previous_value": prev_v,
            "current_value": curr_v,
            "absolute_change": abs_c,
            "percentage_change": pct_c,
            "direction": c.direction,
            "previous_status": prev_st,
            "current_status": effective_status,
            "status": effective_status,
        })
        
    if has_updates:
        try:
            db.commit()
        except Exception:
            db.rollback()
            
    return results
