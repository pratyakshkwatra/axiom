import os
import requests
import base64
from typing import List, Dict
from .base import Connector

class FreshserviceConnector(Connector):
    @property
    def source_name(self) -> str:
        return "freshservice"

    def _get_headers(self):
        api_key = os.getenv("FRESHSERVICE_API_KEY")
        domain = os.getenv("FRESHSERVICE_DOMAIN")
        if not api_key or not domain:
            print("WARNING: Freshservice credentials missing, returning empty")
            return None, None
        
        # Freshservice requires Base64 encoded 'api_key:X'
        auth_str = f"{api_key}:X"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/json"
        }
        return headers, domain

    def sync_entities(self, organization_id: str) -> List[Dict]:
        headers, domain = self._get_headers()
        if not headers:
            return []

        url = f"https://{domain}/api/v2/tickets"
        entities = []
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            data = res.json().get("tickets", [])

            for t in data:
                entities.append({
                    "external_id": f"INC-{t.get('id')}",
                    "entity_type": "ticket",
                    "name": t.get("subject", "No Subject"),
                    "description": t.get("description_text", ""),
                    "metadata_": {
                        "status": t.get("status"),
                        "priority": t.get("priority"),
                        "requester_id": t.get("requester_id")
                    }
                })
        except Exception as e:
            print(f"Failed to fetch real Freshservice tickets: {e}")

        return entities

    def sync_events(self, organization_id: str) -> List[Dict]:
        headers, domain = self._get_headers()
        if not headers:
            return []

        events = []
        try:
            res = requests.get(f"https://{domain}/api/v2/tickets", headers=headers, timeout=10)
            res.raise_for_status()
            for t in res.json().get("tickets", []):
                ticket_id = t.get("id")
                conv_res = requests.get(f"https://{domain}/api/v2/tickets/{ticket_id}/conversations", headers=headers, timeout=10)
                conv_res.raise_for_status()
                for c in conv_res.json().get("conversations", []):
                    events.append({
                        "external_id": f"note-INC-{ticket_id}-{c.get('id')}",
                        "event_type": "note",
                        "title": f"Note on INC-{ticket_id}",
                        "content": c.get("body_text", ""),
                        "metadata_": {"author_id": c.get("user_id"), "ticket": f"INC-{ticket_id}", "private": c.get("private")}
                    })
        except Exception as e:
            print(f"Failed to fetch real Freshservice conversations: {e}")

        return events
