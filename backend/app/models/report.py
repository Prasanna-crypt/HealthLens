# TODO: Might need a cleanup later.

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Report(Base):
    __tablename__ = "reports"
    
    # Unique ID for the report
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key: Links this report to a specific user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Original filename of the uploaded report
    filename = Column(String, nullable=False)
    
    # Date and time the file was uploaded
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    # Date of the actual medical test (extracted from the document)
    report_date = Column(String, nullable=True)
    
    # Name of the patient on the report
    patient_name = Column(String, nullable=True)
    
    # AI-generated summary of the entire report
    ai_summary = Column(Text, nullable=True)
    
    # Quick statistics about the tests in this report
    total_tests = Column(Integer, default=0)
    normal_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    
    # Flag to indicate if this is fake demo data
    is_demo = Column(Boolean, default=False)
    
    # Relationship to the User who uploaded it
    user = relationship("User", back_populates="reports")
    
    # Relationship to the individual test results in this report.
    # cascade="all, delete-orphan" means if we delete the report, its results are also deleted.
    test_results = relationship("TestResult", back_populates="report", cascade="all, delete-orphan")
