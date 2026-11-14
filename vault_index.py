"""Persistent, local-only filename index for connected study folders."""

import os
import sqlite3
from pathlib import Path

from paths import APP_DATA_DIR

VAULT_INDEX_PATH = APP_DATA_DIR / "vault_index.sqlite3"


class VaultIndex:
    """SQLite index that incrementally refreshes vault file metadata."""

    def __init__(self, database_path=VAULT_INDEX_PATH):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.database_path))
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                vault TEXT NOT NULL,
                full_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                relative_dir TEXT NOT NULL,
                modified_ns INTEGER NOT NULL,
                size INTEGER NOT NULL,
                PRIMARY KEY (vault, full_path)
            )
            """
        )
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_files_name ON files(file_name COLLATE NOCASE)"
        )
        self.connection.commit()

    def close(self):
        self.connection.close()

    def refresh_vault(self, vault_path, is_cancelled=None):
        """Refresh one vault and remove files that no longer exist."""
        vault = Path(vault_path).resolve()
        if not vault.is_dir():
            return

        seen = set()
        for root, dirs, files in os.walk(str(vault), followlinks=False):
            if is_cancelled and is_cancelled():
                break
            dirs[:] = [name for name in dirs if not name.startswith(".")]
            root_path = Path(root).resolve()
            try:
                if os.path.commonpath((str(vault), str(root_path))) != str(vault):
                    dirs.clear()
                    continue
            except ValueError:
                dirs.clear()
                continue

            for file_name in files:
                if is_cancelled and is_cancelled():
                    break
                if file_name.startswith("."):
                    continue
                full_path = (root_path / file_name).resolve()
                try:
                    if os.path.commonpath((str(vault), str(full_path))) != str(vault):
                        continue
                    stat = full_path.stat()
                except (OSError, ValueError):
                    continue
                relative_dir = os.path.relpath(str(root_path), str(vault))
                if relative_dir == ".":
                    relative_dir = ""
                normalized_path = str(full_path)
                seen.add(normalized_path)
                self.connection.execute(
                    """
                    INSERT INTO files
                        (vault, full_path, file_name, relative_dir, modified_ns, size)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(vault, full_path) DO UPDATE SET
                        file_name=excluded.file_name,
                        relative_dir=excluded.relative_dir,
                        modified_ns=excluded.modified_ns,
                        size=excluded.size
                    """,
                    (
                        str(vault),
                        normalized_path,
                        file_name,
                        relative_dir,
                        stat.st_mtime_ns,
                        stat.st_size,
                    ),
                )

        if not (is_cancelled and is_cancelled()):
            existing = self.connection.execute(
                "SELECT full_path FROM files WHERE vault = ?", (str(vault),)
            ).fetchall()
            stale = [(path,) for (path,) in existing if path not in seen]
            if stale:
                self.connection.executemany(
                    "DELETE FROM files WHERE vault = ? AND full_path = ?",
                    [(str(vault), path) for (path,) in stale],
                )
        self.connection.commit()

    def search(self, vault_paths, query, limit=100):
        if not query:
            return []
        resolved_vaults = [str(Path(path).resolve()) for path in vault_paths if path]
        if not resolved_vaults:
            return []
        pattern = f"%{query}%"
        placeholders = ",".join("?" for _ in resolved_vaults)
        rows = self.connection.execute(
            f"""
            SELECT file_name, relative_dir, vault, full_path
            FROM files
            WHERE vault IN ({placeholders}) AND file_name LIKE ? COLLATE NOCASE
            ORDER BY file_name COLLATE NOCASE, relative_dir COLLATE NOCASE
            LIMIT ?
            """,
            (*resolved_vaults, pattern, limit),
        ).fetchall()
        return rows
