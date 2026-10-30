# TODO: Might need a cleanup later.

from sqlalchemy import Column, Integer, String, Float
from ..database import Base

# In a medical context, a reference range is the normal expected values for a healthy person.
# For example, normal fasting glucose is 70 to 100 mg/dL.
class ReferenceRange(Base):
    __tablename__ = "reference_ranges"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Name of the test
    test_name = Column(String, unique=True, index=True, nullable=False)
    
    # The lowest normal value
    low = Column(Float, nullable=False)
    
    # The highest normal value
    high = Column(Float, nullable=False)
    
    # The unit (e.g., mg/dL)
    unit = Column(String, nullable=False)
    
    # Category of test
    category = Column(String, nullable=False)
    
    # Where we got this range from (e.g., WHO guidelines)
    source = Column(String, nullable=False)
    
    # JSON string of alternative names for this test (e.g., "Blood Sugar" for "Glucose")
    aliases = Column(String, nullable=True)
