import os
import requests
from requests.auth import HTTPBasicAuth
from typing import List, Dict
from .base import Connector

class JiraConnector(Connector):
    @property
    def source_name(self) -> str:
        return "jira"

    def sync_entities(self, organization_id: str) -> List[Dict]:
        url = os.getenv("JIRA_URL")
        email = os.getenv("JIRA_EMAIL")
        token = os.getenv("JIRA_API_TOKEN")
        if not url or not email or not token:
            print("WARNING: Jira credentials missing, generating massive mock data for knowledge graph.")
            entities = []
            for i in range(1, 201):
                status = "Open" if i % 3 == 0 else "In Progress" if i % 2 == 0 else "Closed"
                entities.append({
                    "external_id": f"PAY-{100 + i}",
                    "entity_type": "ticket",
                    "name": f"Payment gateway issue #{i}",
                    "description": f"Customer reported error {500 + (i%5)} during checkout flow.",
                    "metadata_": {"status": status, "assignee": f"Dev-{i%10}", "project": "Payments"}
                })
            return entities
            
        auth = HTTPBasicAuth(email, token)
        headers = {"Accept": "application/json"}
        try:
            res = requests.get(f"{url}/rest/api/3/search", headers=headers, auth=auth, timeout=10)
            res.raise_for_status()
            issues = res.json().get("issues", [])
            
            entities = []
            for issue in issues:
                fields = issue.get("fields", {})
                entities.append({
                    "external_id": issue.get("key"),
                    "entity_type": "ticket",
                    "name": fields.get("summary", ""),
                    "description": str(fields.get("description", "")),
                    "metadata_": {
                        "status": fields.get("status", {}).get("name"),
                        "assignee": fields.get("assignee", {}).get("displayName")
                    }
                })
            return entities
        except Exception as e:
            print(f"Failed to fetch real Jira issues: {e}")
            return []

    def sync_events(self, organization_id: str) -> List[Dict]:
        url = os.getenv("JIRA_URL")
        if not url:
            events = []
            for i in range(1, 401):
                events.append({
                    "external_id": f"comment-PAY-{100 + (i%100)}-{i}",
                    "event_type": "note",
                    "title": f"Comment on PAY-{100 + (i%100)}",
                    "content": f"Investigated logs for correlation ID {1000 + i}. It seems related to the third-party API rate limit.",
                    "metadata_": {"author": f"Dev-{(i+1)%10}", "issue": f"PAY-{100 + (i%100)}"}
                })
            return events
        return []
