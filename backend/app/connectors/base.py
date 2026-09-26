from abc import ABC, abstractmethod
from typing import List, Dict

class Connector(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        pass

    @abstractmethod
    def sync_entities(self, organization_id: str) -> List[Dict]:
        """
        Returns a list of dicts representing entities to be upserted.
        Expected keys: external_id, entity_type, name, description, metadata_
        """
        pass

    @abstractmethod
    def sync_events(self, organization_id: str) -> List[Dict]:
        """
        Returns a list of dicts representing events.
        Expected keys: external_id, event_type, title, content, metadata_
        """
        pass
