from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import json
import urllib.request
import urllib.parse
import ssl
import os
import time
import random


class SpoolClientError(Exception):
    def __init__(self, message: str, *, status: Optional[int] = None, url: Optional[str] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.status = status
        self.url = url
        self.details = details


class SpoolClientHTTPError(SpoolClientError):
    pass


class SpoolClientNetworkError(SpoolClientError):
    pass


class SpoolClientNotFound(SpoolClientHTTPError):
    pass


class SpoolClientBase:
    SOURCE = "unknown"

    def __init__(self, base_url: str, api_key: Optional[str] = None, endpoints: Optional[Dict[str, Any]] = None, retry_limit: Optional[int] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self._override_endpoints = endpoints or {}
        self._retry_limit = self._load_retry_limit(retry_limit)
        self._retry_backoff, self._retry_jitter = self._load_retry_timing()

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

    # --- helpers ---------------------------------------------------------
    def _headers(self) -> Dict[str, str]:
        h = {
            "Accept": "application/json",
            "User-Agent": "OpenPrintKit/0.1 (+spool-client)",
        }
        if self.api_key:
            # Add common header variants; servers may accept one of these
            h["Authorization"] = f"Bearer {self.api_key}"
            h["X-Api-Key"] = self.api_key
        return h

    def _make_url(self, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url}{path}"
        if params:
            # Filter out Nones and encode
            q = {k: v for k, v in params.items() if v is not None}
            if q:
                url = f"{url}?{urllib.parse.urlencode(q)}"
        return url

    def _is_retryable_status(self, status: int) -> bool:
        # Retry on 408 Request Timeout, 429 Too Many Requests, and 5xx server errors
        return status in (408, 429) or 500 <= status < 600

    def _load_retry_limit(self, override: Optional[int]) -> int:
        # Priority: explicit override > env var > QSettings > default(5)
        if isinstance(override, int) and override >= 0:
            return override
        # Env var
        try:
            env = os.environ.get('OPK_NET_RETRY_LIMIT')
            if env is not None:
                n = int(env)
                if n >= 0:
                    return n
        except Exception:
            pass
        # QSettings (system preferences)
        try:
            from PySide6.QtCore import QSettings  # type: ignore
            s = QSettings("OpenPrintKit", "OPKStudio")
            n = int(s.value("net/retry_limit", 5))
            if n >= 0:
                return n
        except Exception:
            pass
        return 5

    def _load_retry_timing(self) -> Tuple[float, float]:
        # Defaults
        backoff = 0.5
        jitter = 0.25
        # Env var overrides
        try:
            env_b = os.environ.get('OPK_NET_RETRY_BACKOFF')
            if env_b is not None:
                backoff = max(0.0, float(env_b))
        except Exception:
            pass
        try:
            env_j = os.environ.get('OPK_NET_RETRY_JITTER')
            if env_j is not None:
                jitter = max(0.0, float(env_j))
        except Exception:
            pass
        # QSettings overrides
        try:
            from PySide6.QtCore import QSettings  # type: ignore
            s = QSettings("OpenPrintKit", "OPKStudio")
            b = float(s.value("net/retry_backoff", backoff))
            j = float(s.value("net/retry_jitter", jitter))
            backoff = max(0.0, b)
            jitter = max(0.0, j)
        except Exception:
            pass
        return backoff, jitter

    def _request(self, path: str, method: str = "GET", params: Optional[Dict[str, Any]] = None, payload: Optional[Dict[str, Any]] = None) -> Tuple[int, bytes, Dict[str, str]]:
        url = self._make_url(path, params)
        data = None
        headers = self._headers()
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        # Be permissive with SSL in environments that lack certs
        ctx = ssl.create_default_context()
        attempts = max(0, int(self._retry_limit)) + 1
        last_status, last_body, last_hdrs = 0, b"", {}
        for i in range(attempts):
            req = urllib.request.Request(url, headers=headers, method=method, data=data)
            try:
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    body = resp.read()
                    status = getattr(resp, 'status', 200)
                    hdrs = {k.lower(): v for k, v in resp.headers.items()}
                    return status, body, hdrs
            except urllib.error.HTTPError as e:
                body = e.read() if hasattr(e, 'read') else b''
                status = int(getattr(e, 'code', 0) or 0)
                hdrs = {k.lower(): v for k, v in getattr(e, 'headers', {}).items()} if getattr(e, 'headers', None) else {}
                # Retry only if status is retryable and we have more attempts left
                last_status, last_body, last_hdrs = status, body, hdrs
                if i < attempts - 1 and self._is_retryable_status(status):
                    # backoff with jitter
                    try:
                        sleep_s = (self._retry_backoff * (2 ** i)) + (random.uniform(0, self._retry_jitter) if self._retry_jitter > 0 else 0)
                        if sleep_s > 0:
                            time.sleep(sleep_s)
                    except Exception:
                        pass
                    continue
                return status, body, hdrs
            except Exception:
                # Network failure — retry if attempts remain, else return status 0
                last_status, last_body, last_hdrs = 0, b"", {}
                if i < attempts - 1:
                    try:
                        sleep_s = (self._retry_backoff * (2 ** i)) + (random.uniform(0, self._retry_jitter) if self._retry_jitter > 0 else 0)
                        if sleep_s > 0:
                            time.sleep(sleep_s)
                    except Exception:
                        pass
                    continue
                return 0, b"", {}
        # Should not reach here, return last captured info
        return last_status, last_body, last_hdrs

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Tuple[int, bytes, Dict[str, str]]:
        return self._request(path, method="GET", params=params, payload=None)

    def _get_json_first_ok(self, candidates: List[Tuple[str, Dict[str, Any] | None]]):
        """Try a list of (path, params) GETs, return first successful parsed JSON.

        Returns (ok, obj). ok=False if all attempts fail.
        """
        for path, params in candidates:
            status, body, _ = self._get(path, params)
            if status == 200 and body:
                try:
                    return True, json.loads(body.decode("utf-8"))
                except Exception:
                    # Not JSON, try next
                    pass
        return False, None

    def _get_json_first_ok_with_meta(self, candidates: List[Tuple[str, Dict[str, Any] | None]]):
        last_meta = None
        for path, params in candidates:
            url = self._make_url(path, params)
            status, body, hdrs = self._get(path, params)
            meta = {"status": status, "headers": hdrs, "url": url}
            if status == 200 and body:
                try:
                    return True, json.loads(body.decode("utf-8")), meta
                except Exception:
                    pass
            last_meta = meta
        return False, None, last_meta

    # endpoint management
    def _default_endpoints(self) -> Dict[str, List[Tuple[str, Optional[Dict[str, Any]]]]]:
        return {}

    def _endpoints(self) -> Dict[str, List[Tuple[str, Optional[Dict[str, Any]]]]]:
        eps = dict(self._default_endpoints())
        # Merge overrides for specific actions
        for k, v in (self._override_endpoints or {}).items():
            if isinstance(v, list):
                eps[k] = list(v)
        return eps

    def _format_candidates(self, action: str, item_id: Optional[str] = None, query: Optional[str] = None, page: Optional[int] = None, page_size: Optional[int] = None) -> List[Tuple[str, Optional[Dict[str, Any]]]]:
        eps = self._endpoints().get(action, [])
        out: List[Tuple[str, Optional[Dict[str, Any]]]] = []
        iid = urllib.parse.quote(str(item_id)) if item_id is not None else None
        q = query if query is not None else None
        p = int(page) if page is not None else None
        ps = int(page_size) if page_size is not None else None
        offset = None
        if p is not None and ps is not None:
            offset = max(0, (p - 1) * ps)
        for path_t, params_t in eps:
            path = path_t.replace('{id}', iid or '').replace('{q}', urllib.parse.quote(q or ''))
            params = None
            if isinstance(params_t, dict):
                params = {}
                for k, v in params_t.items():
                    if isinstance(v, str):
                        vv = v.replace('{id}', item_id or '').replace('{q}', q or '')
                        if '{page}' in vv and p is not None:
                            vv = vv.replace('{page}', str(p))
                        if '{page_size}' in vv and ps is not None:
                            vv = vv.replace('{page_size}', str(ps))
                        if '{limit}' in vv and ps is not None:
                            vv = vv.replace('{limit}', str(ps))
                        if '{offset}' in vv and offset is not None:
                            vv = vv.replace('{offset}', str(offset))
                    else:
                        vv = v
                    params[k] = vv
            out.append((path, params))
        return out


class SpoolmanClient(SpoolClientBase):
    SOURCE = "spoolman"
    """Minimal Spoolman client (read/search).

    Endpoints vary slightly across versions; we heuristically try a few:
    - Read:   /api/spools/{id}, /api/spool/{id}, /api/spools?id={id}
    - Search: /api/spools?search=QUERY, /api/spools?q=QUERY, /api/spool?search=QUERY
    """

    def _default_endpoints(self) -> Dict[str, List[Tuple[str, Optional[Dict[str, Any]]]]]:
        return {
            'read': [
                ('/api/spools/{id}', None),
                ('/api/spool/{id}', None),
                ('/api/spools', {'id': '{id}'}),
            ],
            'search': [
                ('/api/spools', {'search': '{q}', 'page': '{page}', 'page_size': '{page_size}'}),
                ('/api/spools', {'q': '{q}', 'limit': '{page_size}', 'offset': '{offset}'}),
                ('/api/spool', {'search': '{q}', 'page': '{page}', 'page_size': '{page_size}'}),
            ],
            'create': [
                ('/api/spools', None),
            ],
            'update': [
                ('/api/spools/{id}', None),
                ('/api/spool/{id}', None),
            ],
            'delete': [
                ('/api/spools/{id}', None),
                ('/api/spool/{id}', None),
            ],
        }

    def read(self, item_id: str) -> Dict[str, Any]:
        if not item_id:
            raise ValueError("item_id is required")
        ok, obj = self._get_json_first_ok(self._format_candidates('read', item_id=item_id))
        if not ok:
            raise SpoolClientError("Spoolman read failed (no known endpoint responded)")
        # Some variants return a list for id filter
        if isinstance(obj, list):
            return obj[0] if obj else {}
        if isinstance(obj, dict):
            return obj
        return {}

    def search(self, query: str, page: Optional[int] = None, page_size: Optional[int] = None) -> List[Dict[str, Any]]:
        q = (query or "").strip()
        ok, obj = self._get_json_first_ok(self._format_candidates('search', query=q, page=page, page_size=page_size))
        if not ok:
            raise SpoolClientError("Spoolman search failed (no known endpoint responded)")
        return list(obj or []) if isinstance(obj, list) else [obj] if isinstance(obj, dict) else []

    def search_normalized(self, query: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        q = (query or "").strip()
        ok, obj, meta = self._get_json_first_ok_with_meta(self._format_candidates('search', query=q, page=page, page_size=page_size))
        if not ok:
            raise SpoolClientError("Spoolman search failed (no known endpoint responded)", details=meta)
        items = list(obj or []) if isinstance(obj, list) else [obj] if isinstance(obj, dict) else []
        total = None
        headers = (meta or {}).get('headers') or {}
        for k in ('x-total-count', 'x-total', 'x_count'):
            if k in headers:
                try:
                    total = int(headers[k])
                except Exception:
                    pass
        if total is None and isinstance(obj, dict):
            for k in ('total', 'count', 'total_count'):
                if k in obj and isinstance(obj[k], int):
                    total = obj[k]
                    break
        return {
            'source': 'spoolman',
            'query': q,
            'page': page,
            'page_size': page_size,
            'items': items,
            'count': len(items),
            'total': total,
        }

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        for path, params in self._format_candidates('create'):
            status, body, _ = self._request(path, method="POST", params=params, payload=payload)
            if status in (200, 201) and body:
                try:
                    return json.loads(body.decode('utf-8'))
                except Exception:
                    pass
        raise SpoolClientError("Spoolman create failed (no known endpoint responded)")

    def update(self, item_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        for path, params in self._format_candidates('update', item_id=item_id):
            status, body, _ = self._request(path, method="PUT", params=params, payload=payload)
            if status in (200, 201) and body:
                try:
                    return json.loads(body.decode('utf-8'))
                except Exception:
                    pass
        raise SpoolClientError("Spoolman update failed (no known endpoint responded)")

    def delete(self, item_id: str) -> bool:
        for path, params in self._format_candidates('delete', item_id=item_id):
            status, _, _ = self._request(path, method="DELETE", params=params)
            if status in (200, 202, 204):
                return True
        return False


class TigerTagClient(SpoolClientBase):
    SOURCE = "tigertag"
    """Minimal TigerTag client (read/search).

    Public docs vary; try common REST styles:
    - Read:   /api/spools/{id}, /spools/{id}, /api/items/{id}
    - Search: /api/spools?search=QUERY, /api/spools?q=QUERY, /api/items?search=QUERY
    """

    def _default_endpoints(self) -> Dict[str, List[Tuple[str, Optional[Dict[str, Any]]]]]:
        return {
            'read': [
                ('/api/spools/{id}', None),
                ('/spools/{id}', None),
                ('/api/items/{id}', None),
            ],
            'search': [
                ('/api/spools', {'search': '{q}', 'page': '{page}', 'page_size': '{page_size}'}),
                ('/api/spools', {'q': '{q}', 'limit': '{page_size}', 'offset': '{offset}'}),
                ('/api/items', {'search': '{q}', 'page': '{page}', 'page_size': '{page_size}'}),
            ],
            'create': [
                ('/api/spools', None),
                ('/api/items', None),
            ],
            'update': [
                ('/api/spools/{id}', None),
                ('/api/items/{id}', None),
            ],
            'delete': [
                ('/api/spools/{id}', None),
                ('/api/items/{id}', None),
            ],
        }

    def read(self, item_id: str) -> Dict[str, Any]:
        if not item_id:
            raise ValueError("item_id is required")
        ok, obj = self._get_json_first_ok(self._format_candidates('read', item_id=item_id))
        if not ok:
            raise SpoolClientError("TigerTag read failed (no known endpoint responded)")
        if isinstance(obj, list):
            return obj[0] if obj else {}
        if isinstance(obj, dict):
            return obj
        return {}

    def search(self, query: str, page: Optional[int] = None, page_size: Optional[int] = None) -> List[Dict[str, Any]]:
        q = (query or "").strip()
        ok, obj = self._get_json_first_ok(self._format_candidates('search', query=q, page=page, page_size=page_size))
        if not ok:
            raise SpoolClientError("TigerTag search failed (no known endpoint responded)")
        return list(obj or []) if isinstance(obj, list) else [obj] if isinstance(obj, dict) else []

    def search_normalized(self, query: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        q = (query or "").strip()
        ok, obj, meta = self._get_json_first_ok_with_meta(self._format_candidates('search', query=q, page=page, page_size=page_size))
        if not ok:
            raise SpoolClientError("TigerTag search failed (no known endpoint responded)", details=meta)
        items = list(obj or []) if isinstance(obj, list) else [obj] if isinstance(obj, dict) else []
        total = None
        headers = (meta or {}).get('headers') or {}
        for k in ('x-total-count', 'x-total', 'x_count'):
            if k in headers:
                try:
                    total = int(headers[k])
                except Exception:
                    pass
        if total is None and isinstance(obj, dict):
            for k in ('total', 'count', 'total_count'):
                if k in obj and isinstance(obj[k], int):
                    total = obj[k]
                    break
        return {
            'source': 'tigertag',
            'query': q,
            'page': page,
            'page_size': page_size,
            'items': items,
            'count': len(items),
            'total': total,
        }

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        for path, params in self._format_candidates('create'):
            status, body, _ = self._request(path, method="POST", params=params, payload=payload)
            if status in (200, 201) and body:
                try:
                    return json.loads(body.decode('utf-8'))
                except Exception:
                    pass
        raise SpoolClientError("TigerTag create failed (no known endpoint responded)")

    def update(self, item_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        for path, params in self._format_candidates('update', item_id=item_id):
            status, body, _ = self._request(path, method="PUT", params=params, payload=payload)
            if status in (200, 201) and body:
                try:
                    return json.loads(body.decode('utf-8'))
                except Exception:
                    pass
        raise SpoolClientError("TigerTag update failed (no known endpoint responded)")

    def delete(self, item_id: str) -> bool:
        for path, params in self._format_candidates('delete', item_id=item_id):
            status, _, _ = self._request(path, method="DELETE", params=params)
            if status in (200, 202, 204):
                return True
        return False


class OpenSpoolClient(SpoolClientBase):
    SOURCE = "openspool"
    """Minimal OpenSpool/OpenTag3D client (read/search).

    Try generic REST patterns:
    - Read:   /api/spools/{id}, /spools/{id}, /api/filament/{id}
    - Search: /api/spools?search=QUERY, /api/filament?search=QUERY, /spools?q=QUERY
    """

    def _default_endpoints(self) -> Dict[str, List[Tuple[str, Optional[Dict[str, Any]]]]]:
        return {
            'read': [
                ('/api/spools/{id}', None),
                ('/spools/{id}', None),
                ('/api/filament/{id}', None),
            ],
            'search': [
                ('/api/spools', {'search': '{q}', 'page': '{page}', 'page_size': '{page_size}'}),
                ('/api/filament', {'search': '{q}', 'limit': '{page_size}', 'offset': '{offset}'}),
                ('/spools', {'q': '{q}', 'page': '{page}', 'page_size': '{page_size}'}),
            ],
            'create': [
                ('/api/spools', None),
                ('/api/filament', None),
            ],
            'update': [
                ('/api/spools/{id}', None),
                ('/api/filament/{id}', None),
            ],
            'delete': [
                ('/api/spools/{id}', None),
                ('/api/filament/{id}', None),
            ],
        }

    def read(self, item_id: str) -> Dict[str, Any]:
        if not item_id:
            raise ValueError("item_id is required")
        ok, obj = self._get_json_first_ok(self._format_candidates('read', item_id=item_id))
        if not ok:
            raise SpoolClientError("OpenSpool read failed (no known endpoint responded)")
        if isinstance(obj, list):
            return obj[0] if obj else {}
        if isinstance(obj, dict):
            return obj
        return {}

    def search(self, query: str, page: Optional[int] = None, page_size: Optional[int] = None) -> List[Dict[str, Any]]:
        q = (query or "").strip()
        ok, obj = self._get_json_first_ok(self._format_candidates('search', query=q, page=page, page_size=page_size))
        if not ok:
            raise SpoolClientError("OpenSpool search failed (no known endpoint responded)")
        return list(obj or []) if isinstance(obj, list) else [obj] if isinstance(obj, dict) else []

    def search_normalized(self, query: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        q = (query or "").strip()
        ok, obj, meta = self._get_json_first_ok_with_meta(self._format_candidates('search', query=q, page=page, page_size=page_size))
        if not ok:
            raise SpoolClientError("OpenSpool search failed (no known endpoint responded)", details=meta)
        items = list(obj or []) if isinstance(obj, list) else [obj] if isinstance(obj, dict) else []
        total = None
        headers = (meta or {}).get('headers') or {}
        for k in ('x-total-count', 'x-total', 'x_count'):
            if k in headers:
                try:
                    total = int(headers[k])
                except Exception:
                    pass
        if total is None and isinstance(obj, dict):
            for k in ('total', 'count', 'total_count'):
                if k in obj and isinstance(obj[k], int):
                    total = obj[k]
                    break
        return {
            'source': 'openspool',
            'query': q,
            'page': page,
            'page_size': page_size,
            'items': items,
            'count': len(items),
            'total': total,
        }

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        for path, params in self._format_candidates('create'):
            status, body, _ = self._request(path, method="POST", params=params, payload=payload)
            if status in (200, 201) and body:
                try:
                    return json.loads(body.decode('utf-8'))
                except Exception:
                    pass
        raise SpoolClientError("OpenSpool create failed (no known endpoint responded)")

    def update(self, item_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        for path, params in self._format_candidates('update', item_id=item_id):
            status, body, _ = self._request(path, method="PUT", params=params, payload=payload)
            if status in (200, 201) and body:
                try:
                    return json.loads(body.decode('utf-8'))
                except Exception:
                    pass
        raise SpoolClientError("OpenSpool update failed (no known endpoint responded)")

    def delete(self, item_id: str) -> bool:
        for path, params in self._format_candidates('delete', item_id=item_id):
            status, _, _ = self._request(path, method="DELETE", params=params)
            if status in (200, 202, 204):
                return True
        return False

    # ---- normalized wrappers ------------------------------------------------
    def _envelope(self, action: str, *, item_id: Optional[str] = None, item: Optional[Dict[str, Any]] = None, ok: Optional[bool] = None) -> Dict[str, Any]:
        out: Dict[str, Any] = {"source": getattr(self, 'SOURCE', 'unknown'), "action": action}
        if item_id is not None:
            out["id"] = str(item_id)
        if item is not None:
            out["item"] = item
        if ok is not None:
            out["ok"] = bool(ok)
        return out

    def create_normalized(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._envelope("create", item=self.create(payload))

    def read_normalized(self, item_id: str) -> Dict[str, Any]:
        return self._envelope("read", item_id=item_id, item=self.read(item_id))

    def update_normalized(self, item_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._envelope("update", item_id=item_id, item=self.update(item_id, payload))

    def delete_normalized(self, item_id: str) -> Dict[str, Any]:
        return self._envelope("delete", item_id=item_id, ok=self.delete(item_id))


def get_client(source: str, base_url: str, api_key: Optional[str] = None, endpoints: Optional[Dict[str, Any]] = None) -> SpoolClientBase:
    s = source.lower()
    # Optional endpoint overrides: parameter takes precedence, then env var OPK_SPOOL_ENDPOINTS (JSON)
    overrides = endpoints
    if overrides is None:
        eps_map: Dict[str, Any] = {}
        env = os.environ.get('OPK_SPOOL_ENDPOINTS')
        if env:
            try:
                eps_map = json.loads(env)
            except Exception:
                eps_map = {}
        if isinstance(eps_map, dict):
            overrides = eps_map.get(s)
    if s == 'spoolman':
        return SpoolmanClient(base_url, api_key, endpoints=overrides)
    if s == 'tigertag':
        return TigerTagClient(base_url, api_key, endpoints=overrides)
    if s in ('openspool','opentag3d'):
        return OpenSpoolClient(base_url, api_key, endpoints=overrides)
    raise ValueError(f"Unknown source: {source}")
