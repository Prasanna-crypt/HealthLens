from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)

    reports = relationship("Report", back_populates="owner")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    report_date = Column(String, nullable=True)
    patient_name = Column(String, nullable=True)
    ai_summary = Column(String, nullable=True)
    total_tests = Column(Integer, default=0)
    normal_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    is_demo = Column(Boolean, default=False)

    owner = relationship("User", back_populates="reports")
    test_results = relationship("TestResult", back_populates="report", cascade="all, delete-orphan")

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    test_name = Column(String, index=True)
    value = Column(Float)
    unit = Column(String)
    reference_low = Column(Float, nullable=True)
    reference_high = Column(Float, nullable=True)
    status = Column(String) # NORMAL, LOW, HIGH, UNKNOWN
    ocr_confidence = Column(Float, nullable=True)
    ai_explanation = Column(String, nullable=True)
    category = Column(String, nullable=True)

    report = relationship("Report", back_populates="test_results")
