import json
import importlib
import sys
from types import SimpleNamespace


class _FakeClient:
    def __init__(self):
        self.calls = []

    def create(self, payload):
        self.calls.append(("create", payload))
        return {"id": 1, **payload}

    def read(self, item_id):
        self.calls.append(("read", item_id))
        return {"id": item_id, "name": "X"}

    def update(self, item_id, payload):
        self.calls.append(("update", item_id, payload))
        return {"id": item_id, **payload}

    def delete(self, item_id):
        self.calls.append(("delete", item_id))
        return True

    def search(self, query, page=None, page_size=None):
        self.calls.append(("search", query, page, page_size))
        return [{"id": 1}]

    def search_normalized(self, query, page=1, page_size=50):
        self.calls.append(("search_normalized", query, page, page_size))
        return {"source": "spoolman", "query": query, "page": page, "page_size": page_size, "items": [{"id": 1}], "count": 1, "total": 1}

    # normalized wrappers
    def create_normalized(self, payload):
        return {"source": "spoolman", "action": "create", "item": self.create(payload)}

    def read_normalized(self, item_id):
        return {"source": "spoolman", "action": "read", "id": str(item_id), "item": self.read(item_id)}

    def update_normalized(self, item_id, payload):
        return {"source": "spoolman", "action": "update", "id": str(item_id), "item": self.update(item_id, payload)}

    def delete_normalized(self, item_id):
        return {"source": "spoolman", "action": "delete", "id": str(item_id), "ok": True}


def _run(argv, monkeypatch):
    mod = importlib.import_module('opk.cli.__main__')
    monkeypatch.setattr('opk.integrations.spool_clients.get_client', lambda *a, **k: _FakeClient())
    old = sys.argv
    try:
        sys.argv = ["opk"] + argv
        try:
            mod.main()
        except SystemExit as e:
            if e.code not in (0, None):
                raise
    finally:
        sys.argv = old


def test_cli_spool_read_normalized(monkeypatch, capsys):
    _run(["spool", "--source", "spoolman", "--base-url", "http://x", "--action", "read", "--id", "123", "--format", "normalized"], monkeypatch)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["action"] == "read" and data["id"] == "123" and isinstance(data.get("item"), dict)


def test_cli_spool_delete_normalized(monkeypatch, capsys):
    _run(["spool", "--source", "spoolman", "--base-url", "http://x", "--action", "delete", "--id", "7", "--format", "normalized"], monkeypatch)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["action"] == "delete" and data["ok"] is True and data["id"] == "7"


def test_cli_spool_search_items(monkeypatch, capsys):
    _run(["spool", "--source", "spoolman", "--base-url", "http://x", "--action", "search", "--query", "PLA", "--page", "2", "--page-size", "10", "--format", "items"], monkeypatch)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list) and data and data[0]["id"] == 1
