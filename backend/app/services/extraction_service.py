import re
from ..utils.test_name_normalizer import normalize_test_name, normalize_unit


# ── Known medical units ──────────────────────────────────────────────────────
# If a line contains any of these, it is probably a test result row.
KNOWN_UNITS = [
    "g/dL", "g/dl", "mg/dL", "mg/dl",
    "U/L", "u/l", "IU/L", "iu/l",
    "%",
    "/µL", "/uL", "/ul", "/mcL", "/cumm",
    "million/µL", "million/uL", "mill/µL", "mill/cumm",
    "10^3/µL", "10^3/uL", "x10^3/uL", "thou/µL", "thou/cumm",
    "10^6/µL", "10^6/uL", "x10^6/uL",
    "fL", "fl",
    "pg", "pg/cell",
    "mIU/L", "miu/l", "uIU/mL", "µIU/mL",
    "ng/dL", "ng/dl", "ng/mL", "ng/ml",
    "µg/dL", "ug/dl", "mcg/dL", "mcg/dl",
    "mmol/L", "mmol/l",
    "mEq/L", "meq/l",
    "mm/hr", "mm/h",
    "mg/L", "mg/l",
    "pg/mL", "pg/ml",
    "cells/µL", "cells/uL", "cells/cumm",
    "g/L", "g/l",
    "sec", "seconds", "ratio",
    "copies/mL", "log copies/mL",
    "lakhs/cumm", "lakh/cumm", "lacs/cumm",
    "million/cumm", "gm/dl", "gm/dL", "gms/dl",
    "thou/cumm", "thousand/uL",
]

# ── Noise patterns ───────────────────────────────────────────────────────────
# Lines matching any of these patterns are NOT test results — skip them.
NOISE_PATTERNS = [
    r"^\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}$",   # dates like 01/02/2024
    r"^page\s*\d",                                  # page numbers
    r"^\d{10}$",                                    # phone numbers
    r"^(dr|doctor|mr|mrs|ms|patient|name|age|sex|gender|ref|referred)\b",
    r"^(date|time|sample|collected|received|reported|lab|laboratory|hospital|clinic)\b",
    r"^(address|phone|tel|fax|email|www|http)\b",
    r"^(test\s+name|investigation|parameter|result|unit|reference|normal|range|method)\b",
    r"^\*",
    r"^[-=_]{3,}$",
    r"^(end of report|report generated|printed|authenticated|verified|signature)\b",
]

# Pre-compile for speed
_noise_regexes = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]

# Pattern to find reference ranges like "12.0 - 17.5" or "12.0 – 17.5"
REF_RANGE_PATTERN = re.compile(r"(\d+\.?\d*)\s*[-–—to]+\s*(\d+\.?\d*)")


# ── Helper: Check if a line is noise ────────────────────────────────────────

def is_noise_line(text: str) -> bool:
    """Returns True if this line is a header, date, or other non-test text."""
    clean = text.strip()
    if len(clean) < 3:
        return True
    for pattern in _noise_regexes:
        if pattern.search(clean):
            return True
    return False


# ── Helper: Find unit in text ────────────────────────────────────────────────

def find_unit(text: str) -> tuple[str | None, int, int]:
    """
    Looks for a known medical unit inside the text.
    Checks longest units first to avoid partial matches (e.g. 'million/µL' before '/µL').
    Returns (unit_string, start_position, end_position) or (None, -1, -1).
    """
    units_by_length = sorted(KNOWN_UNITS, key=len, reverse=True)
    text_lower = text.lower()
    for unit in units_by_length:
        pos = text_lower.find(unit.lower())
        if pos != -1:
            return unit, pos, pos + len(unit)
    return None, -1, -1


# ── Helper: Find reference range in text ────────────────────────────────────

def find_reference_range(text: str) -> tuple[float | None, float | None]:
    """
    Finds a printed reference range like '13.0 - 17.5' in the text.
    Returns (low, high) as floats, or (None, None) if not found.
    """
    matches = REF_RANGE_PATTERN.findall(text)
    for match in matches:
        try:
            low  = float(match[0])
            high = float(match[1])
            if low < high:   # Makes sure it's a valid range
                return low, high
        except ValueError:
            continue
    return None, None


# ── Helper: Parse one OCR line into a test result ───────────────────────────

