import json
from sqlalchemy.orm import Session
from ..models.reference_range import ReferenceRange
from ..utils.test_name_normalizer import normalize_test_name


# ── Step 1: Decide if a result is NORMAL, LOW, or HIGH ──────────────────────

def classify_result(value: float | None, low: float | None, high: float | None) -> str:
    """
    Compares a test value against its normal reference range.
    Returns 'LOW', 'HIGH', 'NORMAL', or 'UNKNOWN' if no range is available.
    Safely handles None, string numbers, or unparseable ranges without crashing.
    """
    if value is None or low is None or high is None:
        return "UNKNOWN"
    try:
        val_f = float(value)
        low_f = float(low)
        high_f = float(high)
        if val_f < low_f:
            return "LOW"
        if val_f > high_f:
            return "HIGH"
        return "NORMAL"
    except (ValueError, TypeError):
        return "UNKNOWN"


# ── Step 2: Look up reference range from the database ───────────────────────

class FallbackRange:
    def __init__(self, low: float, high: float, unit: str, category: str = "General", source: str = "MedlinePlus"):
        self.low = low
        self.high = high
        self.unit = unit
        self.category = category
        self.source = source

DEFAULT_FALLBACK_RANGES = {
    "Hemoglobin": (12.0, 17.5, "g/dL", "CBC"),
    "WBC": (4500, 11000, "/µL", "CBC"),
    "RBC": (4.2, 5.7, "million/µL", "CBC"),
    "Platelets": (150000, 400000, "/µL", "CBC"),
    "Hematocrit": (36.0, 48.0, "%", "CBC"),
    "MCV": (80.0, 100.0, "fL", "CBC"),
    "MCH": (27.0, 33.0, "pg", "CBC"),
    "MCHC": (32.0, 36.0, "g/dL", "CBC"),
    "Lymphocytes": (20.0, 40.0, "%", "CBC"),
    "Monocytes": (2.0, 8.0, "%", "CBC"),
    "Basophils": (0.0, 2.0, "%", "CBC"),
    "Neutrophils": (40.0, 70.0, "%", "CBC"),
    "Eosinophils": (1.0, 4.0, "%", "CBC"),
    "Total Cholesterol": (0.0, 200.0, "mg/dL", "Lipid Profile"),
    "LDL Cholesterol": (0.0, 100.0, "mg/dL", "Lipid Profile"),
    "HDL Cholesterol": (40.0, 60.0, "mg/dL", "Lipid Profile"),
    "Triglycerides": (0.0, 150.0, "mg/dL", "Lipid Profile"),
    "Fasting Blood Glucose": (70.0, 100.0, "mg/dL", "Blood Glucose"),
    "HbA1c": (4.0, 5.7, "%", "Blood Glucose"),
    "ALT": (4.0, 36.0, "U/L", "Liver Function"),
    "AST": (8.0, 33.0, "U/L", "Liver Function"),
    "Total Bilirubin": (0.1, 1.2, "mg/dL", "Liver Function"),
    "Albumin": (3.4, 5.4, "g/dL", "Liver Function"),
    "ALP": (44.0, 147.0, "U/L", "Liver Function"),
    "Creatinine": (0.6, 1.2, "mg/dL", "Kidney Function"),
    "BUN": (6.0, 20.0, "mg/dL", "Kidney Function"),
    "Uric Acid": (3.0, 7.0, "mg/dL", "Kidney Function"),
    "TSH": (0.4, 4.0, "mIU/L", "Thyroid"),
    "T3": (80.0, 200.0, "ng/dL", "Thyroid"),
    "T4": (5.0, 12.0, "µg/dL", "Thyroid"),
    "Free T4": (0.8, 1.8, "ng/dL", "Thyroid"),
}

def find_reference_range(test_name: str, db: Session) -> ReferenceRange | FallbackRange | None:
    """
    Searches the database for the normal range of a test.
    Tries three ways: exact name, normalized name, and known aliases.
    Falls back to medical standard reference dictionary if not found in db.
    """
    if not test_name:
        return None

    normalized = normalize_test_name(test_name)

    # Try 1: Exact name match (e.g. "Hemoglobin")
    result = db.query(ReferenceRange).filter(ReferenceRange.test_name == test_name).first()
    if result:
        return result

    # Try 2: Normalized name (e.g. "Hb" → "Hemoglobin")
    if normalized != test_name:
        result = db.query(ReferenceRange).filter(ReferenceRange.test_name == normalized).first()
        if result:
            return result

    # Try 3: Check all aliases (e.g. "HGB" is an alias for "Hemoglobin")
    all_ranges = db.query(ReferenceRange).all()
    name_lower = test_name.lower().strip()

    for ref in all_ranges:
        if not ref.aliases:
            continue
        try:
            aliases = json.loads(ref.aliases) if isinstance(ref.aliases, str) else ref.aliases
            for alias in aliases:
                if str(alias).lower().strip() == name_lower:
                    return ref
        except Exception:
            pass

    # Try 4: Medical standard reference fallback dictionary
    if normalized in DEFAULT_FALLBACK_RANGES:
        low, high, unit, cat = DEFAULT_FALLBACK_RANGES[normalized]
        return FallbackRange(low=low, high=high, unit=unit, category=cat)

    return None  # Not found anywhere


# ── Step 3: Classify all tests in a report ──────────────────────────────────

def classify_all_results(test_results: list[dict], db: Session) -> list[dict]:
    """
    High-speed classification:
    1. Checks the local SQLite reference database first (instantaneous <5ms).
    2. Only invokes AI for tests that still lack units or ranges after DB lookup.
    3. Safely labels each test as NORMAL, LOW, HIGH, or UNKNOWN.
    """
    classified = []
    unresolved_tests = []

    # Fast Pass: Check document values and local database
    for test in test_results:
        # Note: Must use 'if x is not None' because 0.0 is falsy in Python!
        low = test.get("report_ref_low") if test.get("report_ref_low") is not None else test.get("reference_low")
        high = test.get("report_ref_high") if test.get("report_ref_high") is not None else test.get("reference_high")
        unit = test.get("unit") or ""

        db_ref = find_reference_range(test.get("test_name", ""), db)
        if db_ref:
            if low is None:
                low = db_ref.low
            if high is None:
                high = db_ref.high
            if not unit and db_ref.unit:
                unit = db_ref.unit

        test["unit"] = unit
        test["reference_low"] = low
        test["reference_high"] = high

        # If still missing unit or range, queue for AI enhancement
        if not unit or low is None or high is None:
            unresolved_tests.append(test)

        classified.append(test)

    # Selective AI Pass: Only if any test is still missing metadata
    if unresolved_tests:
        try:
            from .ai_service import ai_enhance_test_metadata
            ai_enhance_test_metadata(unresolved_tests)
        except Exception as e:
            print(f"[HealthLens] AI fill skipped: {e}")

    # Final Pass: Label statuses
    for test in classified:
        low = test.get("reference_low")
        high = test.get("reference_high")
        test["status"] = classify_result(test.get("value"), low, high)

    return classified
