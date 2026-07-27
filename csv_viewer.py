"""
High-performance CSV/TSV Table Viewer and Editor (CsvViewer) for EleViewer.
Features off-thread QThread parsing, interactive delimiter/quoting toolbar overrides,
dual Table Grid ⇄ Raw Text view modes, non-destructive text preservation, and Universal TTS.
"""

import csv
import io
import os
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QPushButton, QToolButton, QLabel, QStackedWidget,
    QMessageBox, QAbstractItemView, QFrame
)

from editor import EditorTab
from theme import (
    BRAND_PANEL, BRAND_PANEL_2, BRAND_PRIMARY, BRAND_BORDER,
    BRAND_BACKGROUND, BRAND_MUTED_FG, get_brand_accent,
    compact_toolbar_stylesheet
)


class CsvLoadWorker(QThread):
    """Off-thread CSV parser to prevent GUI freezes on large datasets."""
    loaded = Signal(list, str)  # (rows, detected_delimiter)
    error = Signal(str)

    def __init__(self, file_path=None, content=None, delimiter=None, quoting=csv.QUOTE_MINIMAL, encoding="utf-8"):
        super().__init__()
        self.file_path = file_path
        self.content = content
        self.delimiter = delimiter
        self.quoting = quoting
        self.encoding = encoding

    def run(self):
        try:
            raw_text = ""
            if self.content is not None:
                raw_text = self.content
            elif self.file_path and os.path.exists(self.file_path):
                try:
                    with open(self.file_path, "r", encoding=self.encoding) as f:
                        raw_text = f.read()
                except UnicodeDecodeError:
                    with open(self.file_path, "r", encoding="latin-1", errors="replace") as f:
                        raw_text = f.read()

            if not raw_text.strip():
                self.loaded.emit([[""]], ",")
                return

            detected_delim = self.delimiter
            if not detected_delim or detected_delim == "auto":
                try:
                    sample = raw_text[:4096]
                    sniffer = csv.Sniffer()
                    detected_delim = sniffer.sniff(sample, delimiters=",\t;|").delimiter
                except Exception:
                    detected_delim = "," if not self.file_path or not str(self.file_path).endswith(".tsv") else "\t"

            reader = csv.reader(
                io.StringIO(raw_text),
                delimiter=detected_delim,
                quoting=self.quoting
            )
            rows = []
            for row in reader:
                rows.append([str(cell) for cell in row])
            
            if not rows:
                rows = [[""]]

            self.loaded.emit(rows, detected_delim)
        except Exception as e:
            self.error.emit(str(e))


