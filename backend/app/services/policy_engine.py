import json
from anthropic import Anthropic
import os
from ..models.policy import AccessPolicy
from sqlalchemy.orm import Session
import uuid

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def parse_policy(nlp_text: str, organization_id: str, db: Session) -> AccessPolicy:
    """
    Uses LLM to convert natural language into a structured AccessPolicy.
    """
    prompt = f"""
    Convert this natural language access policy into a structured JSON object.
    Policy: "{nlp_text}"
    
    Output exactly valid JSON with the following keys:
    - resource_type: The type of resource being accessed (e.g., 'ticket', 'project', 'compensation', 'all').
    - action: The action allowed (e.g., 'read', 'write', 'all').
    - allowed_role: The role that is allowed (e.g., 'HR_ADMIN', 'ENGINEERING_MANAGER', 'EMPLOYEE').
    - allowed_team: The specific team allowed, if any. Otherwise null.
    - effect: 'ALLOW' or 'DENY'. (Usually policies state who is allowed, so effect is ALLOW for that role, effectively DENYing others later).
    """
    
    response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        content = response.content[0].text
        # Extract JSON from potential markdown blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        data = json.loads(content)
        
        policy = AccessPolicy(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            natural_language=nlp_text,
            resource_type=data.get("resource_type", "all").lower(),
            action=data.get("action", "read").lower(),
            allowed_role=data.get("allowed_role"),
            allowed_team=data.get("allowed_team"),
            effect=data.get("effect", "ALLOW").upper()
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy
    except Exception as e:
        raise ValueError(f"Failed to parse policy: {str(e)}")

def evaluate_access(user: dict, resource_type: str, action: str, db: Session) -> bool:
    """
    Evaluates if the given user is allowed to perform the action on the resource_type.
    `user` dict is extracted from the JWT token.
    """
    policies = db.query(AccessPolicy).filter(
        AccessPolicy.organization_id == user.get("organization_id"),
        AccessPolicy.resource_type.in_([resource_type.lower(), "all"])
    ).all()
    
    if not policies:
        # Default deny if no policies exist for this resource (zero-trust)
        return False
        
    for policy in policies:
        # Check if the policy explicitly denies
        if policy.effect == "DENY":
            if policy.allowed_role and user.get("role") == policy.allowed_role:
                return False
                
        # Check if the policy allows
        if policy.effect == "ALLOW":
            if policy.allowed_role and user.get("role") == policy.allowed_role:
                return True
            if policy.allowed_role == "ANY" or policy.allowed_role == "EMPLOYEE":
                return True

    return False
