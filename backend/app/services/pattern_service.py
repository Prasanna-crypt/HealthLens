import json
from sqlalchemy.orm import Session
from ..models.health import HealthPattern
from ..models.report import Report
from ..models.test_result import TestResult
from ..utils.test_name_normalizer import normalize_test_name
from .classification_service import find_reference_range, classify_result


def _get_status(test_item, db: Session) -> str:
    status = getattr(test_item, 'status', None)
    if not status or status.upper() == 'UNKNOWN':
        ref = find_reference_range(test_item.test_name, db)
        if ref and test_item.value is not None:
            status = classify_result(test_item.value, ref.low, ref.high)
    return (status or 'NORMAL').upper()


def _format_observed(tests: list[TestResult], db: Session) -> str:
    parts = []
    for t in tests:
        st = _get_status(t, db)
        unit_str = f" {t.unit}" if t.unit else ""
        parts.append(f"{t.test_name}: {t.value}{unit_str} ({st.capitalize()})")
    return ", ".join(parts)


def evaluate_biomarker_patterns(tests_by_name: dict[str, TestResult], db: Session) -> list[dict]:
    patterns = []

    # 1. Renal Function & Filtration Stress Pattern
    kidney_keys = ['Creatinine', 'BUN', 'Uric Acid']
    found_kidney = [tests_by_name[k] for k in kidney_keys if k in tests_by_name]
    if len(found_kidney) >= 2:
        abnormal_kidney = [t for t in found_kidney if _get_status(t, db) in ('HIGH', 'LOW')]
        if abnormal_kidney or any(_get_status(t, db) == 'HIGH' for t in found_kidney):
            has_high_cr = any(normalize_test_name(t.test_name) == 'Creatinine' and _get_status(t, db) == 'HIGH' for t in found_kidney)
            has_high_bun = any(normalize_test_name(t.test_name) == 'BUN' and _get_status(t, db) == 'HIGH' for t in found_kidney)
            severity = 'High' if (has_high_cr and has_high_bun) else 'Medium'
            patterns.append({
                "pattern_name": "Renal Clearance & Kidney Stress Pattern",
                "related_tests": [t.test_name for t in found_kidney],
                "observed_values": _format_observed(found_kidney, db),
                "explanation": "Concomitant elevation in serum creatinine, blood urea nitrogen (BUN), or uric acid points to reduced glomerular filtration rate, nitrogenous waste buildup, or acute renal strain.",
                "severity": severity,
                "recommended_discussion": "Review hydration, check estimated GFR (eGFR), assess blood pressure, and review any nephrotoxic medications such as NSAIDs."
            })

    # 2. Hepatic Cellular Stress & Liver Enzyme Pattern
    liver_keys = ['ALT', 'AST', 'Total Bilirubin', 'ALP', 'Albumin']
    found_liver = [tests_by_name[k] for k in liver_keys if k in tests_by_name]
    if len(found_liver) >= 2:
        abnormal_liver = [t for t in found_liver if _get_status(t, db) in ('HIGH', 'LOW')]
        if abnormal_liver:
            has_high_alt = any(normalize_test_name(t.test_name) == 'ALT' and _get_status(t, db) == 'HIGH' for t in found_liver)
            has_high_ast = any(normalize_test_name(t.test_name) == 'AST' and _get_status(t, db) == 'HIGH' for t in found_liver)
            severity = 'High' if (has_high_alt and has_high_ast) else 'Medium'
            patterns.append({
                "pattern_name": "Hepatic Cellular Stress Pattern",
                "related_tests": [t.test_name for t in found_liver],
                "observed_values": _format_observed(found_liver, db),
                "explanation": "Elevated hepatocellular transaminases (ALT/AST) or biliary markers reflect hepatic cellular stress, metabolic fatty liver changes, or bile flow congestion.",
                "severity": severity,
                "recommended_discussion": "Discuss liver ultrasound imaging, review alcohol or medication consumption, and discuss lifestyle modifications for liver health."
            })

    # 3. Cardiovascular & Atherogenic Lipid Risk Pattern
    lipid_keys = ['Total Cholesterol', 'LDL Cholesterol', 'HDL Cholesterol', 'Triglycerides']
    found_lipids = [tests_by_name[k] for k in lipid_keys if k in tests_by_name]
    if len(found_lipids) >= 2:
        abnormal_lipids = [t for t in found_lipids if _get_status(t, db) in ('HIGH', 'LOW')]
        if abnormal_lipids:
            has_high_ldl = any(normalize_test_name(t.test_name) == 'LDL Cholesterol' and _get_status(t, db) == 'HIGH' for t in found_lipids)
            has_high_tc = any(normalize_test_name(t.test_name) == 'Total Cholesterol' and _get_status(t, db) == 'HIGH' for t in found_lipids)
            severity = 'High' if (has_high_ldl and has_high_tc) else 'Medium'
            patterns.append({
                "pattern_name": "Atherogenic Lipid & Cardiovascular Risk",
                "related_tests": [t.test_name for t in found_lipids],
                "observed_values": _format_observed(found_lipids, db),
                "explanation": "Elevated LDL cholesterol or triglycerides combined with reduced HDL cholesterol promotes arterial endothelial plaque accumulation.",
                "severity": severity,
                "recommended_discussion": "Evaluate 10-year ASCVD cardiovascular risk score, emphasize heart-healthy omega-rich nutrition, and consider medical lipid therapy if indicated."
            })

    # 4. Metabolic Health & Glycemic Risk Pattern
    glycemic_keys = ['Fasting Blood Glucose', 'HbA1c', 'Triglycerides', 'HDL Cholesterol']
    found_glycemic = [tests_by_name[k] for k in glycemic_keys if k in tests_by_name]
    if any(k in tests_by_name for k in ['Fasting Blood Glucose', 'HbA1c']):
        glucose_t = tests_by_name.get('Fasting Blood Glucose')
        hba1c_t = tests_by_name.get('HbA1c')
        is_high_g = glucose_t and _get_status(glucose_t, db) == 'HIGH'
        is_high_a1c = hba1c_t and _get_status(hba1c_t, db) == 'HIGH'
        if is_high_g or is_high_a1c:
            severity = 'High' if (is_high_a1c or (glucose_t and glucose_t.value and glucose_t.value >= 126)) else 'Medium'
            patterns.append({
                "pattern_name": "Glycemic Dysregulation & Insulin Resistance Pattern",
                "related_tests": [t.test_name for t in found_glycemic],
                "observed_values": _format_observed(found_glycemic, db),
                "explanation": "Elevated fasting blood sugar or glycated hemoglobin demonstrates reduced cellular insulin sensitivity and impaired glucose homeostasis.",
                "severity": severity,
                "recommended_discussion": "Discuss dietary glycemic load reduction, regular post-meal physical activity, and consider fasting insulin or continuous glucose monitoring."
            })

    # 5. Thyroid Endocrine Axis Modulation
    thyroid_keys = ['TSH', 'Free T4', 'T3', 'T4']
    found_thyroid = [tests_by_name[k] for k in thyroid_keys if k in tests_by_name]
    if found_thyroid:
        abnormal_thyroid = [t for t in found_thyroid if _get_status(t, db) in ('HIGH', 'LOW')]
        if abnormal_thyroid:
            tsh_t = tests_by_name.get('TSH')
            is_high_tsh = tsh_t and _get_status(tsh_t, db) == 'HIGH'
            is_low_tsh = tsh_t and _get_status(tsh_t, db) == 'LOW'
            subtype = "Hypothyroid Tendency" if is_high_tsh else ("Hyperthyroid Tendency" if is_low_tsh else "Thyroid Axis Shift")
            severity = 'High' if (tsh_t and (tsh_t.value >= 10.0 or tsh_t.value <= 0.1)) else 'Medium'
            patterns.append({
                "pattern_name": f"Thyroid Axis Pattern ({subtype})",
                "related_tests": [t.test_name for t in found_thyroid],
                "observed_values": _format_observed(found_thyroid, db),
                "explanation": f"Abnormal pituitary TSH regulation alongside circulating thyroid hormones indicates altered metabolic thyroid signaling ({subtype.lower()}).",
                "severity": severity,
                "recommended_discussion": "Discuss anti-thyroid peroxidase (TPO) antibodies, symptom assessment (fatigue, weight, temperature sensitivity), and follow-up panel."
            })

    # 6. Hematologic & Red Cell Pattern (Anemia / Microcytosis)
    cbc_red_keys = ['Hemoglobin', 'Hematocrit', 'MCV', 'MCH', 'RBC']
    found_red = [tests_by_name[k] for k in cbc_red_keys if k in tests_by_name]
    if len(found_red) >= 2:
        abnormal_red = [t for t in found_red if _get_status(t, db) in ('HIGH', 'LOW')]
        if abnormal_red:
            has_low_hb = any(normalize_test_name(t.test_name) == 'Hemoglobin' and _get_status(t, db) == 'LOW' for t in found_red)
            has_low_mcv = any(normalize_test_name(t.test_name) == 'MCV' and _get_status(t, db) == 'LOW' for t in found_red)
            severity = 'High' if (has_low_hb and has_low_mcv) else 'Medium'
            patterns.append({
                "pattern_name": "Erythrocyte Oxygen-Carrying Capacity Shift (Anemia Risk)",
                "related_tests": [t.test_name for t in found_red],
                "observed_values": _format_observed(found_red, db),
                "explanation": "Decreased hemoglobin or red blood cell indices (MCV/MCH) indicates diminished oxygen-carrying capacity, microcytosis, or iron utilization changes.",
                "severity": severity,
                "recommended_discussion": "Check serum ferritin, iron saturation, and vitamin B12 levels before initiating supplementation."
            })

    # 7. Immune System & Leukocyte Activation Pattern
    white_keys = ['WBC', 'Lymphocytes', 'Neutrophils', 'Monocytes', 'Basophils', 'Eosinophils']
    found_white = [tests_by_name[k] for k in white_keys if k in tests_by_name]
    if len(found_white) >= 2:
        abnormal_white = [t for t in found_white if _get_status(t, db) in ('HIGH', 'LOW')]
        if abnormal_white:
            severity = 'Medium'
            patterns.append({
                "pattern_name": "Leukocyte Differential & Immune Response Pattern",
                "related_tests": [t.test_name for t in found_white],
                "observed_values": _format_observed(found_white, db),
                "explanation": "Differential shifts in white blood cell subsets reflect active immune surveillance, reactive leukocyte proliferation, or resolving inflammation.",
                "severity": severity,
                "recommended_discussion": "Correlate with recent viral or bacterial symptoms, allergies, or physical stress."
            })

    return patterns


