import io
from urllib.error import HTTPError
import builtins
from opk.integrations.spool_clients import SpoolmanClient


class _Resp:
    def __init__(self, status=200, headers=None, body=b"{}"):
        self.status = status
        self.headers = headers or {}
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_request_retries_respects_env_limit(monkeypatch):
    calls = {"n": 0}

    def fake_urlopen(req, context=None, timeout=None):
        calls["n"] += 1
        # fail with 500 twice, then succeed
        if calls["n"] < 3:
            fp = io.BytesIO(b"{\"err\":true}")
            raise HTTPError(url="http://x", code=500, msg="boom", hdrs={}, fp=fp)
        return _Resp(status=200, headers={"X-Total-Count": "1"}, body=b"{}")

    monkeypatch.setenv("OPK_NET_RETRY_LIMIT", "3")
    # Avoid real sleeping; count calls
    sleep_calls = {"n": 0, "args": []}
    def fake_sleep(s):
        sleep_calls["n"] += 1
        sleep_calls["args"].append(s)
    monkeypatch.setattr("time.sleep", fake_sleep)
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    cli = SpoolmanClient("http://example")
    status, body, hdrs = cli._request("/api/spools/1")
    assert status == 200 and calls["n"] == 3 and sleep_calls["n"] == 2


def test_no_retry_on_404(monkeypatch):
    calls = {"n": 0}

    def fake_urlopen(req, context=None, timeout=None):
        calls["n"] += 1
        fp = io.BytesIO(b"not found")
        raise HTTPError(url="http://x", code=404, msg="nope", hdrs={}, fp=fp)

    monkeypatch.setenv("OPK_NET_RETRY_LIMIT", "5")
    monkeypatch.setattr("time.sleep", lambda s: None)
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    cli = SpoolmanClient("http://example")
    status, body, hdrs = cli._request("/api/spools/404")
    assert status == 404 and calls["n"] == 1
