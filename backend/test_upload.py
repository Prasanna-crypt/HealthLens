import asyncio
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from app.database import SessionLocal
from app.services.report_service import process_report
from app.models.user import User
from app.utils.security import hash_password

db = SessionLocal()

# Create a dummy user
user = db.query(User).filter(User.email == "test@test.com").first()
if not user:
    user = User(email="test@test.com", hashed_password=hash_password("password"), full_name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)

# Dummy image
dummy_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa7\x35\x81\x84\x00\x00\x00\x00IEND\xaeB`\x82'

print("Calling process_report...")
try:
    report = process_report(dummy_image, "test.png", "image/png", user.id, db)
    print(f"Success! Report ID: {report.id}")
except Exception as e:
    import traceback
    traceback.print_exc()

db.close()
