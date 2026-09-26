from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
from .base import Base

class Entity(Base):
    """
    Person, Team, Project, Customer, Document, Ticket, etc.
    """
    __tablename__ = "entities"
    id = Column(String, primary_key=True)
    organization_id = Column(String, index=True)
    entity_type = Column(String, index=True) # "Person", "Team", "Ticket", "Project"
    name = Column(String)
    description = Column(String)
    source = Column(String) # "slack", "jira", "freshservice"
    external_id = Column(String)
    metadata_ = Column("metadata", JSON)
    embedding = Column(Vector(384))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Event(Base):
    """
    Message, Meeting, Note, Incident, Email
    """
    __tablename__ = "events"
    id = Column(String, primary_key=True)
    organization_id = Column(String, index=True)
    event_type = Column(String, index=True)
    title = Column(String)
    content = Column(String)
    source = Column(String)
    external_id = Column(String)
    metadata_ = Column("metadata", JSON)
    embedding = Column(Vector(384))
    timestamp = Column(DateTime, default=datetime.utcnow)

class Relationship(Base):
    """
    Employee->Team, Ticket->Customer, Decision->Project, etc.
    """
    __tablename__ = "relationships"
    id = Column(String, primary_key=True)
    source_entity_id = Column(String, ForeignKey("entities.id"), index=True)
    target_entity_id = Column(String, ForeignKey("entities.id"), index=True)
    relation_type = Column(String, index=True) # "BELONGS_TO", "MENTIONS", "RESOLVES"
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