def parse_single_line(text: str, confidence: float) -> dict | None:
    """
    Tries to read one line of OCR text as a test result.

    Handles formats like:
        'Hemoglobin  14.5  g/dL  12.0 - 17.5'
        'SGPT (ALT)  45  U/L  4 - 36'
        'Vitamin B12  450  pg/mL'
    Returns a dict with test_name, value, unit, etc. or None if not a test.
    """
    if is_noise_line(text):
        return None

    # Find all numbers in the line (the value will be one of them)
    numbers = list(re.finditer(r"(?<![a-zA-Z])(\d+\.?\d*)(?![a-zA-Z\d])", text))
    if not numbers:
        return None

    unit, _, _ = find_unit(text)
    ref_low, ref_high = find_reference_range(text)

    # The test value is the first number that is NOT part of the reference range
    test_value = None
    value_position = -1
    for number in numbers:
        num = float(number.group(1))
        if ref_low  is not None and abs(num - ref_low)  < 0.001:
            continue  # This number is the reference low — skip
        if ref_high is not None and abs(num - ref_high) < 0.001:
            continue  # This number is the reference high — skip
        test_value = num
        value_position = number.start()
        break

    # If we couldn't separate the value, just use the first number
    if test_value is None and numbers:
        test_value = float(numbers[0].group(1))
        value_position = numbers[0].start()

    if test_value is None:
        return None

    # Everything before the value number is the test name
    raw_name = text[:value_position].strip()
    raw_name = re.sub(r"[:\-|]+$", "", raw_name).strip()   # Remove trailing colons/dashes
    raw_name = re.sub(r"\(\s*\)$", "", raw_name).strip()   # Remove empty parentheses

    # Reject if the name has no letters (it's probably a number or noise)
    if not raw_name or not re.search(r"[a-zA-Z]", raw_name):
        return None

    # Reject if the name looks like clinical prose / long sentences rather than a biomarker name
    if len(raw_name) > 55 or len(raw_name.split()) > 6:
        return None

    # Reject if the name looks like a date (e.g. '14/02')
    if re.match(r"^\d+[/\-\.]\d+", raw_name):
        return None

    # If no unit was found, only keep this result if we have a reference range to validate it
    if not unit:
        if ref_low is None:
            return None   # Can't confirm this is a real test row
        unit = ""

    return {
        "test_name":       normalize_test_name(raw_name),
        "value":           test_value,
        "unit":            normalize_unit(unit) if unit else "",
        "confidence":      confidence,
        "report_ref_low":  ref_low,
        "report_ref_high": ref_high,
    }


# ── Helper: Try joining two consecutive lines ────────────────────────────────

def parse_joined_lines(ocr_lines: list[dict], already_found: set) -> list[dict]:
    """
    Fallback parser: joins each pair of consecutive lines and tries to parse them.
    Useful when OCR splits 'Hemoglobin  14.5' across two lines.
    """
    extra_results = []
    texts = [line.get("text", "") for line in ocr_lines]

    for i in range(len(texts) - 1):
        joined_text = texts[i] + " " + texts[i + 1]
        confidence  = min(
            ocr_lines[i].get("confidence", 1.0),
            ocr_lines[i + 1].get("confidence", 1.0),
        )
        result = parse_single_line(joined_text, confidence)
        if result:
            name_key = result["test_name"].lower()
            if name_key not in already_found:
                extra_results.append(result)
                already_found.add(name_key)

    return extra_results


# ── Main Function ────────────────────────────────────────────────────────────

def extract_test_results(ocr_lines: list[dict]) -> list[dict]:
    """
    Takes a list of OCR text lines and extracts all test results from them.
    Returns a list of dicts: test_name, value, unit, confidence, ref_low, ref_high.
    """
    results    = []
    seen_names = set()

    # Pass 1: Try to parse each line individually
    for line_data in ocr_lines:
        text       = line_data.get("text", "")
        confidence = line_data.get("confidence", 1.0)
        result     = parse_single_line(text, confidence)

        if result:
            name_key = result["test_name"].lower()
            if name_key not in seen_names:
                results.append(result)
                seen_names.add(name_key)

    # Pass 2: If very few results found, try joining consecutive lines
    if len(results) < 3:
        print("[HealthLens] Few results found — trying multi-line join...")
        extra = parse_joined_lines(ocr_lines, seen_names)
        results.extend(extra)

    print(f"[HealthLens] Extraction found {len(results)} test results")
    return results
