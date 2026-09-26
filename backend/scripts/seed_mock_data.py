"""
Seeds the database with synthetic demo data for the knowledge graph.

Why this exists: the connectors in app/connectors/ only talk to the real
Freshservice, Jira and Slack APIs. Our hackathon sandbox accounts contain only
a handful of records, which is not enough to show cross-system context,
relationship mapping or the knowledge graph at realistic scale. This script
fills that gap with clearly-labelled mock records (metadata "mock": true)
and runs completely separately from the real sync (POST /sync, run_sync()).

Usage (from backend/):
    python scripts/seed_mock_data.py
"""
import os
import sys
import random

# Add backend directory to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import SessionLocal
from app.services.ingestion import ingest_records

ORGANIZATION_ID = "org-1"

def mock_freshservice():
    entities = []
    for i in range(1, 301):
        entities.append({
            "external_id": f"INC-{8000 + i}",
            "entity_type": "ticket",
            "name": f"IT Request #{i} - Access Issue",
            "description": f"User is requesting access to internal tool {i%10}. Needs manager approval.",
            "metadata_": {"status": "Pending" if i%2==0 else "Resolved", "requester": f"Employee-{i%50}", "mock": True}
        })

    events = []
    for i in range(1, 501):
        events.append({
            "external_id": f"note-INC-{8000 + (i%150)}-{i}",
            "event_type": "note",
            "title": f"Note on INC-{8000 + (i%150)}",
            "content": f"Followed up with the user. Provisioning access now. Wait time approx {i%5} hours.",
            "metadata_": {"author": f"Support Agent {i%10}", "ticket": f"INC-{8000 + (i%150)}", "mock": True}
        })
    return entities, events

def mock_jira():
    entities = []
    for i in range(1, 201):
        status = "Open" if i % 3 == 0 else "In Progress" if i % 2 == 0 else "Closed"
        entities.append({
            "external_id": f"PAY-{100 + i}",
            "entity_type": "ticket",
            "name": f"Payment gateway issue #{i}",
            "description": f"Customer reported error {500 + (i%5)} during checkout flow.",
            "metadata_": {"status": status, "assignee": f"Dev-{i%10}", "project": "Payments", "mock": True}
        })

    events = []
    for i in range(1, 401):
        events.append({
            "external_id": f"comment-PAY-{100 + (i%100)}-{i}",
            "event_type": "note",
            "title": f"Comment on PAY-{100 + (i%100)}",
            "content": f"Investigated logs for correlation ID {1000 + i}. It seems related to the third-party API rate limit.",
            "metadata_": {"author": f"Dev-{(i+1)%10}", "issue": f"PAY-{100 + (i%100)}", "mock": True}
        })
    return entities, events

def mock_slack():
    entities = []
    for i in range(1, 51):
        entities.append({
            "external_id": f"C01A2B3C4D{i}",
            "entity_type": "project",
            "name": f"#eng-team-{i}",
            "description": f"Discussion channel for engineering team {i}.",
            "metadata_": {"members": 10 + i, "mock": True}
        })

    events = []
    for i in range(1, 801):
        channel_id = random.randint(1, 50)
        events.append({
            "external_id": f"msg-{10000 + i}",
            "event_type": "message",
            "title": f"Message in #eng-team-{channel_id}",
            "content": f"Discussing architecture for feature {i%50}. Let's make sure we handle edge cases properly.",
            "metadata_": {"author": f"User-{i%30}", "channel": f"#eng-team-{channel_id}", "mock": True}
        })
    return entities, events

def mock_hris():
    entities = []
    for i in range(10):
        entities.append({
            "external_id": f"EMP-{i}",
            "entity_type": "employee_record",
            "name": f"Employee record - Dev-{i} (Payments team)",
            "description": f"Dev-{i}, payment gateway engineer. Performance review: {'exceeds' if i%2 else 'meets'} expectations. On-call for checkout flow incidents.",
            "metadata_": {"manager": "Eng Manager Payments", "mock": True}
        })
        entities.append({
            "external_id": f"COMP-{i}",
            "entity_type": "compensation",
            "name": f"Compensation - Dev-{i} (Payments team)",
            "description": f"Dev-{i} salary band L{3 + i%3}, base {90 + i*7}k USD, retention bonus pending after payment gateway incident work.",
            "metadata_": {"mock": True}
        })
    return entities, []

MOCK_SOURCES = {
    "hris": mock_hris,
    "freshservice": mock_freshservice,
    "jira": mock_jira,
    "slack": mock_slack,
}

def seed_data():
    print("Starting mock data seed...")
    db = SessionLocal()
    try:
        for source, generate in MOCK_SOURCES.items():
            entities, events = generate()
            stats = ingest_records(ORGANIZATION_ID, source, entities, events, db)
            print(f"  {source}: {stats}")
        db.commit()
        print("Seed complete!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
