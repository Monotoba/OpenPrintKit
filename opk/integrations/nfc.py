from __future__ import annotations
from typing import Dict, Any


def nfc_available() -> bool:
    try:
        import nfc  # type: ignore
        return True
    except Exception:
        return False


def read_tag(timeout: float = 5.0) -> Dict[str, Any]:
    """Read OpenPrintTag payload from an NFC tag (if supported).
    Returns a dict payload. Raises RuntimeError on failure or if dependency missing.
    """
    try:
        import nfc  # type: ignore
    except Exception as e:
        raise RuntimeError("nfcpy not available; install 'nfcpy' to use NFC features") from e

    # Minimal nfcpy polling example; expects NDEF record with JSON text
    payload: Dict[str, Any] = {}
    def on_connect(tag):
        try:
            if hasattr(tag, 'ndef') and tag.ndef:
                for rec in tag.ndef.records:
                    if getattr(rec, 'type', b'').endswith(b'text') or rec.type == 'urn:nfc:wkt:T':
                        try:
                            txt = rec.text
                        except Exception:
                            txt = rec.data.decode('utf-8', errors='ignore')
                        import json
                        try:
                            data = json.loads(txt)
                            if isinstance(data, dict):
                                payload.update(data)
                        except Exception:
                            pass
            return False
        except Exception:
            return False

    try:
        clf = nfc.ContactlessFrontend('usb')
    except Exception as e:
        raise RuntimeError(f"Failed to open NFC device: {e}")
    try:
        clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: False)
    finally:
        try:
            clf.close()
        except Exception:
            pass
    return payload


def write_tag(data: Dict[str, Any]) -> None:
    """Write OpenPrintTag payload to NFC tag as a text NDEF record with JSON."""
    try:
        import nfc  # type: ignore
        import ndef  # type: ignore
    except Exception as e:
        raise RuntimeError("nfcpy/ndef not available; install 'nfcpy' to use NFC features") from e

    import json
    text = json.dumps(data, ensure_ascii=False)

    def on_connect(tag):
        try:
            if tag.ndef is None:
                tag.format()
            records = [ndef.TextRecord(text)]
            tag.ndef.records = records
            return False
        except Exception:
            return False

    clf = nfc.ContactlessFrontend('usb')
    try:
        clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: False)
    finally:
        try:
            clf.close()
        except Exception:
            pass

