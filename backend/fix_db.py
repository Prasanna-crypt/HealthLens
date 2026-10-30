import sys
sys.path.append('app')
from app.database import SessionLocal
from app.models.test_result import TestResult
from app.services.ai_service import generate_test_explanation

db = SessionLocal()
# Fetch test results that failed
results = db.query(TestResult).filter(TestResult.ai_explanation.like('%Explanation unavailable%')).all()
count = 0
for r in results:
    print(f'Regenerating {r.test_name}...')
    new_exp = generate_test_explanation(r.test_name, r.value, r.unit, r.reference_low, r.reference_high, r.status)
    r.ai_explanation = new_exp
    db.commit()
    count += 1
print(f'Fixed {count} records.')
