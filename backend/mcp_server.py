"""
AXIOM MCP server (stdio).

Exposes AXIOM's permission-aware enterprise memory to any MCP-compatible
AI agent. Every tool call is evaluated against the organization's access
policies and written to the audit log.

Run:
    python mcp_server.py
Connect Claude Code (backend running in docker compose):
    claude mcp add axiom -- docker exec -i axiom-backend-1 python mcp_server.py
"""
import uuid
from mcp.server.fastmcp import FastMCP

from app.db.session import SessionLocal
from app.models.policy import AccessPolicy, AuditLog
from app.services.retrieval import search_context

ORGANIZATION_ID = "org-1"
ROLES = ["ENGINEER", "SUPPORT_AGENT", "CONTRACTOR", "HR_ADMIN"]

mcp = FastMCP("axiom")

def _audit(db, actor_id: str, intent: str, resource: str, result: str, policy: str = None):
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        organization_id=ORGANIZATION_ID,
        actor_id=actor_id,
        intent=intent,
        requested_resource=resource,
        policy_evaluated=policy,
        result=result,
        action_type="read"
    ))
    db.commit()

@mcp.tool()
def axiom_search(query: str, role: str = "ENGINEER", agent_id: str = "external-agent") -> dict:
    """
    Search AXIOM's unified enterprise memory (Freshservice tickets and notes,
    Jira issues and comments, Slack channels and messages, HR records).
    Results are filtered by the access policies for the given role before
    they are returned; anything withheld is reported but never revealed.

    role: one of ENGINEER, SUPPORT_AGENT, CONTRACTOR, HR_ADMIN
    """
    role = role.upper()
    if role not in ROLES:
        return {"error": f"Unknown role '{role}'. Valid roles: {', '.join(ROLES)}"}

    db = SessionLocal()
    try:
        results = search_context(query, {"organization_id": ORGANIZATION_ID, "role": role}, db, limit=8)
        withheld = results["withheld"]
        returned = len(results["entities"]) + len(results["events"])

        if withheld:
            blocked = ", ".join(f"{count} {kind}" for kind, count in withheld.items())
            results["policy_enforcement"] = (
                f"AXIOM withheld {sum(withheld.values())} matching records ({blocked}): "
                f"role {role} is not authorized by any access policy to read them."
            )
            result = "PARTIAL" if returned else "DENIED"
        else:
            result = "ALLOWED"

        _audit(db, f"{agent_id} ({role})", f"search: {query}", ", ".join(results["withheld"]) or "context", result, "RBAC")
        results["audit"] = f"Logged as {result} for {agent_id} ({role})"
        return results
    finally:
        db.close()

@mcp.tool()
def axiom_list_policies() -> list:
    """
    List the organization's access policies, in the natural language the
    admin wrote them in and the structured rule AXIOM enforces.
    """
    db = SessionLocal()
    try:
        policies = db.query(AccessPolicy).filter(AccessPolicy.organization_id == ORGANIZATION_ID).all()
        return [{
            "policy": p.natural_language,
            "enforced_as": f"{p.effect} {p.allowed_role} {p.action} {p.resource_type}"
        } for p in policies]
    finally:
        db.close()

@mcp.tool()
def axiom_audit_log(limit: int = 10) -> list:
    """
    Return the most recent entries from AXIOM's audit log: every retrieval,
    who asked, what was requested and whether it was allowed or denied.
    """
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).filter(AuditLog.organization_id == ORGANIZATION_ID).order_by(AuditLog.timestamp.desc()).limit(limit).all()
        return [{
            "time": l.timestamp.isoformat() if l.timestamp else None,
            "actor": l.actor_id,
            "intent": l.intent,
            "resource": l.requested_resource,
            "result": l.result
        } for l in logs]
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run()
