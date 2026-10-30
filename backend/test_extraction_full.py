import sys
sys.path.append(r"d:\New folder\healthlens\backend")
import os
import io

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from app.services.ocr_service import extract_text
from app.services.extraction_service import extract_test_results

pdf_path = r"d:\New folder\healthlens\backend\uploads\09ef50e1-6716-40e5-ba2f-31a0025db625_Sample-Smart-Report-Clinics.pdf"
with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

print("Extracting text...")
ocr_lines = extract_text(pdf_bytes, 'application/pdf')

print("Extracted lines:", len(ocr_lines))
for i, line in enumerate(ocr_lines[:20]):
    print(f"Line {i}: {line['text']}")

print("---")
print("Extracting test results...")
results = extract_test_results(ocr_lines)
print("Results:", results)
