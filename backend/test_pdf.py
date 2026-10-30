import os
pdf_path = r"d:\New folder\healthlens\backend\uploads\09ef50e1-6716-40e5-ba2f-31a0025db625_Sample-Smart-Report-Clinics.pdf"
try:
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        print(f"Extracted {len(text)} characters using pdfplumber.")
        print(text[:500])
except ImportError:
    print("pdfplumber not installed")
