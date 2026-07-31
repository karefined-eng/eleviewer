import os
import pytest
from pathlib import Path
from vault_search import VaultSearchWorker
from vault_indexer import index_vault, search_index

def test_vault_search_worker_finds_files_by_filename(tmp_path):
    vault = tmp_path / "my_vault"
    vault.mkdir()
    
    (vault / "test1.md").write_text("hello")
    (vault / "ignore.txt").write_text("world")
    
    hidden_dir = vault / ".hidden"
    hidden_dir.mkdir()
    (hidden_dir / "test2.md").write_text("hidden")
    
    sub_dir = vault / "sub"
    sub_dir.mkdir()
    (sub_dir / "test3.md").write_text("sub")
    
    results = []
    worker = VaultSearchWorker([str(vault)], "test")
    
    def on_result(filename, display_dir, vault_name, full_path, snippet):
        results.append(filename)
        
    worker.result_found.connect(on_result)
    worker.run()
    
    assert "test1.md" in results
    assert "test3.md" in results
    assert "test2.md" not in results
    assert "ignore.txt" not in results


def test_vault_search_worker_finds_content_via_fts5(tmp_path, monkeypatch):
    db_path = tmp_path / "vault_index.db"
    vault = tmp_path / "content_vault"
    vault.mkdir()
    (vault / "notes.md").write_text("quantum genetics lecture notes")

    monkeypatch.setattr("vault_indexer.VAULT_INDEX_DB_PATH", db_path)
    monkeypatch.setattr("paths.VAULT_INDEX_DB_PATH", db_path)

    index_vault(str(vault), db_path=db_path)

    hits = search_index([str(vault)], "genetics", db_path=db_path)
    assert hits
    assert any("notes.md" in row[0] for row in hits)

    results = []
    worker = VaultSearchWorker([str(vault)], "genetics")

    def on_result(filename, display_dir, vault_name, full_path, snippet):
        results.append(filename)

    worker.result_found.connect(on_result)
    worker.run()

    assert "notes.md" in results


def test_vault_search_worker_cancellation(tmp_path):
    vault = tmp_path / "vault2"
    vault.mkdir()
    for i in range(10):
        (vault / f"test{i}.md").write_text("test")
        
    worker = VaultSearchWorker([str(vault)], "test")
    worker.cancel()
    
    results = []
    worker.result_found.connect(lambda f, d, v, p, s: results.append(f))
    worker.run()
    
    assert len(results) == 0
