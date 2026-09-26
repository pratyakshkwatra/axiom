"""
Seeds the structured access policies used by the demo roles.

Each row is what the policy engine (app/services/policy_engine.py) produces
from the natural-language rule stored alongside it. Seeding them directly
keeps the demo independent of the LLM parser. Re-running replaces the
organization's policies.

Usage (from backend/):
    python scripts/seed_policies.py
"""
import os
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import SessionLocal
from app.models.policy import AccessPolicy

ORGANIZATION_ID = "org-1"

# (natural language, resource_type, allowed_role)
POLICIES = [
    ("Engineers can read tickets, projects, messages and notes.", "ticket", "ENGINEER"),
    ("Engineers can read tickets, projects, messages and notes.", "project", "ENGINEER"),
    ("Engineers can read tickets, projects, messages and notes.", "message", "ENGINEER"),
    ("Engineers can read tickets, projects, messages and notes.", "note", "ENGINEER"),
    ("Support agents can read tickets and ticket notes only.", "ticket", "SUPPORT_AGENT"),
    ("Support agents can read tickets and ticket notes only.", "note", "SUPPORT_AGENT"),
    ("Contractors can read project information but nothing else.", "project", "CONTRACTOR"),
    ("Only HR administrators can access employee records and compensation.", "employee_record", "HR_ADMIN"),
    ("Only HR administrators can access employee records and compensation.", "compensation", "HR_ADMIN"),
    ("HR administrators can read all organizational context.", "all", "HR_ADMIN"),
]

def seed_policies():
    db = SessionLocal()
    try:
        db.query(AccessPolicy).filter(AccessPolicy.organization_id == ORGANIZATION_ID).delete()
        for text, resource_type, role in POLICIES:
            db.add(AccessPolicy(
                id=str(uuid.uuid4()),
                organization_id=ORGANIZATION_ID,
                natural_language=text,
                resource_type=resource_type,
                action="read",
                allowed_role=role,
                effect="ALLOW"
            ))
        db.commit()
        print(f"Seeded {len(POLICIES)} policies for {ORGANIZATION_ID}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_policies()
