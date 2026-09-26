from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..db.session import get_db
from ..services.retrieval import search_context

router = APIRouter()

class SearchQuery(BaseModel):
    query: str
    organization_id: str
    user_role: str

@router.post("/search")
def search(query_data: SearchQuery, db: Session = Depends(get_db)):
    # Mocking user extraction from JWT for the endpoint
    user = {
        "organization_id": query_data.organization_id,
        "role": query_data.user_role
    }
    
    try:
        results = search_context(query_data.query, user, db)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph")
def get_graph(db: Session = Depends(get_db)):
    """
    Returns a massive mock knowledge graph representing an interconnected enterprise.
    """
    nodes = [
        # People
        {"id": "p1", "label": "Pratyaksh", "group": "person", "val": 3},
        {"id": "p2", "label": "Sarah Chen", "group": "person", "val": 2},
        {"id": "p3", "label": "Rahul", "group": "person", "val": 2},
        {"id": "p4", "label": "Alex", "group": "person", "val": 1.5},
        
        # Jira Issues
        {"id": "j1", "label": "ENG-992: Redis Migration", "group": "jira", "val": 2},
        {"id": "j2", "label": "ENG-1045: Fix Auth Bug", "group": "jira", "val": 1.5},
        {"id": "j3", "label": "PROD-22: Project Atlas", "group": "jira", "val": 3},
        {"id": "j4", "label": "PROD-45: Acme Escalation", "group": "jira", "val": 2.5},
        
        # Slack Channels/Threads
        {"id": "s1", "label": "#architecture", "group": "slack", "val": 2},
        {"id": "s2", "label": "#project-atlas", "group": "slack", "val": 2.5},
        {"id": "s3", "label": "Acme payment issue thread", "group": "slack", "val": 1.5},
        {"id": "s4", "label": "#incidents", "group": "slack", "val": 2},
        
        # Freshservice
        {"id": "f1", "label": "TKT-88912: Acme Payment Failed", "group": "freshservice", "val": 2},
        {"id": "f2", "label": "TKT-89004: DB Latency", "group": "freshservice", "val": 1.5},
        
        # GitHub
        {"id": "g1", "label": "PR #443: Auth Patch", "group": "github", "val": 2},
        {"id": "g2", "label": "PR #421: Redis setup", "group": "github", "val": 1.5},
        {"id": "g3", "label": "Repo: axiom-core", "group": "github", "val": 3},
        
        # Notion
        {"id": "n1", "label": "Atlas Architecture Spec", "group": "notion", "val": 2},
        {"id": "n2", "label": "HR Compensation Policy", "group": "notion", "val": 1.5},
        
        # PagerDuty / Datadog
        {"id": "pd1", "label": "INC-921: Access Denied Alert", "group": "pagerduty", "val": 1.5},
        {"id": "dd1", "label": "Monitor: DB Latency High", "group": "datadog", "val": 1.5},
        
        # Google Drive
        {"id": "d1", "label": "Q3 Planning.pdf", "group": "drive", "val": 1.5},
    ]
    
    edges = [
        # People to Projects/Tickets
        {"source": "p2", "target": "n2"},
        {"source": "p1", "target": "j3"},
        {"source": "p3", "target": "j1"},
        {"source": "p4", "target": "f1"},
        {"source": "p1", "target": "g1"},
        
        # Jira to other systems
        {"source": "j1", "target": "s1"},
        {"source": "j1", "target": "g2"},
        {"source": "j3", "target": "s2"},
        {"source": "j3", "target": "n1"},
        {"source": "j4", "target": "f1"},
        {"source": "j4", "target": "s3"},
        
        # GitHub to Systems
        {"source": "g3", "target": "g1"},
        {"source": "g3", "target": "g2"},
        {"source": "g1", "target": "j2"},
        
        # Incidents
        {"source": "f2", "target": "dd1"},
        {"source": "dd1", "target": "s4"},
        {"source": "pd1", "target": "s4"},
        
        # Cross-context
        {"source": "n1", "target": "d1"},
        {"source": "p1", "target": "s1"},
        {"source": "p1", "target": "s2"},
        {"source": "p3", "target": "n2"},
    ]
    
    return {"nodes": nodes, "links": edges}

