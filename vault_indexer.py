"""SQLite FTS5 vault indexer with optional Rust acceleration via eleviewer_native."""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from paths import VAULT_INDEX_DB_PATH

try:
    import eleviewer_native as _native
    NATIVE_AVAILABLE = True
except ImportError:
    _native = None
    NATIVE_AVAILABLE = False

INDEX_EXTENSIONS = {".md", ".txt", ".csv"}
MAX_CONTENT_BYTES = 2_000_000

_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS document_index USING fts5(
    filename,
    content,
    path UNINDEXED,
    vault UNINDEXED,
    tokenize='porter unicode61'
);
CREATE TABLE IF NOT EXISTS file_meta (
    path TEXT PRIMARY KEY,
    vault TEXT NOT NULL,
    mtime REAL NOT NULL
);
"""


def _fts_query(raw: str) -> str:
    tokens = re.findall(r"\w+", raw.lower())
    if not tokens:
        return ""
    return " AND ".join(f'"{t.replace(chr(34), chr(34) * 2)}"*' for t in tokens)


def _init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(_SCHEMA)


def _vault_name(vault_path: str) -> str:
    try:
        return Path(vault_path).resolve().name or vault_path
    except OSError:
        return Path(vault_path).name or vault_path


def _read_text_content(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    if len(data) > MAX_CONTENT_BYTES:
        data = data[:MAX_CONTENT_BYTES]
    return data.decode("utf-8", errors="replace")


def _extract_text(path: Path) -> str:
    if path.suffix.lower() not in INDEX_EXTENSIONS:
        return ""
    return _read_text_content(path)


def _index_vault_python(db_path: Path, vault_path: str) -> int:
    vault_root = Path(vault_path).resolve()
    if not vault_root.is_dir():
        return 0

    vault_str = str(vault_root)
    vault_name = vault_root.name
    conn = sqlite3.connect(db_path)
    try:
        _init_db(conn)
        conn.execute("DELETE FROM document_index WHERE vault = ?", (vault_name,))
        conn.execute("DELETE FROM file_meta WHERE vault = ?", (vault_name,))

        count = 0
        for root, dirs, files in os.walk(vault_str, followlinks=False):
            abs_root = os.path.abspath(root)
            if not abs_root.startswith(vault_str):
                dirs.clear()
                continue
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for name in files:
                if name.startswith("."):
                    continue
                full_path = Path(root) / name
                try:
                    abs_full = str(full_path.resolve())
                except OSError:
                    continue
                if not abs_full.startswith(vault_str):
                    continue
                if full_path.suffix.lower() not in INDEX_EXTENSIONS:
                    continue

                try:
                    mtime = full_path.stat().st_mtime
                except OSError:
                    continue

                content = _extract_text(full_path)
                conn.execute(
                    "INSERT INTO document_index (filename, content, path, vault) VALUES (?, ?, ?, ?)",
                    (name, content, abs_full, vault_name),
                )
                conn.execute(
                    "INSERT INTO file_meta (path, vault, mtime) VALUES (?, ?, ?)",
                    (abs_full, vault_name, mtime),
                )
                count += 1
        conn.commit()
        return count
    finally:
        conn.close()


def index_vault(vault_path: str, db_path: Path | None = None) -> int:
    db = db_path or VAULT_INDEX_DB_PATH
    db.parent.mkdir(parents=True, exist_ok=True)
    if NATIVE_AVAILABLE:
        return _native.index_vault(str(db), vault_path)
    return _index_vault_python(db, vault_path)


def search_index(
    vaults: list[str],
    query: str,
    limit: int = 100,
    db_path: Path | None = None,
) -> list[tuple[str, str, str, str, str]]:
    """Return (filename, display_dir, vault_name, full_path, snippet) tuples."""
    fts = _fts_query(query)
    if not fts:
        return []

    db = db_path or VAULT_INDEX_DB_PATH
    if not db.exists():
        return []

    if NATIVE_AVAILABLE:
        rows = _native.search_documents(str(db), query, vaults, limit)
        return [tuple(row) for row in rows]

    vault_names = {_vault_name(v) for v in vaults if v}
    conn = sqlite3.connect(db)
    try:
        _init_db(conn)
        cur = conn.execute(
            """
            SELECT path, vault, filename,
                   snippet(document_index, 1, '«', '»', '...', 15) AS snip,
                   bm25(document_index) AS rank
            FROM document_index
            WHERE document_index MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts, limit * 4),
        )
        results: list[tuple[str, str, str, str, str]] = []
        for full_path, vault_name, filename, snippet, _rank in cur.fetchall():
            if vault_names and vault_name not in vault_names:
                continue
            display_dir = ""
            for vault in vaults:
                try:
                    root = Path(vault).resolve()
                    rel = Path(full_path).parent.relative_to(root)
                    if str(rel) != ".":
                        display_dir = f" ({rel})"
                    break
                except (OSError, ValueError):
                    continue
            results.append((filename, display_dir, vault_name, full_path, snippet or ""))
            if len(results) >= limit:
                break
        return results
    finally:
        conn.close()


class VaultIndexWorker(QThread):
    vault_indexed = Signal(str, int)

    def __init__(self, vault_paths: list[str], parent=None):
        super().__init__(parent)
        self._vault_paths = [p for p in vault_paths if p]
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        for vault_path in self._vault_paths:
            if self._cancelled:
                break
            try:
                count = index_vault(vault_path)
                if not self._cancelled:
                    self.vault_indexed.emit(vault_path, count)
            except Exception:
                if not self._cancelled:
                    self.vault_indexed.emit(vault_path, 0)


_active_worker: VaultIndexWorker | None = None


def stop_vault_indexer() -> None:
    """Stop active vault indexing background worker cleanly on exit."""
    global _active_worker
    if _active_worker and _active_worker.isRunning():
        _active_worker.cancel()
        _active_worker.terminate()
        _active_worker.wait()
        _active_worker = None


def schedule_vault_index(vault_paths: list[str]) -> None:
    """Start background indexing for one or more vault paths."""
    global _active_worker
    
    from settings import load_settings
    if not load_settings().get("vault_auto_index", True):
        return
        
    paths = [p for p in vault_paths if p and os.path.isdir(p)]
    if not paths:
        return

    if _active_worker and _active_worker.isRunning():
        _active_worker.cancel()
        _active_worker.terminate()
        _active_worker.wait()

    _active_worker = VaultIndexWorker(paths)
    _active_worker.start()

