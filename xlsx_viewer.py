from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QTabBar, QHeaderView,
)
from PySide6.QtCore import Signal, Qt
from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
import io

from theme import xlsx_sheet_tab_stylesheet


class XlsxViewer(QWidget):
    """XLSX viewer with Google Sheets-style bottom sheet tabs."""

    textChanged = Signal()

    def __init__(self, file_path=None):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        self.workbook = None
        self.current_sheet_name = None
        self.merged_cells_ranges = set()
        self._loading_sheet = False

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1e1e1e;
                color: #fff;
                gridline-color: #333;
            }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected { background: #0e47a1; }
        """)
        self.table.itemChanged.connect(self._on_cell_changed)

        self.sheet_tabs = QTabBar()
        self.sheet_tabs.setDrawBase(True)
        self.sheet_tabs.setStyleSheet(xlsx_sheet_tab_stylesheet())
        self.sheet_tabs.currentChanged.connect(self._on_tab_index_changed)

        layout.addWidget(self.table)
        layout.addWidget(self.sheet_tabs)
        self.setLayout(layout)

        if file_path:
            self.load_from_path(file_path)
        else:
            from openpyxl import Workbook
            self.workbook = Workbook()
            self.sheet_tabs.blockSignals(True)
            while self.sheet_tabs.count():
                self.sheet_tabs.removeTab(0)
            for name in self.workbook.sheetnames:
                self.sheet_tabs.addTab(name)
            self.sheet_tabs.blockSignals(False)
            if self.workbook.sheetnames:
                self.sheet_tabs.setCurrentIndex(0)
                self._on_sheet_changed(self.workbook.sheetnames[0])
            self.is_modified = False

    def load_from_path(self, file_path):
        try:
            self.workbook = load_workbook(file_path, data_only=False, keep_vba=False)
            self.sheet_tabs.blockSignals(True)
            while self.sheet_tabs.count():
                self.sheet_tabs.removeTab(0)
            for name in self.workbook.sheetnames:
                self.sheet_tabs.addTab(name)
            self.sheet_tabs.blockSignals(False)

            if self.workbook.sheetnames:
                self.sheet_tabs.setCurrentIndex(0)
                self._on_sheet_changed(self.workbook.sheetnames[0])
            self.is_modified = False
        except Exception as e:
            error_msg = str(e)
            if "defaultColWidthPt" in error_msg:
                raise Exception(
                    "XLSX file compatibility issue. Try opening in Excel and re-saving."
                )
            raise Exception(f"Failed to load XLSX: {error_msg}")

    def _on_tab_index_changed(self, index):
        if index < 0 or not self.workbook:
            return
        name = self.sheet_tabs.tabText(index)
        if name != self.current_sheet_name:
            self._flush_table_to_workbook()
            self._on_sheet_changed(name)

    def _flush_table_to_workbook(self):
        if not self.workbook or not self.current_sheet_name:
            return
        ws = self.workbook[self.current_sheet_name]
        for row_idx in range(self.table.rowCount()):
            for col_idx in range(self.table.columnCount()):
                try:
                    cell = ws.cell(row=row_idx + 1, column=col_idx + 1)
                    if isinstance(cell, MergedCell):
                        continue
                    item = self.table.item(row_idx, col_idx)
                    value = item.text() if item else ""
                    if str(cell.value or "") != value:
                        cell.value = value
                except Exception:
                    continue

    def _on_sheet_changed(self, sheet_name):
        if not self.workbook or sheet_name not in self.workbook.sheetnames:
            return

        self._loading_sheet = True
        self.current_sheet_name = sheet_name
        ws = self.workbook[sheet_name]
        max_row = max(ws.max_row or 1, 20)
        max_col = max(ws.max_column or 1, 10)
        self.merged_cells_ranges = set(ws.merged_cells.ranges)

        self.table.blockSignals(True)
        self.table.setRowCount(max_row)
        self.table.setColumnCount(max_col)

        for row_idx in range(1, max_row + 1):
            for col_idx in range(1, max_col + 1):
                try:
                    cell = ws.cell(row=row_idx, column=col_idx)
                    is_merged = isinstance(cell, MergedCell)
                    value = cell.value if cell.value is not None else ""
                    item = QTableWidgetItem(str(value))
                    if is_merged:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row_idx - 1, col_idx - 1, item)
                except Exception:
                    self.table.setItem(row_idx - 1, col_idx - 1, QTableWidgetItem(""))

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.blockSignals(False)
        self._loading_sheet = False

    def _on_cell_changed(self, item):
        if self._loading_sheet:
            return
        self.is_modified = True
        self.textChanged.emit()

    def to_xlsx_bytes(self):
        try:
            self._flush_table_to_workbook()
            byte_stream = io.BytesIO()
            self.workbook.save(byte_stream)
            byte_stream.seek(0)
            return byte_stream.getvalue()
        except Exception as e:
            raise Exception(f"Failed to save XLSX: {str(e)}")

    def toPlainText(self):
        text_rows = []
        for row_idx in range(self.table.rowCount()):
            row_vals = []
            for col_idx in range(self.table.columnCount()):
                item = self.table.item(row_idx, col_idx)
                row_vals.append(item.text() if item else "")
            text_rows.append(" | ".join(row_vals))
        return "\n".join(text_rows)

    def setPlainText(self, text):
        pass
