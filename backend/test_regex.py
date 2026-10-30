import re

pattern = re.compile(r'([A-Za-z\s\.]+)[:\s]+([\d\.]+)[\s]*(g/dL|mg/dL|U/L|%|/µL|million/µL|fL|pg|mIU/L|ng/dL|µg/dL)', re.IGNORECASE)
text = "Cholesterol 199.99 mg/dL"
match = pattern.search(text)
if match:
    print(f"Group 1 (name): '{match.group(1)}'")
    print(f"Group 2 (value): '{match.group(2)}'")
    print(f"Group 3 (unit): '{match.group(3)}'")
else:
    print("No match")
