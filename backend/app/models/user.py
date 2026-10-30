# TODO: Might need a cleanup later.

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

# A Database Model represents a table in the database. Each attribute is a column.
class User(Base):
    __tablename__ = "users"
    
    # Unique ID for each user (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # User's email address (Must be unique, used for login)
    email = Column(String, unique=True, index=True, nullable=False)
    
    # User's full name
    full_name = Column(String, nullable=False)
    
    # We store a hashed password instead of plain text for security
    hashed_password = Column(String, nullable=False)
    
    # When the user registered
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: One user can have many reports. This links to the Report model.
    reports = relationship("Report", back_populates="user")
