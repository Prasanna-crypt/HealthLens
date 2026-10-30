from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append(r"d:\New folder\healthlens\backend")
from app.config import settings
from app.models.report import Report
from app.models.test_result import TestResult

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

reports = db.query(Report).order_by(Report.id.desc()).limit(3).all()
for r in reports:
    print(f"Report ID: {r.id}, Name: {r.filename}, Total Tests: {r.total_tests}, Normal: {r.normal_count}, Low: {r.low_count}")
    tests = db.query(TestResult).filter(TestResult.report_id == r.id).all()
    if tests:
        print(f"  First test: {tests[0].test_name} = {tests[0].value} {tests[0].unit}")
