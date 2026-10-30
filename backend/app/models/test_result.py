# TODO: Might need a cleanup later.

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

class TestResult(Base):
    __tablename__ = "test_results"
    
    # Unique ID for the test result
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to the Report this result belongs to
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    
    # Name of the lab test (e.g., Hemoglobin, Glucose)
    test_name = Column(String, nullable=False)
    
    # The actual measured number (e.g., 14.5)
    value = Column(Float, nullable=False)
    
    # The unit of measurement (e.g., g/dL)
    unit = Column(String, nullable=False)
    
    # The lower and upper bounds of what is considered "normal"
    reference_low = Column(Float, nullable=True)
    reference_high = Column(Float, nullable=True)
    
    # Classification: NORMAL, LOW, or HIGH
    status = Column(String, nullable=False)
    
    # How confident the OCR (text extraction) was
    ocr_confidence = Column(Float, nullable=True)
    
    # AI-generated simple explanation of this specific result
    ai_explanation = Column(Text, nullable=True)
    
    # General category of the test (e.g., Blood, Liver, Kidney)
    category = Column(String, nullable=True)
    
    # Relationship back to the Report
    report = relationship("Report", back_populates="test_results")
