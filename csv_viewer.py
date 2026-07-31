"""
High-performance CSV/TSV Table Viewer and Editor (CsvViewer) for EleViewer.
Features off-thread QThread parsing, interactive delimiter/quoting toolbar overrides,
dual Table Grid ⇄ Raw Text view modes, non-destructive text preservation, and Universal TTS.
"""

import csv
import io
import os
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView, QComboBox, 
    QPushButton, QToolButton, QLabel, QStackedWidget, QMessageBox, 
    QAbstractItemView, QFrame
)

from editor import EditorTab
from theme import (
    get_active_palette, get_brand_accent,
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
                # Sniff encoding with chardet; fall back to utf-8 then latin-1
                detected_encoding = self.encoding
                try:
                    import chardet
                    with open(self.file_path, "rb") as fb:
                        raw_bytes = fb.read(32768)  # sample first 32 KB
                    result = chardet.detect(raw_bytes)
                    if result and result.get("confidence", 0) >= 0.7:
                        detected_encoding = result["encoding"] or "utf-8"
                except Exception:
                    detected_encoding = self.encoding or "utf-8"

                try:
                    with open(self.file_path, "r", encoding=detected_encoding, errors="replace") as f:
                        raw_text = f.read()
                except (UnicodeDecodeError, LookupError):
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


class CsvTableModel(QAbstractTableModel):
    """Virtualized model for high-performance rendering of large CSV datasets."""
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self._data = data if data else [[""]]
        self._max_cols = max((len(r) for r in self._data), default=1)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return self._max_cols

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        r, c = index.row(), index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if r < len(self._data) and c < len(self._data[r]):
                return str(self._data[r][c])
            return ""
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            r, c = index.row(), index.column()
            while len(self._data) <= r:
                self._data.append([])
            while len(self._data[r]) <= c:
                self._data[r].append("")
            self._data[r][c] = str(value)
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._col_to_letter(section)
            elif orientation == Qt.Vertical:
                return str(section + 1)
        return None

    def _col_to_letter(self, col_idx):
        result = ""
        while col_idx >= 0:
            result = chr(col_idx % 26 + 65) + result
            col_idx = col_idx // 26 - 1
        return result

    def set_data(self, data):
        self.beginResetModel()
        self._data = data if data else [[""]]
        self._max_cols = max((len(r) for r in self._data), default=1)
        self.endResetModel()

    def get_data(self):
        return self._data

    def add_row(self):
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append([""] * self._max_cols)
        self.endInsertRows()

    def add_column(self):
        self.beginInsertColumns(QModelIndex(), self._max_cols, self._max_cols)
        self._max_cols += 1
        for r in self._data:
            while len(r) < self._max_cols:
                r.append("")
        self.endInsertColumns()

    def remove_rows(self, row_indices):
        for r in sorted(row_indices, reverse=True):
            if 0 <= r < len(self._data):
                self.beginRemoveRows(QModelIndex(), r, r)
                del self._data[r]
                self.endRemoveRows()
        if not self._data:
            self._data = [[""]]
            self._max_cols = 1


class CsvViewer(QWidget):
    """CSV/TSV Workstation Table Viewer & Raw Text Editor."""
    textChanged = Signal()

    def __init__(self, file_path=None, content=None):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        self._loading = False
        self._bookmark_callback = None
        self.current_delimiter = "auto"
        self.current_quoting = csv.QUOTE_MINIMAL
        self.current_encoding = "utf-8"
        self.view_mode = "grid"  # 'grid' or 'raw'
        self.worker = None

        self._build_ui()

        if content is not None:
            self.load_from_content(content)
        elif file_path:
            self.load_from_path(file_path)
        else:
            self.model.set_data([["A", "B", "C"], ["", "", ""]])
            self.is_modified = False

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Toolbar ────────────────────────────────────────────────────────
        p = get_active_palette()
        self.toolbar = QFrame()
        self.toolbar.setStyleSheet(f"""
            QFrame {{
                background-color: {p['BRAND_PANEL']};
                border-bottom: 1px solid {p['BRAND_BORDER']};
                padding: 4px 8px;
            }}
            QLabel {{ color: {p['BRAND_MUTED_FG']}; font-size: 11px; font-weight: bold; }}
            QComboBox {{
                background-color: {p['BRAND_PANEL_2']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 12px;
                min-width: 90px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                selection-background-color: #6cb6ff;
                selection-color: #0c1826;
            }}
            QComboBox::drop-down {{ border: none; }}
            QPushButton {{
                background-color: {p['BRAND_PANEL_2']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background-color: {p['BRAND_BORDER']}; }}
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

        self.btn_bookmark = QPushButton("🔖 Bookmark")
        self.btn_bookmark.setToolTip("Bookmark current scroll position")
        self.btn_bookmark.clicked.connect(self._add_bookmark_here)
        tb_layout.addWidget(self.btn_bookmark)

        # View Switcher
        self.btn_toggle_view = QPushButton("📄 Raw Text")
        self.btn_toggle_view.setToolTip("Toggle between Table Grid View and Raw CSV Text View")
        self.btn_toggle_view.clicked.connect(self.toggle_view_mode)
        tb_layout.addWidget(self.btn_toggle_view)

        layout.addWidget(self.toolbar)

        # ── Stacked Views (Grid vs Raw Text) ──────────────────────────────
        self.stack = QStackedWidget()

        # 1. Grid View (Virtualized QTableView)
        self.model = CsvTableModel()
        self.model.dataChanged.connect(self._on_cell_changed)
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setStyleSheet(f"""
            QTableView {{
                background-color: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                gridline-color: {p['BRAND_BORDER']};
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }}
            QTableView::item {{ padding: 6px; }}
            QTableView::item:selected {{
                background-color: {get_brand_accent()};
                color: {p['BRAND_BACKGROUND']};
            }}
            QHeaderView::section {{
                background-color: {p['BRAND_PANEL_2']};
                color: {p['BRAND_MUTED_FG']};
                padding: 6px;
                border: 1px solid {p['BRAND_BORDER']};
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
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
        self.model.set_data(rows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        for c in range(min(self.model.columnCount(), 15)):
            self.table.resizeColumnToContents(c)
            if self.table.columnWidth(c) < 80:
                self.table.setColumnWidth(c, 80)
        self._loading = False

    def _col_to_letter(self, col_idx):
        result = ""
        while col_idx >= 0:
            result = chr(col_idx % 26 + 65) + result
            col_idx = col_idx // 26 - 1
        return result

    # ── Table Grid & Raw View Editing ─────────────────────────────────────
    def _on_cell_changed(self, top_left=None, bottom_right=None, roles=None):
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
        if self.file_path or self.model.rowCount() > 0:
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
        self.model.add_row()
        self.is_modified = True
        self.textChanged.emit()

    def add_column(self):
        self.model.add_column()
        self.is_modified = True
        self.textChanged.emit()

    def delete_selected(self):
        selected_indexes = self.table.selectedIndexes()
        if not selected_indexes:
            return
        rows_to_del = set(idx.row() for idx in selected_indexes)
        self.model.remove_rows(rows_to_del)
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
        for row in self.model.get_data():
            writer.writerow(row)
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

    def set_bookmark_callback(self, callback):
        self._bookmark_callback = callback

    def _bookmark_payload(self):
        name = os.path.basename(self.file_path) if self.file_path else "csv file"
        return {
            "page_number": 0,
            "scroll_position_y": float(self.table.verticalScrollBar().value()),
            "scroll_position_x": float(self.table.horizontalScrollBar().value()),
            "label": f"Position in {name}",
        }

    def _add_bookmark_here(self):
        if self._bookmark_callback:
            self._bookmark_callback(self._bookmark_payload())

    def go_to_bookmark(self, page_number=0, scroll_position_y=0.0, **kwargs):
        self.table.verticalScrollBar().setValue(int(scroll_position_y))
        if "scroll_position_x" in kwargs:
            self.table.horizontalScrollBar().setValue(int(kwargs["scroll_position_x"]))

    # ── Universal TTS (F9) Support ────────────────────────────────────────
    def read_current_page(self, voice_id=None):
        """Duck-typed TTS method for Universal Read Aloud (F9)."""
        if self.view_mode == "raw":
            return self.raw_editor.read_current_page(voice_id=voice_id)

        selected_indexes = self.table.selectedIndexes()
        if selected_indexes:
            lines = []
            for idx in selected_indexes:
                r = idx.row() + 1
                c = self._col_to_letter(idx.column())
                val = str(self.model.data(idx, Qt.DisplayRole) or "").strip()
                if val:
                    lines.append(f"Row {r}, Column {c}: {val}")
            if lines:
                return ". ".join(lines)

        # Fallback: Read summary and top headers
        num_rows = self.model.rowCount()
        num_cols = self.model.columnCount()
        headers = []
        if num_rows > 0:
            for c in range(min(num_cols, 5)):
                val = str(self.model.data(self.model.index(0, c), Qt.DisplayRole) or "").strip()
                if val:
                    headers.append(val)
        
        summary = f"CSV spreadsheet with {num_rows} rows and {num_cols} columns."
        if headers:
            summary += f" First row contains: {', '.join(headers)}."
        return summary
