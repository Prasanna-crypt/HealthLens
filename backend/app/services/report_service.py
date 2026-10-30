# TODO: Might need a cleanup later.

import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.report import Report
from ..models.test_result import TestResult
from ..config import settings
from .ocr_service import extract_text
from .extraction_service import extract_test_results
from .classification_service import classify_all_results
from .ai_service import generate_report_summary, generate_test_explanation

def process_report(file_bytes: bytes, filename: str, file_type: str, user_id: int, db: Session) -> Report:
    # Step 1: Save the uploaded file to the hard drive
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    # Use uuid to give it a unique random name so files don't overwrite each other
    saved_filename = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, saved_filename)
    
    with open(filepath, "wb") as f:
        f.write(file_bytes)
        
    # Step 2: Run OCR to read text from the image
    ocr_lines = extract_text(file_bytes, file_type)
    
    # Step 3: Extract actual test numbers from the raw text using Regex
    raw_results = extract_test_results(ocr_lines)
    
    # Step 4: Classify results as LOW, NORMAL, or HIGH
    classified_results = classify_all_results(raw_results, db)
    
    # Step 5: Ask the AI to write a summary of the whole report
    summary = generate_report_summary(classified_results)
    
    # Count how many tests fall into each category
    normal_c = sum(1 for r in classified_results if r['status'] == 'NORMAL')
    low_c = sum(1 for r in classified_results if r['status'] == 'LOW')
    high_c = sum(1 for r in classified_results if r['status'] == 'HIGH')
    
    # Step 6: Save the main Report details to the database
    report = Report(
        user_id=user_id,
        filename=filename,
        report_date=datetime.utcnow().strftime("%Y-%m-%d"),
        ai_summary=summary,
        total_tests=len(classified_results),
        normal_count=normal_c,
        low_count=low_c,
        high_count=high_c
    )
    db.add(report)
    db.commit()
    db.refresh(report) # Refresh to get the new ID from the database
    
    # Step 7: Save each individual test result and get AI explanations for them
    for r in classified_results:
        exp = generate_test_explanation(r['test_name'], r['value'], r['unit'], r.get('reference_low'), r.get('reference_high'), r['status'])
        tr = TestResult(
            report_id=report.id,
            test_name=r['test_name'],
            value=r['value'],
            unit=r['unit'],
            reference_low=r.get('reference_low'),
            reference_high=r.get('reference_high'),
            status=r['status'],
            ocr_confidence=r.get('confidence'),
            ai_explanation=exp
        )
        db.add(tr)
        
    db.commit()
    db.refresh(report)

    # Core Feature Integration
    from .pattern_service import detect_patterns
    from .comparison_service import calculate_changes
    detect_patterns(report.id, user_id, db)
    calculate_changes(report.id, user_id, db)
    
    return report

def process_demo_report(data: dict, user_id: int, db: Session) -> Report:
    # Used for loading fake demo data into the dashboard for testing
    report = Report(
        user_id=user_id,
        filename=data['title'],
        report_date=data['date'],
        patient_name=data['patient'],
        ai_summary=data['summary'],
        total_tests=len(data['tests']),
        is_demo=True
    )
    
    normal = sum(1 for t in data['tests'] if t['status'] == 'NORMAL')
    low = sum(1 for t in data['tests'] if t['status'] == 'LOW')
    high = sum(1 for t in data['tests'] if t['status'] == 'HIGH')
    report.normal_count = normal
    report.low_count = low
    report.high_count = high
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    for t in data['tests']:
        tr = TestResult(
            report_id=report.id,
            test_name=t['test_name'],
            value=t['value'],
            unit=t['unit'],
            reference_low=t.get('ref_low'),
            reference_high=t.get('ref_high'),
            status=t['status'],
            ai_explanation=f"Demo explanation for {t['test_name']}"
        )
        db.add(tr)
    db.commit()
    db.refresh(report)
    return report
