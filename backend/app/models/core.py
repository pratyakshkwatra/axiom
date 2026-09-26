from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    organization_id = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    department = Column(String)
    role = Column(String)
    status = Column(String)

class Source(Base):
    __tablename__ = "sources"
    id = Column(String, primary_key=True)
    organization_id = Column(String, index=True)
    type = Column(String)
    external_id = Column(String)
    permissions = Column(JSON)
    last_sync = Column(DateTime)
    status = Column(String)

class KnowledgeObject(Base):
    __tablename__ = "knowledge_objects"
    id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey("sources.id"))
    type = Column(String)
    external_id = Column(String)
    content = Column(String)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class Policy(Base):
    __tablename__ = "policies"
    id = Column(String, primary_key=True)
    organization_id = Column(String, index=True)
    name = Column(String)
    subject = Column(String)
    resource = Column(String)
    action = Column(String)
    effect = Column(String)
    conditions = Column(JSON)

class Action(Base):
    __tablename__ = "actions"
    id = Column(String, primary_key=True)
    name = Column(String)
    connector = Column(String)
    description = Column(String)
    risk_level = Column(Integer)
    requires_confirmation = Column(Boolean, default=False)
