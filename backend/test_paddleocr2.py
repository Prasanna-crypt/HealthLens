import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
try:
    from paddleocr import PaddleOCR
except Exception as e:
    import traceback
    traceback.print_exc()