@router.post("/chat")
def chat_with_agent(query_data: SearchQuery, db: Session = Depends(get_db)):
    """
    GPT-like chat interface that uses Claude to answer questions based on the retrieved context,
    and generates dynamic charts if requested.
    """
    import os
    from anthropic import Anthropic
    import json
    import re
    
    # 1. Retrieve Context
    user = {"organization_id": query_data.organization_id, "role": query_data.user_role}
    try:
        results = search_context(query_data.query, user, db, limit=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context search failed: {str(e)}")

    # 2. Format Context
    context_str = f"Context (the user is signed in as role {query_data.user_role}):\n"
    for e in results.get("entities", []):
        context_str += f"Entity: {e.get('name')} (Type: {e.get('type')}, Source: {e.get('source')}) - {e.get('description')} Metadata: {e.get('metadata')}\n"
    for ev in results.get("events", []):
        context_str += f"Event: {ev.get('title')} (Type: {ev.get('type')}, Source: {ev.get('source')}) - {ev.get('content')}\n"
    withheld = results.get("withheld", {})
    if withheld:
        blocked = ", ".join(f"{count} {kind}" for kind, count in withheld.items())
        context_str += f"\nPOLICY ENFORCEMENT: AXIOM withheld {sum(withheld.values())} matching records ({blocked}) because role {query_data.user_role} is not authorized to read them. You MUST tell the user that these records exist but were withheld by access policy, never guess their contents, and include <ui_component>permission_check</ui_component>.\n"
    
    # 3. Call Claude
    client = Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        default_headers={"anthropic-workspace-id": os.getenv("ANTHROPIC_WORKSPACE_ID", "")} if os.getenv("ANTHROPIC_WORKSPACE_ID") else {}
    )
    prompt = f"""You are AXIOM, an enterprise AI assistant. Answer the user's question using ONLY the provided context.
If the user asks for analytics, a graph, a dashboard, or ticket distributions, you must ALSO generate a chart.
To generate a chart, include a JSON array of objects with 'name' and 'value' properties inside <chart></chart> xml tags.
Example:
<chart>
[
  {{"name": "Open", "value": 45}},
  {{"name": "Closed", "value": 12}}
]
</chart>

If the user asks to create an AI support agent, manage agents, or something similar, you MUST include the following tag in your response:
<ui_component>agent_configuration</ui_component>

If the user asks about access policies, engineering managers, or RBAC, you MUST include the following tag in your response:
<ui_component>policy_preview</ui_component>

If the user asks to show everything known about a specific project (e.g., Project Atlas) or customer, you MUST include:
<ui_component>context_view</ui_component>

If the user asks to send a message, create a ticket, or take a destructive action, you MUST request confirmation by including:
<ui_component>action_confirmation</ui_component>

If the user asks to show what an agent did, view an audit log, or view activity history, you MUST include:
<ui_component>audit_timeline</ui_component>

If the user asks to visualize the organization graph, zoom into nodes, or see the network, you MUST include:
<ui_component>knowledge_graph</ui_component>

If the user asks for restricted resources or something they shouldn't access, you MUST include:
<ui_component>permission_check</ui_component>

ALWAYS include 1-3 suggested follow-up questions for the user, enclosed in a <suggestions> JSON array </suggestions> tag.
Example:
<suggestions>
["Show me more details", "Generate an audit log"]
</suggestions>

{context_str}

User Question: {query_data.query}"""

    try:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY is not set")
            
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = message.content[0].text
        
        # Parse chart data if present
        chart_data = []
        chart_match = re.search(r'<chart>(.*?)</chart>', response_text, re.DOTALL)
        if chart_match:
            try:
                chart_data = json.loads(chart_match.group(1).strip())
                response_text = re.sub(r'<chart>.*?</chart>', '', response_text, flags=re.DOTALL).strip()
            except json.JSONDecodeError:
                pass

        # Parse UI component if present
        ui_component = None
        component_match = re.search(r'<ui_component>(.*?)</ui_component>', response_text)
        if component_match:
            ui_component = component_match.group(1).strip()
            response_text = re.sub(r'<ui_component>.*?</ui_component>', '', response_text).strip()
            
        # Parse suggestions if present
        suggestions = ["Tell me more", "What else?"]
        suggestions_match = re.search(r'<suggestions>(.*?)</suggestions>', response_text, re.DOTALL)
        if suggestions_match:
            try:
                suggestions = json.loads(suggestions_match.group(1).strip())
                response_text = re.sub(r'<suggestions>.*?</suggestions>', '', response_text, flags=re.DOTALL).strip()
            except json.JSONDecodeError:
                pass
                
        return {"answer": response_text, "chartData": chart_data, "uiComponent": ui_component, "suggestions": suggestions}
    except Exception as e:
        # MOCK RESPONSE FOR PROTOTYPING IF CLAUDE FAILS / KEY MISSING
        query_lower = query_data.query.lower()
        mock_ui = None
        mock_text = "I've processed your request."
        suggestions = []
        if "agent" in query_lower:
            mock_ui = "agent_configuration"
            mock_text = "I've synthesized the required permissions and data streams. Review the autonomous agent constraints before deployment:"
            suggestions = ["What models does this agent use?", "Set up a fallback policy", "Test this agent in sandbox"]
        elif "policy" in query_lower or "breach" in query_lower:
            mock_ui = "policy_preview"
            mock_text = "I ran a dynamic simulation against current RBAC controls. Here is the active access topography:"
            suggestions = ["Apply this to the entire Engineering org", "What happens if a manager is on leave?", "View policy audit logs"]
        elif "atlas" in query_lower or "sentiment" in query_lower:
            mock_ui = "context_view"
            mock_text = "I've aggregated millions of data points across Slack, Jira, and GitHub. Here is the synthesized reality of the project:"
            suggestions = ["Why was the architecture changed?", "Who made the last commit?", "Draft a status update for the CEO"]
        elif "send" in query_lower or "message" in query_lower or "status update" in query_lower:
            mock_ui = "action_confirmation"
            mock_text = "Awaiting biometric or explicit authorization to execute real-world write action:"
            suggestions = ["Cancel and rewrite the message", "CC the product managers", "Schedule this for tomorrow at 9AM"]
        elif "did" in query_lower or "audit" in query_lower:
            mock_ui = "audit_timeline"
            mock_text = "Reconstructing timeline of agent activities:"
            suggestions = ["Export this log to CSV", "Show me denied actions only", "Who created this policy?"]
        elif "visualize" in query_lower or "graph" in query_lower:
            mock_ui = "knowledge_graph"
            mock_text = "Rendering the knowledge graph of your enterprise across all tools:"
            suggestions = ["Zoom into Engineering node", "Show orphaned projects", "Filter by Jira tickets only"]
        
        # --- Handle specific follow-up suggestions ---
        elif "architecture changed" in query_lower:
            mock_text = "According to Jira ticket ENG-992 and a Slack thread in #architecture, the change was made because the previous caching layer couldn't handle the new vector search load. The team migrated to Redis."
            suggestions = ["Show me the Jira ticket", "Who approved this change?"]
        elif "models does this" in query_lower:
            mock_text = "This agent is currently configured to use a hybrid routing approach. It defaults to Claude 3.5 Sonnet for standard context retrieval, and escalates to Claude 3 Opus for complex reasoning tasks."
            suggestions = ["Force it to use GPT-4o", "Show rate limits"]
        elif "sandbox" in query_lower:
            mock_text = "Sandbox initialized. The agent is now running in an isolated container. You can safely simulate prompts without affecting production data."
            suggestions = ["Run a breach simulation", "Check sandbox memory usage"]
        elif "engineering org" in query_lower or "entire engineering" in query_lower:
            mock_ui = "policy_preview"
            mock_text = "I have expanded the target scope to the entire Engineering Organization (142 members). Please review the updated policy graph."
            suggestions = ["Test policy in staging", "Deploy to production"]
        elif "manager is on leave" in query_lower:
            mock_text = "If a manager is on leave, the Policy Engine automatically routes access requests to their designated backup or the Director of Engineering, depending on the urgency score of the request."
            suggestions = ["Set up a backup mapping", "Show me the routing rules"]
        elif "export this log" in query_lower:
            mock_text = "The audit log has been exported and securely sent to your email."
            suggestions = ["Clear audit logs", "Show me denied actions only"]
        elif "denied actions only" in query_lower:
            mock_ui = "audit_timeline"
            mock_text = "Filtering the audit timeline. Displaying ONLY actions that were blocked by the Policy Engine:"
            suggestions = ["Who created this policy?", "Export to CSV"]
            
        # --- NEW HANDLERS FOR REMAINING SUGGESTIONS ---
        elif "zoom into engineering node" in query_lower:
            mock_ui = "knowledge_graph"
            mock_text = "Zooming into the Engineering sub-graph. I found 42 interconnected nodes relating to active pull requests, deployment pipelines, and Jira epics."
            suggestions = ["Filter by Jira tickets only", "Show orphaned projects"]
        elif "show orphaned projects" in query_lower:
            mock_ui = "knowledge_graph"
            mock_text = "Highlighting 3 orphaned projects with no active commits in the last 90 days. Would you like me to draft an archival request?"
            suggestions = ["Draft archival request", "Who owns these projects?"]
        elif "filter by jira tickets only" in query_lower:
            mock_ui = "knowledge_graph"
            mock_text = "Applied filter. The graph now only displays nodes and relationships sourced directly from Atlassian Jira."
            suggestions = ["Zoom into Engineering node", "Clear filters"]
        elif "draft a status update" in query_lower:
            mock_text = "I've drafted a status update: 'Project Atlas is currently 85% complete. We experienced a minor delay due to the Redis migration (ENG-992), but we are on track for Friday.' Should I send this?"
            suggestions = ["Send to CEO", "Make it sound more urgent"]
        elif "cancel and rewrite" in query_lower:
            mock_text = "Action cancelled. Please tell me what you'd like to say instead."
            suggestions = []
        elif "schedule this for tomorrow" in query_lower:
            mock_text = "Done. This action has been securely queued and will automatically execute tomorrow at 9:00 AM local time."
            suggestions = ["Cancel scheduled action", "Show scheduled actions"]
        elif "who created this policy" in query_lower:
            mock_text = "This policy was originally created by Sarah Chen (Head of Security) on October 12, 2024, and was last modified by an automated AXIOM rotation script."
            suggestions = ["View policy history", "Revoke policy"]
        elif "compensation" in query_lower:
            mock_ui = "permission_check"
            mock_text = "Access denied by HR Compensation Policy. Your role (Engineering Manager) does not have explicit read access to this resource."
            suggestions = ["Request temporary access", "View public org chart"]
        elif "show me the jira ticket" in query_lower:
            mock_text = "Here is the summary of ENG-992 (Redis Migration):\n\nStatus: IN PROGRESS\nAssignee: Rahul\nDescription: Migrating the vector cache from in-memory to Redis to handle scale. Expecting 2 hours of downtime this weekend."
            suggestions = ["Who approved this change?", "Tell me more"]
        elif "who approved this change" in query_lower:
            mock_text = "The architectural change was approved by Alex (VP of Engineering) on Oct 10th during the Q4 Technical Review."
            suggestions = ["Show me the context around Project Atlas", "Draft a status update for the CEO"]
        elif "context around project atlas" in query_lower or "project atlas" in query_lower:
            mock_ui = "context_view"
            mock_text = "Project Atlas is the Q4 initiative to overhaul the billing engine. I found 3 active Slack channels, 12 Jira Epics, and 4 Google Drive docs related to it."
            suggestions = ["Why is the Acme escalation still unresolved?", "Who made the last commit?"]
        elif "acme escalation" in query_lower:
            mock_text = "The Acme escalation (TKT-88912) is unresolved because it's blocked by the Redis migration (ENG-992). The DB latency caused their payment webhooks to time out."
            suggestions = ["Make it sound more urgent", "CC the product managers"]
        elif "create a support agent" in query_lower or "configure an agent" in query_lower:
            mock_ui = "agent_configuration"
            mock_text = "I've started drafting a new Support Agent. It will need read-access to Freshservice and Slack. Please review the configuration."
            suggestions = ["What models does this agent use?", "Test this agent in sandbox"]
        elif "access customer data" in query_lower:
            mock_ui = "policy_preview"
            mock_text = "Currently, only the 'Customer Success Core' group (24 users) and 2 autonomous agents have access to raw customer data. Here is the topology."
            suggestions = ["Simulate a breach on current access policies", "Apply this to the entire Engineering org"]
        elif "tell me more" in query_lower or "what else" in query_lower:
            mock_text = "I also noticed that the DB latency alerts in Datadog are correlated with the recent spike in API traffic. We might want to provision more read replicas."
            suggestions = ["Deploy an autonomous DevOps agent", "Run a breach simulation"]
        elif "set up a fallback policy" in query_lower:
            mock_text = "Fallback policy established. If the primary authorization service goes down, the system will temporarily default to read-only for all non-admin roles."
            suggestions = ["View policy audit logs", "Show me the routing rules"]
        elif "who made the last commit" in query_lower:
            mock_text = "The last commit to the 'axiom-core' repo was made by Pratyaksh 42 minutes ago: 'fix(auth): patch JWT validation bypass'."
            suggestions = ["Show orphaned projects", "Clear filters"]
        elif "cc the product managers" in query_lower:
            mock_text = "I've added the product-management@axiom.local group to the notification chain. They will be CC'd on the next update."
            suggestions = ["Draft a status update for the CEO", "Cancel and rewrite"]
        elif "clear audit logs" in query_lower:
            mock_text = "Audit logs cannot be cleared by an Engineering Manager. This requires dual-authorization from the Security team."
            suggestions = ["Request temporary access", "Who created this policy?"]
        elif "draft archival request" in query_lower:
            mock_text = "Drafted: 'To all engineering leads, I am requesting to archive the legacy reporting microservices due to 90+ days of inactivity.' Should I post this to Slack?"
            suggestions = ["Send to CEO", "Cancel and rewrite"]
        elif "who owns these projects" in query_lower:
            mock_text = "According to the last active commits and Jira components, the legacy reporting projects are owned by Sarah Chen."
            suggestions = ["Show me who can access customer data", "Visualize the entire organization graph"]
        elif "clear filters" in query_lower:
            mock_ui = "knowledge_graph"
            mock_text = "Filters cleared. Displaying the complete enterprise context graph."
            suggestions = ["Zoom into Engineering node", "Filter by Jira tickets only"]
        elif "send to ceo" in query_lower:
            mock_ui = "action_confirmation"
            mock_text = "Preparing to send the update to the CEO. Please confirm."
            suggestions = ["Schedule this for tomorrow at 9AM", "Cancel and rewrite"]
        elif "make it sound more urgent" in query_lower:
            mock_text = "Updated draft: 'URGENT: Project Atlas is blocked by critical DB latency (ENG-992). The Acme escalation is currently failing SLA. Immediate intervention required on the Redis migration.'"
            suggestions = ["Send to CEO", "CC the product managers"]
        elif "cancel scheduled action" in query_lower:
            mock_text = "The scheduled action for 9:00 AM tomorrow has been successfully cancelled."
            suggestions = ["Show scheduled actions", "Visualize the entire organization graph"]
        elif "show scheduled actions" in query_lower:
            mock_text = "You have no more actions scheduled. Would you like to set up a recurring cron job for project updates?"
            suggestions = ["Yes, setup cron", "No, thanks"]
        elif "view policy history" in query_lower:
            mock_ui = "audit_timeline"
            mock_text = "Here is the historical audit trail for this policy, including all changes made over the last 90 days."
            suggestions = ["Export this log to CSV", "Revoke policy"]
        elif "revoke policy" in query_lower:
            mock_ui = "action_confirmation"
            mock_text = "WARNING: Revoking this policy will instantly drop access for 142 engineers. Are you sure you want to proceed?"
            suggestions = ["Yes, revoke", "Cancel and rewrite"]
        elif "request temporary access" in query_lower:
            mock_text = "A temporary access request (4 hours) has been routed to HR and the Security team for approval."
            suggestions = ["Show scheduled actions", "View public org chart"]
        elif "view public org chart" in query_lower:
            mock_ui = "knowledge_graph"
            mock_text = "Here is the public organizational chart. You can click on any person to see their public context and current projects."
            suggestions = ["Zoom into Engineering node", "Show orphaned projects"]
        elif "show agent audit log" in query_lower:
            mock_ui = "audit_timeline"
            mock_text = "Loading the audit log for all autonomous agents across the network."
            suggestions = ["Show me denied actions only", "Export to CSV"]
        elif "visualize the entire organization graph" in query_lower or "organization graph" in query_lower:
            mock_ui = "knowledge_graph"
            mock_text = "Rendering the complete enterprise graph, spanning all users, systems, and active data streams."
            suggestions = ["Zoom into Engineering node", "Filter by Jira tickets only"]
        elif "force it to use gpt" in query_lower:
            mock_text = "Routing enforced. The agent is now hard-pinned to GPT-4o for all reasoning steps. Note that this may increase latency by ~120ms."
            suggestions = ["Test this agent in sandbox", "Show rate limits"]
        elif "show rate limits" in query_lower:
            mock_text = "Current utilization: 42,000 / 100,000 tokens per minute. You have plenty of headroom for this agent."
            suggestions = ["Deploy an autonomous DevOps agent", "Visualize the entire organization graph"]
        elif "run a breach simulation" in query_lower or "simulating a breach" in query_lower:
            mock_ui = "audit_timeline"
            mock_text = "Running a Monte Carlo breach simulation against the 'Customer Data' resource. Result: 2 vulnerabilities found where indirect access is possible."
            suggestions = ["Set up a fallback policy", "View policy audit logs"]
        elif "check sandbox memory usage" in query_lower:
            mock_text = "Sandbox memory usage is at 45MB. Vector store is consuming 12MB. The environment is healthy."
            suggestions = ["Test this agent in sandbox", "Deploy to production"]
        elif "test policy in staging" in query_lower:
            mock_text = "Policy deployed to staging environment. Running regression tests against 1,000 simulated access requests..."
            suggestions = ["Deploy to production", "Cancel scheduled action"]
        elif "deploy to production" in query_lower or "deploy an autonomous" in query_lower:
            mock_ui = "action_confirmation"
            mock_text = "Ready to deploy to production. This action will affect live infrastructure and user permissions. Awaiting authorization."
            suggestions = ["Proceed with deployment", "Cancel and rewrite"]
        elif "set up a backup mapping" in query_lower:
            mock_text = "Backup mapping configured: If Engineering Manager is unavailable, requests will route to VP of Engineering (Alex)."
            suggestions = ["Show me the routing rules", "Test policy in staging"]
        elif "show me the routing rules" in query_lower:
            mock_ui = "policy_preview"
            mock_text = "Here is the visual topology of the current approval routing rules."
            suggestions = ["Test policy in staging", "Apply this to the entire Engineering org"]
        elif "analyze sentiment" in query_lower:
            mock_ui = "context_view"
            mock_text = "I've analyzed sentiment across Jira, Slack, and Freshservice. Engineering morale seems strained due to the Redis migration, but customer support sentiment is holding steady."
            suggestions = ["Draft a status update for the CEO", "Show me the Jira ticket"]
        else:
            # Better fallback instead of "I've processed your request."
            mock_text = f"I've analyzed '{query_data.query}'. As an AI assistant, I can perform deep context retrieval, generate policies, or configure agents based on this intent."
            suggestions = ["Show agent audit log", "Visualize the entire organization graph"]
            
        return {"answer": mock_text, "chartData": [], "uiComponent": mock_ui, "suggestions": suggestions}
