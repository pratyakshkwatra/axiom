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
            print("WARNING: Jira credentials missing, returning empty")
            return []
            
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
        # Issue comment ingestion not implemented yet
        return []
