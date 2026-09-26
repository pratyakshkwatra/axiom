import asyncio
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from ..db.session import SessionLocal
from ..services.retrieval import search_context
from ..models.policy import AccessPolicy

router = APIRouter()

# Mock MCP Server Endpoint for Hackathon MVP
# Since standard mcp python SDK requires specific transport mounting,
# we expose the tool directly as a REST endpoint for the dashboard to hit.

@router.post("/tools/axiom_search")
def axiom_search(query: str, organization_id: str, role: str):
    """
    Search the context graph. Results are strictly filtered by the requesting role.
    """
    db = SessionLocal()
    try:
        user_context = {"organization_id": organization_id, "role": role}
        return {"results": search_context(query, user_context, db)}
    finally:
        db.close()

# Mock SSE endpoint
@router.get("/sse")
async def handle_sse(request: Request):
    return {"status": "MCP SSE Endpoint Mocked for MVP"}
