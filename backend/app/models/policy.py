from sqlalchemy import Column, String, JSON, DateTime, Boolean, Integer
from datetime import datetime
from .base import Base

class AccessPolicy(Base):
    """
    Structured policy derived from Natural Language.
    """
    __tablename__ = "access_policies"
    id = Column(String, primary_key=True)
    organization_id = Column(String, index=True)
    natural_language = Column(String)
    
    # Structured representation
    resource_type = Column(String) # "compensation", "ticket", "project"
    action = Column(String) # "read", "write"
    allowed_role = Column(String) # "HR_ADMIN", "ENGINEERING_MANAGER"
    allowed_team = Column(String, nullable=True)
    effect = Column(String, default="DENY")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    """
    Immutable log of all context retrievals and actions.
    """
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True)
    organization_id = Column(String, index=True)
    actor_id = Column(String, index=True) # Agent or Employee ID
    intent = Column(String)
    requested_resource = Column(String)
    policy_evaluated = Column(String, nullable=True)
    result = Column(String) # "ALLOWED", "DENIED", "EXECUTED", "REQUIRES_APPROVAL"
    action_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
