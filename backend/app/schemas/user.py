# TODO: Might need a cleanup later.

from pydantic import BaseModel, EmailStr
from datetime import datetime

# Pydantic schemas validate incoming JSON data and serialize outgoing Python objects to JSON.
# Unlike SQLAlchemy models (which talk to the database), Pydantic schemas talk to the API client.

# Schema for creating a new user (Registration)
class UserCreate(BaseModel):
    email: EmailStr  # Validates that it looks like an email
    password: str
    full_name: str

# Schema for logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for what we send back to the client (Notice we DO NOT include the password here!)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime
    
    class Config:
        # This tells Pydantic to read data even if it's an ORM model (not a dictionary)
        from_attributes = True

# Schema for returning the login token
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
