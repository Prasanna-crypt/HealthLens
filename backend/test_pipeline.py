import sys
sys.path.insert(0, '.')

from app.services.ocr_service import extract_text_from_pdf
from app.services.extraction_service import extract_test_results
import pymupdf

# Create a realistic multi-section lab report PDF
doc = pymupdf.open()
page = doc.new_page()
y = 60

lines = [
    ("PATIENT: John Doe    AGE: 35    SEX: Male", 12),
    ("Date: 15/01/2024    Lab: City Diagnostics", 10),
    ("", 8),
    ("--- COMPLETE BLOOD COUNT (CBC) ---", 12),
    ("Hemoglobin (Hb)  14.5  g/dL  12.0 - 17.5", 10),
    ("WBC  8500  /uL  4500 - 11000", 10),
    ("RBC  4.8  million/uL  4.2 - 5.7", 10),
    ("Platelets  250000  /uL  150000 - 400000", 10),
    ("Hematocrit  42.0  %  36.0 - 48.0", 10),
    ("MCV  88.5  fL  80 - 100", 10),
    ("MCH  29.0  pg  27 - 33", 10),
    ("MCHC  33.5  g/dL  32 - 36", 10),
    ("RDW  13.2  %  11.5 - 14.5", 10),
    ("", 8),
    ("--- LIVER FUNCTION TESTS ---", 12),
    ("SGPT (ALT)  45  U/L  4 - 36", 10),
    ("SGOT (AST)  28  U/L  8 - 33", 10),
    ("Total Bilirubin  0.8  mg/dL  0.1 - 1.2", 10),
    ("Alkaline Phosphatase  95  U/L  44 - 147", 10),
    ("GGT  35  U/L  9 - 48", 10),
    ("Total Protein  7.2  g/dL  6.0 - 8.3", 10),
    ("Albumin  4.5  g/dL  3.4 - 5.4", 10),
    ("Globulin  2.7  g/dL  2.0 - 3.5", 10),
    ("", 8),
    ("--- LIPID PROFILE ---", 12),
    ("Total Cholesterol  210  mg/dL  0 - 200", 10),
    ("Triglycerides  180  mg/dL  0 - 150", 10),
    ("HDL Cholesterol  42  mg/dL  40 - 60", 10),
    ("LDL Cholesterol  132  mg/dL  0 - 100", 10),
    ("VLDL Cholesterol  36  mg/dL  5 - 40", 10),
    ("", 8),
    ("--- THYROID PROFILE ---", 12),
    ("TSH  3.5  mIU/L  0.4 - 4.0", 10),
    ("Free T4  1.2  ng/dL  0.8 - 1.8", 10),
    ("Free T3  3.1  pg/mL  2.3 - 4.2", 10),
    ("", 8),
    ("--- KIDNEY FUNCTION ---", 12),
    ("Creatinine  1.1  mg/dL  0.6 - 1.2", 10),
    ("BUN  15  mg/dL  6 - 20", 10),
    ("Uric Acid  5.5  mg/dL  3.0 - 7.0", 10),
    ("", 8),
    ("--- DIABETES ---", 12),
    ("Fasting Glucose  110  mg/dL  70 - 100", 10),
    ("HbA1c  6.2  %  4.0 - 5.7", 10),
    ("", 8),
    ("--- VITAMINS & MINERALS ---", 12),
    ("Vitamin D  25.5  ng/mL  30 - 100", 10),
    ("Vitamin B12  450  pg/mL  200 - 900", 10),
    ("Iron  85  ug/dl  60 - 170", 10),
    ("Ferritin  120  ng/mL  12 - 300", 10),
    ("Calcium  9.5  mg/dL  8.5 - 10.5", 10),
    ("", 8),
    ("--- INFLAMMATORY MARKERS ---", 12),
    ("C-Reactive Protein  3.2  mg/L  0 - 5", 10),
    ("ESR  12  mm/hr  0 - 20", 10),
]

for text, size in lines:
    if text:
        page.insert_text((72, y), text, fontsize=size)
    y += size + 4

pdf_bytes = doc.tobytes()
doc.close()

# Extract and parse
text_lines = extract_text_from_pdf(pdf_bytes)
results = extract_test_results(text_lines)

print("=== Extracted " + str(len(results)) + " results ===")
for r in results:
    ref = ""
    if r["report_ref_low"] is not None:
        ref = " (ref: " + str(r["report_ref_low"]) + "-" + str(r["report_ref_high"]) + ")"
    print("  " + r["test_name"] + ": " + str(r["value"]) + " " + r["unit"] + ref)
