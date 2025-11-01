from __future__ import annotations
from typing import Dict, Any, List


def list_sources() -> List[str]:
    return [
        "OpenFilamentDatabase", "PrusaPrinters", "CuraMarketplace", "FilamentPM", "Printables"
    ]


def search_remote(source: str, query: str) -> List[Dict[str, Any]]:
    # Stub: return empty list (network features can be implemented later)
    # Would perform HTTP requests to public APIs where available
    return []


def sync_remote(source: str, tag: Dict[str, Any]) -> bool:
    # Stub: return False to indicate no-op
    return False

