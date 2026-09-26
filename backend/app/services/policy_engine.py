import json
from anthropic import Anthropic
import os
from ..models.policy import AccessPolicy
from sqlalchemy.orm import Session
import uuid
from typing import List

# Initialize Anthropic client
anthropic_client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    default_headers={"anthropic-workspace-id": os.getenv("ANTHROPIC_WORKSPACE_ID")} if os.getenv("ANTHROPIC_WORKSPACE_ID") else {}
)

RESOURCE_TYPES = ["ticket", "note", "project", "message", "employee_record", "compensation", "all"]
ROLES = ["ENGINEER", "SUPPORT_AGENT", "CONTRACTOR", "HR_ADMIN"]

def parse_policy(nlp_text: str, organization_id: str, db: Session) -> List[AccessPolicy]:
    """
    Uses LLM to convert natural language into structured AccessPolicy rows (one per resource type).
    """
    prompt = f"""
    Convert this natural language access policy into structured rules.
    Policy: "{nlp_text}"

    Output exactly valid JSON: an array of objects, one per resource type the policy covers, each with keys:
    - resource_type: one of {RESOURCE_TYPES}. Map synonyms: salary/pay -> compensation, HR/employee info -> employee_record,
      Jira issues/Freshservice tickets -> ticket, comments/ticket notes -> note, Slack messages -> message, channels/projects -> project.
    - action: 'read' or 'write'.
    - allowed_role: one of {ROLES} (the role the rule applies to).
    - effect: 'ALLOW' or 'DENY'.
    Output only the JSON array.
    """

    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
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
        if isinstance(data, dict):
            data = [data]

        policies = []
        for rule in data:
            resource_type = rule.get("resource_type", "").lower()
            role = (rule.get("allowed_role") or "").upper()
            if resource_type not in RESOURCE_TYPES or role not in ROLES:
                continue
            policy = AccessPolicy(
                id=str(uuid.uuid4()),
                organization_id=organization_id,
                natural_language=nlp_text,
                resource_type=resource_type,
                action=rule.get("action", "read").lower(),
                allowed_role=role,
                effect=rule.get("effect", "ALLOW").upper()
            )
            db.add(policy)
            policies.append(policy)

        if not policies:
            raise ValueError("No enforceable rule found in policy")
        db.commit()
        return policies
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
