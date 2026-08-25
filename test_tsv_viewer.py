"""
Minimal test to ensure .tsv files are routed to the CsvViewer and content round-trips.
"""

import sys
import time
from PySide6.QtWidgets import QApplication
from csv_viewer import CsvViewer
from file_handler import create_viewer_widget, get_file_content


def test_tsv_routing_and_round_trip():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    app = QApplication.instance() or QApplication(sys.argv)

    sample_tsv = 'ID\tName\tScore\n00123\tDoe, John\t98.5\n00456\tJane Smith\t100\n'

    # direct CsvViewer usage
    viewer = CsvViewer(content=sample_tsv, delimiter='\t')
    timeout = 3.0
    start = time.time()
    while getattr(viewer, '_loading', False) and (time.time() - start) < timeout:
        app.processEvents()
        time.sleep(0.05)

    assert viewer.model.rowCount() == 3, "TSV: expected 3 rows"

    # factory routing
    widget = create_viewer_widget('sample_data.tsv', content=sample_tsv)
    assert isinstance(widget, CsvViewer), f"Expected CsvViewer for .tsv, got {type(widget)}"

    start = time.time()
    while getattr(widget, '_loading', False) and (time.time() - start) < timeout:
        app.processEvents()
        time.sleep(0.05)

    extracted = get_file_content(widget, 'sample_data.tsv')
    assert '00123' in extracted, f"Expected '00123' in extracted TSV content, got: {extracted}"

    viewer.close()
    widget.close()
    app.processEvents()
    print('TSV routing and round-trip test passed!')