def detect_patterns(report_id: int, user_id: int, db: Session):
    """Detects patterns for a specific report and persists them."""
    tests = db.query(TestResult).filter(TestResult.report_id == report_id).all()
    if not tests:
        return
        
    tests_by_name = {normalize_test_name(t.test_name): t for t in tests}
    patterns = evaluate_biomarker_patterns(tests_by_name, db)
    
    for p in patterns:
        db_pattern = HealthPattern(
            user_id=user_id,
            report_id=report_id,
            pattern_name=p["pattern_name"],
            related_tests=json.dumps(p["related_tests"]),
            explanation=p["explanation"],
            severity=p["severity"],
            recommended_discussion=p["recommended_discussion"]
        )
        db.add(db_pattern)
    db.commit()


def get_user_patterns(user_id: int, db: Session):
    """
    Evaluates patterns across all user lab results to present a comprehensive,
    multi-report health pattern analysis.
    """
    tests = (
        db.query(TestResult)
        .join(Report, TestResult.report_id == Report.id)
        .filter(Report.user_id == user_id)
        .order_by(Report.report_date.desc(), Report.id.desc())
        .all()
    )
    
    if not tests:
        return []

    # Map latest test by normalized name
    tests_by_name = {}
    for t in tests:
        norm = normalize_test_name(t.test_name)
        if norm not in tests_by_name:
            tests_by_name[norm] = t

    return evaluate_biomarker_patterns(tests_by_name, db)
