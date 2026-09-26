from sqlalchemy import Column, String, DateTime
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    organization_id = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    department = Column(String)
    role = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
