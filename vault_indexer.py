# IMPROVEMENT: FTS5 SQLite index replaces synchronous os.walk search
import os
import sqlite3
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from paths import scandir_walk

INDEX_DB = Path.home() / ".eleviewer" / "vault_index.db"


def init_fts_index():
    INDEX_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(INDEX_DB)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS files USING fts5(
            path,
            filename,
            content,
            tokenize='unicode61'
        )
    """)
    conn.commit()
    return conn


class VaultIndexWorker(QThread):
    progress = Signal(int)  # number of files indexed
    finished = Signal()

    def __init__(self, vault_paths: list):
        super().__init__()
        self.vault_paths = vault_paths
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            conn = init_fts_index()
            conn.execute("DELETE FROM files")  # full re-index
            count = 0
            TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".html"}
            for vault in self.vault_paths:
                if self._is_cancelled:
                    break
                try:
                    vault_resolved = Path(vault).resolve()
                except Exception:
                    continue
                for root, dirs, files in scandir_walk(str(vault_resolved), followlinks=False):
                    if self._is_cancelled:
                        break
                    abs_root = os.path.abspath(root)
                    if not abs_root.startswith(str(vault_resolved)):
                        dirs.clear()
                        continue

                    for fname in files:
                        if self._is_cancelled:
                            break
                        if fname.startswith("."):
                            continue

                        fpath = Path(root) / fname
                        content = ""
                        if fpath.suffix.lower() in TEXT_EXTENSIONS:
                            try:
                                content = fpath.read_text(encoding="utf-8", errors="replace")[:10000]
                            except OSError:
                                pass
                        try:
                            conn.execute(
                                "INSERT INTO files(path, filename, content) VALUES (?, ?, ?)",
                                (str(fpath), fname, content)
                            )
                            count += 1
                            if count % 100 == 0:
                                conn.commit()
                                self.progress.emit(count)
                        except Exception:
                            pass
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[FTS Indexer] Error during indexing: {e}")
        self.finished.emit()


def search_fts(query: str) -> list[tuple[str, str]]:
    """Return list of (filename, full_path) matching query."""
    if not INDEX_DB.exists():
        return []
    try:
        conn = sqlite3.connect(INDEX_DB)
        cursor = conn.execute(
            "SELECT filename, path FROM files WHERE files MATCH ? ORDER BY rank LIMIT 200",
            (query,)
        )
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"[FTS Search] Search error: {e}")
        return []
