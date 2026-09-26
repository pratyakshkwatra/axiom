from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from ..db.session import get_db
from ..models.policy import AccessPolicy
from ..services.policy_engine import parse_policy

router = APIRouter()

def _serialize(p: AccessPolicy) -> dict:
    return {
        "id": p.id,
        "text": p.natural_language,
        "resource_type": p.resource_type,
        "action": p.action,
        "allowed_role": p.allowed_role,
        "effect": p.effect
    }

class PolicyCreate(BaseModel):
    natural_language: str
    organization_id: str

@router.post("/", response_model=dict)
def create_policy(policy: PolicyCreate, db: Session = Depends(get_db)):
    try:
        new_policies = parse_policy(policy.natural_language, policy.organization_id, db)
        return {"policies": [_serialize(p) for p in new_policies]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def list_policies(organization_id: str, db: Session = Depends(get_db)):
    policies = db.query(AccessPolicy).filter(AccessPolicy.organization_id == organization_id).all()
    return {"policies": [_serialize(p) for p in policies]}

@router.delete("/{policy_id}")
def delete_policy(policy_id: str, db: Session = Depends(get_db)):
    policy = db.query(AccessPolicy).filter(AccessPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    db.delete(policy)
    db.commit()
    return {"deleted": policy_id}
