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
            print("WARNING: Slack credentials missing, generating massive mock data for knowledge graph.")
            entities = []
            for i in range(1, 51):
                entities.append({
                    "external_id": f"C01A2B3C4D{i}",
                    "entity_type": "project",
                    "name": f"#eng-team-{i}",
                    "description": f"Discussion channel for engineering team {i}.",
                    "metadata_": {"members": 10 + i}
                })
            return entities
            
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
        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            events = []
            import random
            for i in range(1, 801):
                channel_id = random.randint(1, 50)
                events.append({
                    "external_id": f"msg-{10000 + i}",
                    "event_type": "message",
                    "title": f"Message in #eng-team-{channel_id}",
                    "content": f"Discussing architecture for feature {i%50}. Let's make sure we handle edge cases properly.",
                    "metadata_": {"author": f"User-{i%30}", "channel": f"#eng-team-{channel_id}"}
                })
            return events
        return []
