from sqlalchemy.orm import Session
import uuid
from ..connectors import ACTIVE_CONNECTORS
from ..models.memory import Entity, Event
from .retrieval import embed_text

def run_sync(organization_id: str, db: Session) -> dict:
    """
    Iterates over all active connectors, fetches entities and events, embeds them, and commits to DB.
    """
    stats = {"entities_synced": 0, "events_synced": 0, "sources": []}
    
    for connector in ACTIVE_CONNECTORS:
        stats["sources"].append(connector.source_name)
        
        # Sync Entities
        entities_data = connector.sync_entities(organization_id)
        for e_data in entities_data:
            # Check if exists (upsert logic simplified for MVP)
            existing = db.query(Entity).filter(
                Entity.external_id == e_data["external_id"],
                Entity.source == connector.source_name
            ).first()
            
            text_to_embed = f"{e_data.get('name', '')} {e_data.get('description', '')}"
            embedding = embed_text(text_to_embed)
            
            if existing:
                existing.name = e_data.get("name")
                existing.description = e_data.get("description")
                existing.metadata_ = e_data.get("metadata_")
                existing.embedding = embedding
            else:
                new_entity = Entity(
                    id=str(uuid.uuid4()),
                    organization_id=organization_id,
                    entity_type=e_data["entity_type"],
                    name=e_data.get("name"),
                    description=e_data.get("description"),
                    source=connector.source_name,
                    external_id=e_data["external_id"],
                    metadata_=e_data.get("metadata_"),
                    embedding=embedding
                )
                db.add(new_entity)
            stats["entities_synced"] += 1

        # Sync Events
        events_data = connector.sync_events(organization_id)
        for ev_data in events_data:
            existing = db.query(Event).filter(
                Event.external_id == ev_data["external_id"],
                Event.source == connector.source_name
            ).first()
            
            text_to_embed = f"{ev_data.get('title', '')} {ev_data.get('content', '')}"
            embedding = embed_text(text_to_embed)
            
            if existing:
                existing.title = ev_data.get("title")
                existing.content = ev_data.get("content")
                existing.metadata_ = ev_data.get("metadata_")
                existing.embedding = embedding
            else:
                new_event = Event(
                    id=str(uuid.uuid4()),
                    organization_id=organization_id,
                    event_type=ev_data["event_type"],
                    title=ev_data.get("title"),
                    content=ev_data.get("content"),
                    source=connector.source_name,
                    external_id=ev_data["external_id"],
                    metadata_=ev_data.get("metadata_"),
                    embedding=embedding
                )
                db.add(new_event)
            stats["events_synced"] += 1
            
    db.commit()
    return stats
