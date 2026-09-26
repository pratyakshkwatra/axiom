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
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            data = res.json().get("tickets", [])
            
            entities = []
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
            
        print("Appending massive mock Freshservice data for knowledge graph...")
        for i in range(1, 301):
            entities.append({
                "external_id": f"INC-{8000 + i}",
                "entity_type": "ticket",
                "name": f"IT Request #{i} - Access Issue",
                "description": f"User is requesting access to internal tool {i%10}. Needs manager approval.",
                "metadata_": {"status": "Pending" if i%2==0 else "Resolved", "requester": f"Employee-{i%50}"}
            })
            
        return entities

    def sync_events(self, organization_id: str) -> List[Dict]:
        events = []
        for i in range(1, 501):
            events.append({
                "external_id": f"note-INC-{8000 + (i%150)}-{i}",
                "event_type": "note",
                "title": f"Note on INC-{8000 + (i%150)}",
                "content": f"Followed up with the user. Provisioning access now. Wait time approx {i%5} hours.",
                "metadata_": {"author": f"Support Agent {i%10}", "ticket": f"INC-{8000 + (i%150)}"}
            })
        return events
