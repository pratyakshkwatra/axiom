import hashlib
from typing import List
from sqlalchemy.orm import Session
from ..models.memory import Entity, Event
from .policy_engine import evaluate_access
from sentence_transformers import SentenceTransformer

# Load the model once to avoid loading it on every request
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text: str) -> List[float]:
    """
    Generates a real 384-dimensional vector using sentence-transformers.
    """
    if not text.strip():
        return [0.0] * 384
    return embedding_model.encode(text).tolist()

def search_context(query: str, user: dict, db: Session, limit: int = 5) -> dict:
    """
    Embeds the query, searches the memory graph, filters by RBAC, and returns safe context.
    """
    query_vector = embed_text(query)
    
    # Search Entities
    entities = db.query(Entity).filter(
        Entity.organization_id == user.get("organization_id")
    ).order_by(Entity.embedding.cosine_distance(query_vector)).limit(limit * 2).all()
    
    # Search Events
    events = db.query(Event).filter(
        Event.organization_id == user.get("organization_id")
    ).order_by(Event.embedding.cosine_distance(query_vector)).limit(limit * 2).all()
    
    safe_entities = []
    for entity in entities:
        if evaluate_access(user, entity.entity_type, "read", db):
            safe_entities.append(entity)
            if len(safe_entities) >= limit:
                break
                
    safe_events = []
    for event in events:
        if evaluate_access(user, event.event_type, "read", db):
            safe_events.append(event)
            if len(safe_events) >= limit:
                break
                
    return {
        "entities": [{"id": e.id, "type": e.entity_type, "name": e.name, "source": e.source} for e in safe_entities],
        "events": [{"id": e.id, "type": e.event_type, "title": e.title, "source": e.source} for e in safe_events]
    }
