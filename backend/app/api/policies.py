from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from ..db.session import get_db
from ..models.policy import AccessPolicy
from ..services.policy_engine import parse_policy

router = APIRouter()

class PolicyCreate(BaseModel):
    natural_language: str
    organization_id: str

@router.post("/", response_model=dict)
def create_policy(policy: PolicyCreate, db: Session = Depends(get_db)):
    try:
        new_policy = parse_policy(policy.natural_language, policy.organization_id, db)
        return {
            "id": new_policy.id,
            "resource_type": new_policy.resource_type,
            "action": new_policy.action,
            "allowed_role": new_policy.allowed_role,
            "effect": new_policy.effect
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def list_policies(organization_id: str, db: Session = Depends(get_db)):
    policies = db.query(AccessPolicy).filter(AccessPolicy.organization_id == organization_id).all()
    return {"policies": [{"id": p.id, "text": p.natural_language, "resource": p.resource_type, "role": p.allowed_role} for p in policies]}
