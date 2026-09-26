from sqlalchemy.orm import Session
from typing import List, Dict
import uuid
from ..connectors import ACTIVE_CONNECTORS
from ..models.memory import Entity, Event
from .retrieval import embed_text

def ingest_records(organization_id: str, source: str, entities_data: List[Dict], events_data: List[Dict], db: Session) -> dict:
    """
    Embeds and upserts entities and events for a single source. Does not commit.
    """
    stats = {"entities_synced": 0, "events_synced": 0}

    for e_data in entities_data:
        # Check if exists (upsert logic simplified for MVP)
        existing = db.query(Entity).filter(
            Entity.external_id == e_data["external_id"],
            Entity.source == source
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
                source=source,
                external_id=e_data["external_id"],
                metadata_=e_data.get("metadata_"),
                embedding=embedding
            )
            db.add(new_entity)
        stats["entities_synced"] += 1

    for ev_data in events_data:
        existing = db.query(Event).filter(
            Event.external_id == ev_data["external_id"],
            Event.source == source
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
                source=source,
                external_id=ev_data["external_id"],
                metadata_=ev_data.get("metadata_"),
                embedding=embedding
            )
            db.add(new_event)
        stats["events_synced"] += 1

    return stats

def run_sync(organization_id: str, db: Session) -> dict:
    """
    Iterates over all active connectors, fetches entities and events from the real APIs, embeds them, and commits to DB.
    """
    stats = {"entities_synced": 0, "events_synced": 0, "sources": []}

    for connector in ACTIVE_CONNECTORS:
        stats["sources"].append(connector.source_name)
        source_stats = ingest_records(
            organization_id,
            connector.source_name,
            connector.sync_entities(organization_id),
            connector.sync_events(organization_id),
            db
        )
        stats["entities_synced"] += source_stats["entities_synced"]
        stats["events_synced"] += source_stats["events_synced"]

    db.commit()
    return stats
