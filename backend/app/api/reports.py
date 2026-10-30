# TODO: Might need a cleanup later.

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.report import Report
from ..models.test_result import TestResult
from ..schemas.report import ReportResponse, ReportListResponse
from ..utils.security import get_current_user
from ..services.report_service import process_report
from ..services.classification_service import find_reference_range, classify_all_results
from ..services.ai_service import generate_report_summary, generate_test_explanation
from ..services.pattern_service import detect_patterns
from ..services.comparison_service import calculate_changes

router = APIRouter()

# Upload Endpoint: Receives an image and triggers the entire processing pipeline
@router.post("/upload", response_model=ReportResponse)
async def upload_report(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Ensure it's an image or PDF
    allowed_types = {"image/jpeg", "image/png", "image/jpg", "application/pdf"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    contents = await file.read()
    
    # Prevent massive files from crashing the server
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB).")

    return process_report(contents, file.filename or "report", file.content_type or "", current_user.id, db)


@router.post("/extract")
async def extract_report_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Extracts data for user review prior to saving
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB).")

    from ..services.ocr_service import extract_text
    from ..services.extraction_service import extract_test_results
    from ..services.quality_service import check_report_quality

    try:
        ocr_lines = extract_text(contents, file.content_type, file.filename)
        raw_results = extract_test_results(ocr_lines)
        classified_results = classify_all_results(raw_results, db)
        issues = check_report_quality(classified_results)

        return {
            "extracted_results": classified_results,
            "quality_issues": issues,
            "filename": file.filename
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


class SaveReportRequest(BaseModel):
    filename: str
    results: List[Any]

@router.post("/save", response_model=ReportResponse)
def save_extracted_report(
    request: SaveReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    final_results = classify_all_results(request.results, db)
    
    summary = generate_report_summary(final_results)
    normal_c = sum(1 for r in final_results if r.get('status') == 'NORMAL')
    low_c = sum(1 for r in final_results if r.get('status') == 'LOW')
    high_c = sum(1 for r in final_results if r.get('status') == 'HIGH')
    
    report = Report(
        user_id=current_user.id,
        filename=request.filename,
        report_date=datetime.utcnow().strftime("%Y-%m-%d"),
        ai_summary=summary,
        total_tests=len(final_results),
        normal_count=normal_c,
        low_count=low_c,
        high_count=high_c
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    for r in final_results:
        status = r.get('status', 'UNKNOWN')
        name = r.get('test_name', 'Unknown')
        val = r.get('value', 0.0)
        u = r.get('unit', '')
        r_low = r.get('reference_low')
        r_high = r.get('reference_high')

        # Instant High-Speed Explanation: medically grounded, natural remedies only, zero latency
        exp = generate_test_explanation(name, val, u, r_low, r_high, status)

        tr = TestResult(
            report_id=report.id,
            test_name=name,
            value=val,
            unit=u,
            reference_low=r_low,
            reference_high=r_high,
            status=status,
            ocr_confidence=r.get('ocr_confidence', 1.0),
            ai_explanation=exp
        )
        db.add(tr)
        
    db.commit()
    db.refresh(report)

    detect_patterns(report.id, current_user.id, db)
    calculate_changes(report.id, current_user.id, db)
    
    return report


# List Endpoint: Get all reports belonging to the current user
@router.get("/", response_model=List[ReportListResponse])
def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Report)
        .filter(Report.user_id == current_user.id)
        .order_by(Report.upload_date.desc())
        .all()
    )


# Compare Endpoint: Show two reports side-by-side and calculate differences
@router.get("/compare")
def compare_reports(
    report1_id: int,
    report2_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    r1 = db.query(Report).filter(Report.id == report1_id, Report.user_id == current_user.id).first()
    r2 = db.query(Report).filter(Report.id == report2_id, Report.user_id == current_user.id).first()
    if not r1 or not r2:
        raise HTTPException(status_code=404, detail="One or both reports not found")

    r1_tests = {tr.test_name: tr for tr in r1.test_results}
    r2_tests = {tr.test_name: tr for tr in r2.test_results}

    all_test_names = set(r1_tests.keys()) | set(r2_tests.keys())
    comparisons = []
    
    for name in sorted(all_test_names):
        t1 = r1_tests.get(name)
        t2 = r2_tests.get(name)
        if t1 and t2:
            comparisons.append({
                "test_name": name,
                "report1_value": t1.value,
                "report1_unit": t1.unit,
                "report1_status": t1.status,
                "report2_value": t2.value,
                "report2_unit": t2.unit,
                "report2_status": t2.status,
                "change": round(t2.value - t1.value, 3),
            })

    return {
        "report1": {"id": r1.id, "filename": r1.filename, "report_date": r1.report_date, "upload_date": r1.upload_date.isoformat() if r1.upload_date else ""},
        "report2": {"id": r2.id, "filename": r2.filename, "report_date": r2.report_date, "upload_date": r2.upload_date.isoformat() if r2.upload_date else ""},
        "comparisons": comparisons,
    }


# Get Single Report Endpoint: Load the full details of a specific report
@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    for tr in report.test_results:
        if not tr.unit or str(tr.unit).strip() in ("", "—"):
            ref = find_reference_range(tr.test_name, db)
            if ref and ref.unit:
                tr.unit = ref.unit
                
    return report


# Delete Endpoint: Remove a report and all its results
@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return {"status": "deleted", "id": report_id}
