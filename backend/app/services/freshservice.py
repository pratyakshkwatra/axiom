import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

FRESHSERVICE_DOMAIN = os.getenv("FRESHSERVICE_DOMAIN")
FRESHSERVICE_API_KEY = os.getenv("FRESHSERVICE_API_KEY")

class FreshserviceClient:
    def __init__(self):
        self.domain = FRESHSERVICE_DOMAIN
        self.api_key = FRESHSERVICE_API_KEY
        self.base_url = f"https://{self.domain}/api/v2"

    def _get_headers(self):
        # Freshservice uses Basic Auth with API Key as the username and a dummy password "X"
        auth_string = f"{self.api_key}:X"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }

    def search_tickets(self, query=None):
        url = f"{self.base_url}/tickets"
        # Optional query filtering can be applied here
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json().get("tickets", [])

    def get_ticket(self, ticket_id):
        url = f"{self.base_url}/tickets/{ticket_id}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json().get("ticket", {})

freshservice_client = FreshserviceClient()
