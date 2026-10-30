import sys
sys.path.append('d:/New folder/healthlens/backend/app')
from database import SessionLocal
from models.test_result import TestResult
from services.ai_service import generate_test_explanation

db = SessionLocal()
results = db.query(TestResult).filter(TestResult.status.in_(['HIGH', 'LOW'])).all()
count = 0
for r in results:
    if 'lifestyle and dietary changes' not in r.ai_explanation.lower() and 'natural remedies' not in r.ai_explanation.lower():
        print(f'Regenerating {r.test_name}...')
        new_exp = generate_test_explanation(r.test_name, r.value, r.unit, r.reference_low, r.reference_high, r.status)
        r.ai_explanation = new_exp
        db.commit()
        count += 1
print(f'Fixed {count} HIGH/LOW records with new prompt.')
