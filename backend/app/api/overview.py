from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..models.memory import Entity, Event
from ..connectors import ACTIVE_CONNECTORS

router = APIRouter()

@router.get("/")
def get_overview(db: Session = Depends(get_db)):
    entity_count = db.query(Entity).count()
    event_count = db.query(Event).count()
    
    # Mocking some stats for the dashboard based on actual DB counts
    return {
        "connected_sources": len(ACTIVE_CONNECTORS),
        "indexed_records": entity_count + event_count,
        "active_agents": 2,
        "actions_today": 45,
        "pending_approvals": 3,
        "recent_activity": [
            {"id": 1, "text": "Ingested 150 Freshservice Tickets", "status": "success"},
            {"id": 2, "text": "Ingested 100 Jira Issues", "status": "success"},
            {"id": 3, "text": "Slack message blocked by RBAC", "status": "warning"}
        ]
    }
