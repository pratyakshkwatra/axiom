# AXIOM

AXIOM is the context and action layer for enterprise AI. It provides permission-aware understanding of organizational context by connecting multiple enterprise systems (like Slack, Freshservice, Jira) and exposing this context to both users (via Slack/Voice/Web) and other AI agents (via MCP).

## Tech Stack
- **Backend**: Python (FastAPI, Pydantic, SQLAlchemy)
- **Database**: PostgreSQL (pgvector), Redis
- **AI**: Claude Sonnet 4.6 (Anthropic API)
- **Frontend**: Next.js (React)
- **Integrations**: Slack, Freshservice, Gmail, etc.

## Project Structure
- `backend/`: FastAPI application containing core API logic, models, and context engine integrations.
- `frontend/`: Next.js web application for administrative oversight and reporting.
