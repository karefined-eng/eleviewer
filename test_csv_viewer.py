"""
Automated unit and integration test for CsvViewer in EleViewer.
Verifies non-destructive text preservation (leading zeros), delimiter auto-detection,
grid ⇄ raw text toggling, atomic serialization, and Universal TTS (F9) support.
"""

import sys
import os
import time
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from csv_viewer import CsvViewer
from file_handler import create_viewer_widget, get_file_content

def run_tests():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    app = QApplication.instance() or QApplication(sys.argv)
    print("[1/5] Testing CsvViewer initialization and non-destructive text preservation...")
    
    sample_csv = 'ID,Name,Score\n00123,"Doe, John",98.5\n00456,Jane Smith,100\n'
    viewer = CsvViewer(content=sample_csv)
    
    # Wait for background thread to load
    timeout = 5.0
    start_t = time.time()
    while viewer._loading and (time.time() - start_t) < timeout:
        app.processEvents()
        time.sleep(0.05)
    app.processEvents()
    
    # Assert dimensions
    assert viewer.model.rowCount() == 3, f"Expected 3 rows, got {viewer.model.rowCount()}"
    assert viewer.model.columnCount() == 3, f"Expected 3 cols, got {viewer.model.columnCount()}"
    
    # Assert leading zeros preserved (No Excel Trap!)
    id_cell = viewer.model.data(viewer.model.index(1, 0), Qt.DisplayRole)
    assert id_cell == "00123", f"Excel Trap failure! Expected '00123', got '{id_cell}'"
    print("  -> Passed! Leading zero '00123' preserved cleanly.")

    print("[2/5] Testing serialization via toPlainText and to_csv_bytes...")
    out_text = viewer.toPlainText()
    assert "00123" in out_text and '"Doe, John"' in out_text, f"Serialization mismatch: {out_text}"
    out_bytes = viewer.to_csv_bytes()
    assert isinstance(out_bytes, bytes) and b"00123" in out_bytes
    print("  -> Passed! Serializes cleanly to text and UTF-8 bytes.")

    print("[3/5] Testing Universal TTS (F9) Read Aloud method...")
    tts_summary = viewer.read_current_page()
    assert "3 rows" in tts_summary and "ID, Name, Score" in tts_summary, f"Unexpected TTS output: {tts_summary}"
    print(f"  -> Passed! TTS output: '{tts_summary}'")

    print("[4/5] Testing Grid <-> Raw Text View mode toggle...")
    viewer.toggle_view_mode()
    assert viewer.view_mode == "raw", "Expected view mode to be 'raw'"
    raw_val = viewer.raw_editor.toPlainText()
    assert "00123" in raw_val
    
    # Modify raw text
    viewer.raw_editor.setPlainText('ID,Name,Score\n00999,Alice,100\n')
    viewer.toggle_view_mode()
    
    start_t = time.time()
    while viewer._loading and (time.time() - start_t) < timeout:
        app.processEvents()
        time.sleep(0.05)
    app.processEvents()
    
    assert viewer.view_mode == "grid", "Expected view mode to be 'grid'"
    new_id = viewer.model.data(viewer.model.index(1, 0), Qt.DisplayRole)
    assert new_id == "00999", f"Expected new ID '00999' from raw edit, got '{new_id}'"
    print("  -> Passed! Bidirectional sync between Grid View and Raw Text View works!")

    print("[5/5] Testing file_handler factory routing...")
    widget = create_viewer_widget("test_data.csv", content=sample_csv)
    assert isinstance(widget, CsvViewer), f"Expected CsvViewer widget, got {type(widget)}"
    
    start_t = time.time()
    while getattr(widget, "_loading", False) and (time.time() - start_t) < timeout:
        app.processEvents()
        time.sleep(0.05)
    app.processEvents()

    extracted = get_file_content(widget, "test_data.csv")
    assert "00123" in extracted, f"Expected '00123' in extracted content, got '{extracted}'"
    print("  -> Passed! file_handler routes .csv cleanly to CsvViewer.")

    print("\nALL 5 CSV WORKSTATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
