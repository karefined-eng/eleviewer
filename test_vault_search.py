import os
import pytest
from pathlib import Path
from vault_search import VaultSearchWorker

def test_vault_search_worker_finds_files(tmp_path):
    # Setup mock vault
    vault = tmp_path / "my_vault"
    vault.mkdir()
    
    (vault / "test1.md").write_text("hello")
    (vault / "ignore.txt").write_text("world")
    
    # Hidden folder
    hidden_dir = vault / ".hidden"
    hidden_dir.mkdir()
    (hidden_dir / "test2.md").write_text("hidden")
    
    # Subfolder
    sub_dir = vault / "sub"
    sub_dir.mkdir()
    (sub_dir / "test3.md").write_text("sub")
    
    # Run worker
    results = []
    worker = VaultSearchWorker([str(vault)], "test")
    
    def on_result(filename, display_dir, vault_name, full_path):
        results.append(filename)
        
    worker.result_found.connect(on_result)
    worker.run()  # Run synchronously for test
    
    assert "test1.md" in results
    assert "test3.md" in results
    assert "test2.md" not in results  # Should ignore hidden directories
    assert "ignore.txt" not in results # Does not match query

def test_vault_search_worker_cancellation(tmp_path):
    vault = tmp_path / "vault2"
    vault.mkdir()
    for i in range(10):
        (vault / f"test{i}.md").write_text("test")
        
    worker = VaultSearchWorker([str(vault)], "test")
    worker.cancel() # Cancel before running
    
    results = []
    worker.result_found.connect(lambda f, d, v, p: results.append(f))
    worker.run()
    
    assert len(results) == 0 # Should have aborted immediately
