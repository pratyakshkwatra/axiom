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
    ).order_by(Entity.embedding.cosine_distance(query_vector)).limit(limit * 5).all()
    
    # Search Events
    events = db.query(Event).filter(
        Event.organization_id == user.get("organization_id")
    ).order_by(Event.embedding.cosine_distance(query_vector)).limit(limit * 5).all()
    
    # Track what policy filtering removed so callers can show it
    withheld = {}

    safe_entities = []
    for entity in entities:
        if evaluate_access(user, entity.entity_type, "read", db):
            if len(safe_entities) < limit:
                safe_entities.append(entity)
        else:
            withheld[entity.entity_type] = withheld.get(entity.entity_type, 0) + 1

    safe_events = []
    for event in events:
        if evaluate_access(user, event.event_type, "read", db):
            if len(safe_events) < limit:
                safe_events.append(event)
        else:
            withheld[event.event_type] = withheld.get(event.event_type, 0) + 1

    return {
        "entities": [{"id": e.id, "type": e.entity_type, "name": e.name, "description": e.description, "source": e.source, "external_id": e.external_id, "metadata": e.metadata_} for e in safe_entities],
        "events": [{"id": e.id, "type": e.event_type, "title": e.title, "content": e.content, "source": e.source, "external_id": e.external_id, "metadata": e.metadata_} for e in safe_events],
        "withheld": withheld
    }
