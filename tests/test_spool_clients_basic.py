from opk.integrations.spool_clients import SpoolmanClient, TigerTagClient, OpenSpoolClient, SpoolClientBase, get_client, SpoolClientError


def test_spoolman_read_search_with_monkeypatch(monkeypatch):
    # Force deterministic JSON for read/search without network
    def fake_get_json_first_ok(self, candidates):
        # Ensure override formatting works by inspecting first candidate
        assert isinstance(candidates, list) and candidates
        path, params = candidates[0]
        assert isinstance(path, str)
        # Return a successful object
        return True, {"id": 123, "vendor": "Test"}

    monkeypatch.setattr(SpoolClientBase, "_get_json_first_ok", fake_get_json_first_ok)
    c = SpoolmanClient("http://example")
    obj = c.read("123")
    assert obj.get("id") == 123
    res = c.search("PLA")
    # fake returns dict; search should wrap dict in list
    assert isinstance(res, list) and res and isinstance(res[0], dict)


def test_tigertag_create_update_delete(monkeypatch):
    calls = {"last": None}

    def fake_request(self, path, method="GET", params=None, payload=None):
        calls["last"] = (method, path, params, payload)
        if method == "POST":
            return 201, b"{\"id\": 99, \"ok\": true}", {}
        if method == "PUT":
            return 200, b"{\"id\": 99, \"ok\": true, \"updated\": true}", {}
        if method == "DELETE":
            return 204, b"", {}
        return 404, b"", {}

    monkeypatch.setattr(SpoolClientBase, "_request", fake_request)
    c = TigerTagClient("http://example")
    created = c.create({"name": "New Spool"})
    assert created.get("id") == 99 and created.get("ok") is True
    updated = c.update("99", {"name": "Updated"})
    assert updated.get("updated") is True
    ok = c.delete("99")
    assert ok is True


def test_openspool_override_endpoints(monkeypatch):
    # Verify endpoints override is applied and formatted
    seen = {"candidates": None}

    def fake_get_json_first_ok(self, candidates):
        seen["candidates"] = candidates
        return True, {"id": "abc"}

    monkeypatch.setattr(SpoolClientBase, "_get_json_first_ok", fake_get_json_first_ok)
    overrides = {
        "read": [("/custom/sp/{id}", None)],
        "search": [("/custom/search", {"q": "{q}"})],
    }
    c = OpenSpoolClient("http://example", endpoints=overrides)
    _ = c.read("abc")
    cand = seen["candidates"][0]
    assert cand[0] == "/custom/sp/abc"
    _ = c.search("PETG")
    cand2 = seen["candidates"][0]
    assert cand2[0] == "/custom/search" and cand2[1].get("q") == "PETG"


def test_get_client_with_overrides(monkeypatch):
    seen = {"candidates": None}

    def fake_get_json_first_ok(self, candidates):
        seen["candidates"] = candidates
        return True, {"id": "1"}

    monkeypatch.setattr(SpoolClientBase, "_get_json_first_ok", fake_get_json_first_ok)
    overrides = {"read": [("/x/{id}", None)]}
    cli = get_client("spoolman", "http://x", endpoints=overrides)
    _ = cli.read("1")
    assert seen["candidates"][0][0] == "/x/1"


def test_search_normalized_uses_headers(monkeypatch):
    # Simulate header-based total count and JSON list body
    def fake_get(self, path, params=None):
        body = b"[{\"id\":1},{\"id\":2}]"
        headers = {"x-total-count": "42"}
        return 200, body, headers

    monkeypatch.setattr(SpoolClientBase, "_get", fake_get)
    cli = SpoolmanClient("http://example")
    res = cli.search_normalized("PLA", page=2, page_size=2)
    assert res["total"] == 42 and res["count"] == 2 and res["page"] == 2


def test_errors_raise_spoolclienterror(monkeypatch):
    def fake_first_ok_with_meta(self, candidates):
        return False, None, {"status": 404, "url": "http://x/api/spools"}

    monkeypatch.setattr(SpoolClientBase, "_get_json_first_ok_with_meta", fake_first_ok_with_meta)
    cli = OpenSpoolClient("http://example")
    try:
        cli.search_normalized("foo")
        assert False, "expected error"
    except SpoolClientError as e:
        assert isinstance(e, SpoolClientError)
