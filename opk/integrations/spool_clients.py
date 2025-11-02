from __future__ import annotations
from typing import Dict, Any, List, Optional


class SpoolClientBase:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    # CRUD stubs — to be implemented with real HTTP calls
    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def read(self, item_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def update(self, item_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def delete(self, item_id: str) -> bool:
        raise NotImplementedError

    def search(self, query: str) -> List[Dict[str, Any]]:
        raise NotImplementedError


class SpoolmanClient(SpoolClientBase):
    pass


class TigerTagClient(SpoolClientBase):
    pass


class OpenSpoolClient(SpoolClientBase):
    pass


def get_client(source: str, base_url: str, api_key: Optional[str] = None) -> SpoolClientBase:
    s = source.lower()
    if s == 'spoolman':
        return SpoolmanClient(base_url, api_key)
    if s == 'tigertag':
        return TigerTagClient(base_url, api_key)
    if s in ('openspool','opentag3d'):
        return OpenSpoolClient(base_url, api_key)
    raise ValueError(f"Unknown source: {source}")

