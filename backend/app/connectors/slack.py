import os
import requests
from typing import List, Dict
from .base import Connector

class SlackConnector(Connector):
    @property
    def source_name(self) -> str:
        return "slack"

    def sync_entities(self, organization_id: str) -> List[Dict]:
        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            print("WARNING: Slack credentials missing, returning empty")
            return []
            
        headers = {"Authorization": f"Bearer {token}"}
        try:
            res = requests.get("https://slack.com/api/conversations.list", headers=headers, timeout=10)
            res.raise_for_status()
            channels = res.json().get("channels", [])
            
            entities = []
            for c in channels:
                entities.append({
                    "external_id": c.get("id"),
                    "entity_type": "project",
                    "name": f"#{c.get('name')}",
                    "description": c.get("purpose", {}).get("value", ""),
                    "metadata_": {"members": c.get("num_members", 0)}
                })
            return entities
        except Exception as e:
            print(f"Failed to fetch real Slack channels: {e}")
            return []

    def sync_events(self, organization_id: str) -> List[Dict]:
        # Message history ingestion (conversations.history) not implemented yet
        return []
