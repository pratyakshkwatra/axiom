from .base import Connector
from .jira import JiraConnector
from .slack import SlackConnector
from .freshservice import FreshserviceConnector

ACTIVE_CONNECTORS = [
    JiraConnector(),
    SlackConnector(),
    FreshserviceConnector()
]

__all__ = ["Connector", "ACTIVE_CONNECTORS"]
