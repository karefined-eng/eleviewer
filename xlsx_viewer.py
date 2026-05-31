from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QLabel, QComboBox, QHBoxLayout, QHeaderView
)
from PySide6.QtCore import Signal, Qt
from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
import io


class XlsxViewer(QWidget):
    """
    XLSX viewer and editor.
    Displays spreadsheet in an editable table.
    Supports multiple sheets and cell editing.
    Handles merged cells gracefully (read-only).
    """
    
    textChanged = Signal()  # Signal to notify modifications
    
    def __init__(self, file_path=None):
        super().__init__()
        
        self.file_path = file_path
        self.is_modified = False
        self.workbook = None
        self.current_sheet_name = None
        self.merged_cells_ranges = set()  # Track merged cells to skip them on save
        
        # UI Setup
        layout = QVBoxLayout()
        
        # Header with sheet selector
        header_layout = QHBoxLayout()
        
        header_label = QLabel("📊 XLSX Spreadsheet Editor")
        header_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
            }
        """)
        
        self.sheet_selector = QComboBox()
        self.sheet_selector.setStyleSheet("""
            QComboBox {
                background: #2a2a2a;
                color: #fff;
                border: 1px solid #444;
                padding: 5px;
            }
        """)
        self.sheet_selector.currentTextChanged.connect(self._on_sheet_changed)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Sheet:"))
        header_layout.addWidget(self.sheet_selector)
        
        # Main table widget
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background: #1e1e1e;
                color: #fff;
                gridline-color: #333;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background: #0e47a1;
            }
        """)
        
        # Enable editing
        self.table.itemChanged.connect(self._on_cell_changed)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.table)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(layout)
        
        # Load file if provided
        if file_path:
            self.load_from_path(file_path)
    
    def load_from_path(self, file_path):
        """Load XLSX file from disk with robust error handling."""
        try:
            # Use data_only=True to avoid formula parsing issues
            # Use keep_vba=False to simplify loading
            self.workbook = load_workbook(file_path, data_only=False, keep_vba=False)
            
            # Populate sheet selector
            self.sheet_selector.blockSignals(True)
            self.sheet_selector.clear()
            self.sheet_selector.addItems(self.workbook.sheetnames)
            self.sheet_selector.blockSignals(False)
            
            # Load first sheet
            if self.workbook.sheetnames:
                self._on_sheet_changed(self.workbook.sheetnames[0])
            
            self.is_modified = False
        
        except Exception as e:
            # Provide helpful error message
            error_msg = str(e)
            if "defaultColWidthPt" in error_msg:
                raise Exception("XLSX file compatibility issue. Try opening in Excel and re-saving, or use a newer openpyxl version.")
            raise Exception(f"Failed to load XLSX: {error_msg}")
    
    def _on_sheet_changed(self, sheet_name):
        """Load a different sheet from the workbook."""
        if not self.workbook or sheet_name not in self.workbook.sheetnames:
            return
        
        self.current_sheet_name = sheet_name
        ws = self.workbook[sheet_name]
        
        # Get dimensions
        max_row = ws.max_row or 1
        max_col = ws.max_column or 1
        
        # Store merged cells ranges for later (to skip on save)
        self.merged_cells_ranges = set(ws.merged_cells.ranges)
        
        # Setup table
        self.table.blockSignals(True)
        self.table.setRowCount(max_row)
        self.table.setColumnCount(max_col)
        
        # Populate cells
        for row_idx in range(1, max_row + 1):
            for col_idx in range(1, max_col + 1):
                try:
                    cell = ws.cell(row=row_idx, column=col_idx)
                    
                    # Handle merged cells
                    is_merged = isinstance(cell, MergedCell)
                    value = cell.value if cell.value is not None else ""
                    
                    item = QTableWidgetItem(str(value))
                    
                    # Make merged cells read-only for display
                    if is_merged:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    self.table.setItem(row_idx - 1, col_idx - 1, item)
                
                except Exception:
                    # Fallback for problematic cells
                    item = QTableWidgetItem("")
                    self.table.setItem(row_idx - 1, col_idx - 1, item)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        self.table.blockSignals(False)
        self.is_modified = False
    
    def _on_cell_changed(self, item):
        """Mark as modified when user edits a cell."""
        self.is_modified = True
        self.textChanged.emit()
    
    def to_xlsx_bytes(self):
        """
        Convert current table content back to XLSX bytes.
        Updates cells in the workbook with edited values.
        Skips merged cells (read-only).
        """
        try:
            # Update workbook with current table values
            ws = self.workbook[self.current_sheet_name]
            
            for row_idx in range(self.table.rowCount()):
                for col_idx in range(self.table.columnCount()):
                    try:
                        cell = ws.cell(row=row_idx + 1, column=col_idx + 1)
                        
                        # Skip merged cells — they're read-only
                        if isinstance(cell, MergedCell):
                            continue
                        
                        item = self.table.item(row_idx, col_idx)
                        value = item.text() if item else ""
                        
                        # Only update if value changed
                        if str(cell.value or "") != value:
                            cell.value = value
                    
                    except Exception:
                        # Skip problematic cells
                        continue
            
            # Save to bytes
            byte_stream = io.BytesIO()
            self.workbook.save(byte_stream)
            byte_stream.seek(0)
            
            return byte_stream.getvalue()
        
        except Exception as e:
            raise Exception(f"Failed to save XLSX: {str(e)}")
    
    def toPlainText(self):
        """Compatibility method - returns CSV-like text representation."""
        text_rows = []
        for row_idx in range(self.table.rowCount()):
            row_vals = []
            for col_idx in range(self.table.columnCount()):
                item = self.table.item(row_idx, col_idx)
                row_vals.append(item.text() if item else "")
            text_rows.append(" | ".join(row_vals))
        
        return "\n".join(text_rows)
    
    def setPlainText(self, text):
        """Compatibility method - NOT fully supported for XLSX (use load_from_path instead)."""
        # For reopening tabs, this is a fallback. Ideally, use file path.
        pass