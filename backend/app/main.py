from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .db.session import engine, get_db
from .models import Base
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, policies, memory, sync, mcp_routes, overview

# Create vector extension and tables
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AXIOM API", version="1.0.0")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(policies.router, prefix="/api/policies", tags=["policies"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])
app.include_router(mcp_routes.router, prefix="/api/mcp", tags=["mcp"])
app.include_router(overview.router, prefix="/api/overview", tags=["overview"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/overview")
def get_overview(db: Session = Depends(get_db)):
    # Mock data for the dashboard based on PRD
    return {
        "connected_sources": 6,
        "indexed_records": 84231,
        "active_agents": 8,
        "actions_today": 143,
        "pending_approvals": 7,
        "recent_activity": [
            {"id": 1, "text": "Freshservice ticket updated", "status": "success"},
            {"id": 2, "text": "Slack context retrieved", "status": "success"},
            {"id": 3, "text": "Voice request completed", "status": "success"},
            {"id": 4, "text": "Action awaiting approval", "status": "warning"},
        ]
    }

@app.get("/api/knowledge/search")
def search_knowledge(q: str, db: Session = Depends(get_db)):
    return {"results": [], "query": q}

from .services.freshservice import freshservice_client

@app.get("/api/tickets")
def get_tickets():
    try:
        tickets = freshservice_client.search_tickets()
        return {"tickets": tickets}
    except Exception as e:
        return {"error": str(e)}

from .services.agent import axiom_agent

@app.post("/api/agent/chat")
def agent_chat(payload: dict):
    message = payload.get("message", "")
    try:
        # 1. Context Retrieval (Mocking Context Engine from PRD)
        tickets = freshservice_client.search_tickets()
        context_str = "Recent Tickets:\n"
        for t in tickets[:5]: # Limit to top 5
            context_str += f"- Ticket #{t.get('id')}: {t.get('subject')} (Status: {t.get('status')})\n"
            
        # 2. Reasoning (Claude)
        reply = axiom_agent.process_chat(message, context_str)
        return {"response": reply}
    except Exception as e:
        return {"error": str(e)}
