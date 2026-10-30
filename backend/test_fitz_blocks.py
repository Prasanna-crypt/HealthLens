import fitz
pdf_path = r"d:\New folder\healthlens\backend\uploads\09ef50e1-6716-40e5-ba2f-31a0025db625_Sample-Smart-Report-Clinics.pdf"
doc = fitz.open(pdf_path)
for i, page in enumerate(doc):
    print(f"--- Page {i} ---")
    blocks = page.get_text("blocks")
    for b in blocks:
        # b[4] is the text
        print(repr(b[4]))
    break
