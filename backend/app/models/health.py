from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    full_name = Column(String)
    date_of_birth = Column(DateTime)
    sex = Column(String)
    height = Column(Float)
    weight = Column(Float)
    blood_group = Column(String)
    known_allergies = Column(Text)
    existing_conditions = Column(Text)
    current_medications = Column(Text)

class HealthChange(Base):
    __tablename__ = "health_changes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True)
    test_name = Column(String, index=True)
    previous_value = Column(Float)
    current_value = Column(Float)
    absolute_change = Column(Float)
    percentage_change = Column(Float)
    direction = Column(String) # Increased/Decreased/Stable
    previous_status = Column(String)
    current_status = Column(String)

class HealthPattern(Base):
    __tablename__ = "health_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True)
    pattern_name = Column(String)
    related_tests = Column(JSON) # JSON or string
    explanation = Column(Text)
    severity = Column(String)
    recommended_discussion = Column(Text)

class DoctorSummary(Base):
    __tablename__ = "doctor_summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), index=True)
    summary_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
