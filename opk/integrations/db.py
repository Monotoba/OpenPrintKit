from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Dict, Any, Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS openprinttag (
  id TEXT PRIMARY KEY,
  version TEXT,
  url TEXT,
  manufacturer TEXT,
  model TEXT,
  serial TEXT,
  notes TEXT
);
CREATE TABLE IF NOT EXISTS openprinttag_data (
  tag_id TEXT,
  key TEXT,
  value TEXT,
  PRIMARY KEY (tag_id, key),
  FOREIGN KEY (tag_id) REFERENCES openprinttag(id) ON DELETE CASCADE
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.executescript(SCHEMA)
    return con


def save_tag(con: sqlite3.Connection, tag: Dict[str, Any]) -> None:
    tid = tag.get('id') or tag.get('serial') or tag.get('model')
    if not tid:
        raise ValueError("OpenPrintTag requires an 'id' (or serial/model) to save")
    con.execute("REPLACE INTO openprinttag(id,version,url,manufacturer,model,serial,notes) VALUES (?,?,?,?,?,?,?)",
                (tag.get('id'), tag.get('version'), tag.get('url'), tag.get('manufacturer'), tag.get('model'), tag.get('serial'), tag.get('notes')))
    con.execute("DELETE FROM openprinttag_data WHERE tag_id = ?", (tag.get('id'),))
    for k, v in (tag.get('data') or {}).items():
        con.execute("REPLACE INTO openprinttag_data(tag_id,key,value) VALUES (?,?,?)", (tag.get('id'), k, str(v)))
    con.commit()


def load_tag(con: sqlite3.Connection, tag_id: str) -> Dict[str, Any] | None:
    cur = con.execute("SELECT id,version,url,manufacturer,model,serial,notes FROM openprinttag WHERE id=?", (tag_id,))
    row = cur.fetchone()
    if not row:
        return None
    keys = ['id','version','url','manufacturer','model','serial','notes']
    tag = {k: row[i] for i, k in enumerate(keys) if row[i] is not None}
    data = {}
    for k, v in con.execute("SELECT key,value FROM openprinttag_data WHERE tag_id=?", (tag_id,)):
        data[k] = v
    if data:
        tag['data'] = data
    return tag


def search_tags(con: sqlite3.Connection, query: str) -> Iterable[Dict[str, Any]]:
    q = f"%{query}%"
    for row in con.execute("SELECT id,manufacturer,model,serial FROM openprinttag WHERE id LIKE ? OR manufacturer LIKE ? OR model LIKE ? OR serial LIKE ?",
                           (q, q, q, q)):
        yield {'id': row[0], 'manufacturer': row[1], 'model': row[2], 'serial': row[3]}

