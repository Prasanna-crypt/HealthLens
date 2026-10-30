import json
from sqlalchemy.orm import Session
from ..models.health import HealthPattern
from ..models.test_result import TestResult

def detect_patterns(report_id: int, user_id: int, db: Session):
    tests = db.query(TestResult).filter(TestResult.report_id == report_id).all()
    test_dict = {t.test_name.lower(): t for t in tests}
    
    patterns = []
    
    # Rule 1: Lipid panel
    lipid_tests = {'cholesterol', 'triglycerides', 'hdl', 'ldl'}
    found_lipids = lipid_tests.intersection(test_dict.keys())
    if len(found_lipids) >= 2:
        patterns.append({
            "pattern_name": "Lipid Panel",
            "related_tests": json.dumps(list(found_lipids)),
            "explanation": "Multiple lipid tests detected. This indicates an assessment of cardiovascular health.",
            "severity": "Info"
        })
        
    # Rule 2: Diabetes
    diabetes_tests = {'glucose', 'hba1c'}
    found_diabetes = diabetes_tests.intersection(test_dict.keys())
    if len(found_diabetes) == 2:
        patterns.append({
            "pattern_name": "Diabetes Indicator",
            "related_tests": json.dumps(list(found_diabetes)),
            "explanation": "Both Glucose and HbA1c are present, indicating a blood sugar evaluation.",
            "severity": "Medium"
        })
        
    for p in patterns:
        db_pattern = HealthPattern(
            user_id=user_id,
            report_id=report_id,
            pattern_name=p["pattern_name"],
            related_tests=p["related_tests"],
            explanation=p["explanation"],
            severity=p["severity"]
        )
        db.add(db_pattern)
    db.commit()

def get_user_patterns(user_id: int, db: Session):
    return db.query(HealthPattern).filter(HealthPattern.user_id == user_id).all()
