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

def find_reference_range(test_name: str, db: Session) -> ReferenceRange | None:
    """
    Searches the database for the normal range of a test.
    Tries three ways: exact name, normalized name, and known aliases.
    Returns a ReferenceRange object or None if not found.
    """
    if not test_name:
        return None

    # Try 1: Exact name match (e.g. "Hemoglobin")
    result = db.query(ReferenceRange).filter(ReferenceRange.test_name == test_name).first()
    if result:
        return result

    # Try 2: Normalized name (e.g. "Hb" → "Hemoglobin")
    normalized = normalize_test_name(test_name)
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