class CsvViewer(QWidget):
    """CSV/TSV Workstation Table Viewer & Raw Text Editor."""
    textChanged = Signal()

    def __init__(self, file_path=None, content=None):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        self._loading = False
        self.current_delimiter = "auto"
        self.current_quoting = csv.QUOTE_MINIMAL
        self.current_encoding = "utf-8"
        self.view_mode = "grid"  # 'grid' or 'raw'
        self.worker = None
        self._headers = []

        self._build_ui()

        if content is not None:
            self.load_from_content(content)
        elif file_path:
            self.load_from_path(file_path)
        else:
            self._populate_grid([["A", "B", "C"], ["", "", ""]])
            self.is_modified = False

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Toolbar ────────────────────────────────────────────────────────
        self.toolbar = QFrame()
        self.toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {BRAND_PANEL};
                border-bottom: 1px solid {BRAND_BORDER};
                padding: 4px 8px;
            }}
            QLabel {{ color: {BRAND_MUTED_FG}; font-size: 11px; font-weight: bold; }}
            QComboBox {{
                background-color: {BRAND_PANEL_2};
                color: {BRAND_PRIMARY};
                border: 1px solid {BRAND_BORDER};
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 12px;
                min-width: 90px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BRAND_PANEL};
                color: {BRAND_PRIMARY};
                border: 1px solid {BRAND_BORDER};
                selection-background-color: #6cb6ff;
                selection-color: #0c1826;
            }}
            QComboBox::drop-down {{ border: none; }}
            QPushButton {{
                background-color: {BRAND_PANEL_2};
                color: {BRAND_PRIMARY};
                border: 1px solid {BRAND_BORDER};
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background-color: {BRAND_BORDER}; }}
        """)
        tb_layout = QHBoxLayout(self.toolbar)
        tb_layout.setContentsMargins(4, 4, 4, 4)
        tb_layout.setSpacing(10)

        # Delimiter Selector
        tb_layout.addWidget(QLabel("DELIMITER"))
        self.combo_delim = QComboBox()
        self.combo_delim.addItem("Auto-detect", "auto")
        self.combo_delim.addItem("Comma (,)", ",")
        self.combo_delim.addItem("Semicolon (;)", ";")
        self.combo_delim.addItem("Tab (\\t)", "\t")
        self.combo_delim.addItem("Pipe (|)", "|")
        self.combo_delim.currentIndexChanged.connect(self._on_delimiter_changed)
        tb_layout.addWidget(self.combo_delim)

        # Quoting Selector
        tb_layout.addWidget(QLabel("QUOTING"))
        self.combo_quote = QComboBox()
        self.combo_quote.addItem("Standard", csv.QUOTE_MINIMAL)
        self.combo_quote.addItem("All Quotes", csv.QUOTE_ALL)
        self.combo_quote.addItem("None", csv.QUOTE_NONE)
        self.combo_quote.currentIndexChanged.connect(self._on_quoting_changed)
        tb_layout.addWidget(self.combo_quote)

        # Quick Actions
        self.btn_add_row = QPushButton("+ Row")
        self.btn_add_row.setToolTip("Insert new row at bottom")
        self.btn_add_row.clicked.connect(self.add_row)
        tb_layout.addWidget(self.btn_add_row)

        self.btn_add_col = QPushButton("+ Column")
        self.btn_add_col.setToolTip("Insert new column at right")
        self.btn_add_col.clicked.connect(self.add_column)
        tb_layout.addWidget(self.btn_add_col)

        self.btn_del = QPushButton("Delete Selected")
        self.btn_del.setToolTip("Delete selected rows or columns")
        self.btn_del.clicked.connect(self.delete_selected)
        tb_layout.addWidget(self.btn_del)

        tb_layout.addStretch()

        # View Switcher
        self.btn_toggle_view = QPushButton("📄 Raw Text")
        self.btn_toggle_view.setToolTip("Toggle between Table Grid View and Raw CSV Text View")
        self.btn_toggle_view.clicked.connect(self.toggle_view_mode)
        tb_layout.addWidget(self.btn_toggle_view)

        layout.addWidget(self.toolbar)

        # ── Stacked Views (Grid vs Raw Text) ──────────────────────────────
        self.stack = QStackedWidget()

        # 1. Grid View
        self.table = QTableWidget()
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BRAND_PANEL};
                color: {BRAND_PRIMARY};
                gridline-color: {BRAND_BORDER};
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }}
            QTableWidget::item {{ padding: 6px; }}
            QTableWidget::item:selected {{
                background-color: {get_brand_accent()};
                color: {BRAND_BACKGROUND};
            }}
            QHeaderView::section {{
                background-color: {BRAND_PANEL_2};
                color: {BRAND_MUTED_FG};
                padding: 6px;
                border: 1px solid {BRAND_BORDER};
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.itemChanged.connect(self._on_cell_changed)
        self.stack.addWidget(self.table)

        # 2. Raw Text View
        self.raw_editor = EditorTab()
        self.raw_editor.editor.textChanged.connect(self._on_raw_text_changed)
        self.stack.addWidget(self.raw_editor)

        layout.addWidget(self.stack)

    # ── Off-Thread Loading ────────────────────────────────────────────────
    def load_from_path(self, file_path):
        self._loading = True
        self.file_path = file_path
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        delim = self.combo_delim.currentData()
        quote = self.combo_quote.currentData()
        self.worker = CsvLoadWorker(file_path=file_path, delimiter=delim, quoting=quote)
        self.worker.loaded.connect(self._on_load_success)
        self.worker.error.connect(self._on_load_error)
        self.worker.start()

    def load_from_content(self, content):
        self._loading = True
        delim = self.combo_delim.currentData()
        quote = self.combo_quote.currentData()
        self.worker = CsvLoadWorker(content=content, delimiter=delim, quoting=quote)
        self.worker.loaded.connect(self._on_load_success)
        self.worker.error.connect(self._on_load_error)
        self.worker.start()

    def _on_load_success(self, rows, detected_delim):
        self._populate_grid(rows)
        # Update delimiter combo if auto-detected
        if self.combo_delim.currentData() == "auto":
            for i in range(self.combo_delim.count()):
                if self.combo_delim.itemData(i) == detected_delim:
                    self.combo_delim.blockSignals(True)
                    self.combo_delim.setCurrentIndex(i)
                    self.combo_delim.blockSignals(False)
                    break
        self._loading = False
        self.is_modified = False

    def _on_load_error(self, err_msg):
        self._loading = False
        QMessageBox.warning(self, "CSV Parse Warning", f"Could not parse CSV cleanly: {err_msg}\nDefaulting to Raw Text view.")
        self.view_mode = "raw"
        self.stack.setCurrentIndex(1)
        self.btn_toggle_view.setText("📊 Table Grid")
        if self.file_path and os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
                self.raw_editor.setPlainText(f.read())

    def _populate_grid(self, rows):
        self._loading = True
        self.table.blockSignals(True)
        self.table.clear()

        max_cols = max(len(row) for row in rows) if rows else 1
        num_rows = len(rows)

        self.table.setRowCount(num_rows)
        self.table.setColumnCount(max_cols)

        # Standard spreadsheet headers (A, B, C...)
        headers = [self._col_to_letter(c) for c in range(max_cols)]
        self.table.setHorizontalHeaderLabels(headers)
        self._headers = headers

        for r_idx, row in enumerate(rows):
            for c_idx in range(max_cols):
                val = row[c_idx] if c_idx < len(row) else ""
                item = QTableWidgetItem(str(val))
                self.table.setItem(r_idx, c_idx, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        for c in range(min(max_cols, 15)):
            self.table.resizeColumnToContents(c)
            if self.table.columnWidth(c) < 80:
                self.table.setColumnWidth(c, 80)

        self.table.blockSignals(False)
        self._loading = False

    def _col_to_letter(self, col_idx):
        result = ""
        while col_idx >= 0:
            result = chr(col_idx % 26 + 65) + result
            col_idx = col_idx // 26 - 1
        return result

    # ── Table Grid & Raw View Editing ─────────────────────────────────────
    def _on_cell_changed(self, item):
        if self._loading:
            return
        self.is_modified = True
        self.textChanged.emit()

    def _on_raw_text_changed(self):
        if self._loading or self.view_mode != "raw":
            return
        self.is_modified = True
        self.textChanged.emit()

    def _on_delimiter_changed(self, index):
        if self._loading:
            return
        if self.file_path or self.table.rowCount() > 0:
            content = self.toPlainText()
            self.load_from_content(content)

    def _on_quoting_changed(self, index):
        if self._loading:
            return
        self.is_modified = True
        self.textChanged.emit()

    def toggle_view_mode(self):
        if self.view_mode == "grid":
            # Switch to Raw Text
            self._loading = True
            raw_text = self._grid_to_csv_string()
            self.raw_editor.setPlainText(raw_text)
            self.stack.setCurrentIndex(1)
            self.view_mode = "raw"
            self.btn_toggle_view.setText("📊 Table Grid")
            self.btn_add_row.setEnabled(False)
            self.btn_add_col.setEnabled(False)
            self.btn_del.setEnabled(False)
            self._loading = False
        else:
            # Switch to Table Grid
            raw_text = self.raw_editor.toPlainText()
            self.view_mode = "grid"
            self.btn_toggle_view.setText("📄 Raw Text")
            self.btn_add_row.setEnabled(True)
            self.btn_add_col.setEnabled(True)
            self.btn_del.setEnabled(True)
            self.stack.setCurrentIndex(0)
            self.load_from_content(raw_text)

    def add_row(self):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        for c in range(self.table.columnCount()):
            self.table.setItem(row_idx, c, QTableWidgetItem(""))
        self.is_modified = True
        self.textChanged.emit()

    def add_column(self):
        col_idx = self.table.columnCount()
        self.table.insertColumn(col_idx)
        letter = self._col_to_letter(col_idx)
        self.table.setHorizontalHeaderItem(col_idx, QTableWidgetItem(letter))
        for r in range(self.table.rowCount()):
            self.table.setItem(r, col_idx, QTableWidgetItem(""))
        self.is_modified = True
        self.textChanged.emit()

    def delete_selected(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return
        
        # Determine whether to delete rows or columns based on selection spanning
        for rng in sorted(selected_ranges, key=lambda r: r.topRow(), reverse=True):
            if rng.leftColumn() == 0 and rng.rightColumn() == self.table.columnCount() - 1:
                for r in range(rng.bottomRow(), rng.topRow() - 1, -1):
                    self.table.removeRow(r)
            elif rng.topRow() == 0 and rng.bottomRow() == self.table.rowCount() - 1:
                for c in range(rng.rightColumn(), rng.leftColumn() - 1, -1):
                    self.table.removeColumn(c)
            else:
                # Default: clear contents of selected cells
                for r in range(rng.topRow(), rng.bottomRow() + 1):
                    for c in range(rng.leftColumn(), rng.rightColumn() + 1):
                        item = self.table.item(r, c)
                        if item:
                            item.setText("")
        self.is_modified = True
        self.textChanged.emit()

    # ── Serialization & Saving ────────────────────────────────────────────
    def _grid_to_csv_string(self):
        delim = self.combo_delim.currentData()
        if delim == "auto" or not delim:
            delim = "," if not self.file_path or not str(self.file_path).endswith(".tsv") else "\t"
        quote = self.combo_quote.currentData()
        if quote is None:
            quote = csv.QUOTE_MINIMAL

        output = io.StringIO()
        writer = csv.writer(output, delimiter=delim, quoting=quote)
        for r in range(self.table.rowCount()):
            row_vals = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row_vals.append(item.text() if item else "")
            writer.writerow(row_vals)
        return output.getvalue()

    def toPlainText(self):
        if self.view_mode == "raw":
            return self.raw_editor.toPlainText()
        return self._grid_to_csv_string()

    def setPlainText(self, text):
        if self.view_mode == "raw":
            self.raw_editor.setPlainText(text)
        else:
            self.load_from_content(text)
        self.is_modified = False

    def to_csv_bytes(self):
        return self.toPlainText().encode("utf-8")

    # ── Universal TTS (F9) Support ────────────────────────────────────────
    def read_current_page(self, voice_id=None):
        """Duck-typed TTS method for Universal Read Aloud (F9)."""
        if self.view_mode == "raw":
            return self.raw_editor.read_current_page(voice_id=voice_id)

        selected_items = self.table.selectedItems()
        if selected_items:
            lines = []
            for item in selected_items:
                r = item.row() + 1
                c = self._col_to_letter(item.column())
                val = item.text().strip()
                if val:
                    lines.append(f"Row {r}, Column {c}: {val}")
            if lines:
                return ". ".join(lines)

        # Fallback: Read summary and top headers
        num_rows = self.table.rowCount()
        num_cols = self.table.columnCount()
        headers = []
        if num_rows > 0:
            for c in range(min(num_cols, 5)):
                item = self.table.item(0, c)
                if item and item.text().strip():
                    headers.append(item.text().strip())
        
        summary = f"CSV spreadsheet with {num_rows} rows and {num_cols} columns."
        if headers:
            summary += f" First row contains: {', '.join(headers)}."
        return summary
