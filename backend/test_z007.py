import sys
sys.path.append(r"d:\New folder\healthlens\backend")
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from app.services.ocr_service import extract_text
from app.services.extraction_service import extract_test_results

pdf_path = r"d:\New folder\healthlens\backend\uploads\5a372184-7f97-4582-823b-4856f9ca4aeb_Z007.pdf"
with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

ocr_lines = extract_text(pdf_bytes, 'application/pdf')
print("Extracted lines:", len(ocr_lines))
results = extract_test_results(ocr_lines)
print("Results:", results)
