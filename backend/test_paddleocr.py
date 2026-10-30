print("Importing PaddleOCR...")
from paddleocr import PaddleOCR
print("Instantiating PaddleOCR...")
ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
print("Success!")
