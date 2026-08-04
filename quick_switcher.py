import os
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel,
    QStyledItemDelegate, QStyle
)
from PySide6.QtCore import Qt, Signal, QEvent, QTimer, Slot, QRect, QPoint
from PySide6.QtGui import QIcon, QColor, QPainter, QFont, QPen
from theme import get_active_palette, get_brand_accent
from file_icons import file_type_icon
from icons import icon
from vault_search import VaultSearchWorker
from bookmark_manager import load_bookmarks
from web_history import get_history


class _BadgeDelegate(QStyledItemDelegate):
    """Renders a muted pill badge (Tab / Pin / Bookmark etc.) on the right of each list item."""
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        badge = index.data(Qt.UserRole + 1)
        if not badge:
            return

        p = get_active_palette()
        is_selected = option.state & QStyle.State_Selected

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        badge_text = badge
        font = QFont(option.font)
        font.setPointSize(max(7, option.font.pointSize() - 2))
        painter.setFont(font)

        fm = painter.fontMetrics()
        text_w = fm.horizontalAdvance(badge_text)
        pill_w = text_w + 12
        pill_h = fm.height() + 4
        right_margin = 10
        pill_x = option.rect.right() - pill_w - right_margin
        pill_y = option.rect.center().y() - pill_h // 2
        pill_rect = QRect(pill_x, pill_y, pill_w, pill_h)

        # Background pill
        bg_color = QColor(p['BRAND_BORDER'])
        if is_selected:
            bg_color = QColor(p['BRAND_BACKGROUND'])
            bg_color.setAlpha(80)
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(pill_rect, 4, 4)

        # Badge text
        text_color = QColor(p['BRAND_MUTED_FG']) if not is_selected else QColor(p['BRAND_BACKGROUND'])
        painter.setPen(text_color)
        painter.drawText(pill_rect, Qt.AlignCenter, badge_text)
        painter.restore()

class QuickSwitcher(QDialog):
    """
    Unified Command Palette / Quick Switcher.
    Searches files, bookmarks, web history, and URLs.
    """
    file_selected = Signal(str)
    url_selected = Signal(str)

    def __init__(self, recent_files, pinned_files, open_tabs=None, vaults=None, parent=None):
        super().__init__(parent)
        self.recent_files = recent_files or []
        self.pinned_files = pinned_files or []
        self.open_tabs = open_tabs or []
        self.vaults = vaults or []
        
        self.bookmarks = load_bookmarks(validate=False)
        self._search_worker = None
        self._pending_results = []
        
        # Collect local files
        self.local_files = []
        seen = set()
        for lst in [self.open_tabs, self.pinned_files, self.recent_files]:
            for f in lst:
                if f not in seen:
                    self.local_files.append(f)
                    seen.add(f)
                    
        self.setWindowTitle("Quick Switcher")
        p = get_active_palette()
        accent = get_brand_accent()
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: 1px solid {p['BRAND_BORDER']};
                border-radius: 8px;
            }}
            QLineEdit {{
                background: {p['BRAND_PANEL']};
                color: {p['BRAND_PRIMARY']};
                border: none;
                border-bottom: 1px solid {p['BRAND_BORDER']};
                padding: 12px 14px;
                font-size: 16px;
                selection-background-color: {accent};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QListWidget {{
                background: transparent;
                color: {p['BRAND_PRIMARY']};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {p['BRAND_BORDER']};
            }}
            QListWidget::item:selected {{
                background: {accent};
                color: {p['BRAND_BACKGROUND']};
            }}
            QListWidget::item:hover {{
                background: {p['BRAND_PANEL_2']};
            }}
        """)
        
        self.resize(650, 450)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files, bookmarks, or type a URL...")
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.returnPressed.connect(self.select_current)
        
        # File list
        self.file_list = QListWidget()
        self._badge_delegate = _BadgeDelegate(self.file_list)
        self.file_list.setItemDelegate(self._badge_delegate)
        self.file_list.itemDoubleClicked.connect(self.on_item_selected)
        self.file_list.keyPressEvent = self.list_key_press
        
        # Help text
        help_label = QLabel("↑↓ Navigate  Enter Select  Esc Cancel")
        help_label.setStyleSheet(f"color: {p['BRAND_MUTED_FG']}; font-size: 11px; padding: 6px 10px;")
        
        layout.addWidget(self.search_input)
        layout.addWidget(self.file_list)
        layout.addWidget(help_label)
        
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(200)
        self.debounce_timer.timeout.connect(self._do_search)
        
        self._populate_initial()
        self.search_input.setFocus()

    def _cleanup_worker(self):
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.cancel()
            self._search_worker.terminate()
            self._search_worker.wait()

    def reject(self):
        self._cleanup_worker()
        super().reject()
        
    def accept(self):
        self._cleanup_worker()
        super().accept()
        
    def _populate_initial(self):
        self.file_list.clear()
        self._add_section_header("📂 Open Tabs")
        for f in [f for f in self.local_files if f in self.open_tabs]:
            self._add_file_item(f, badge="Tab")
            
        self._add_section_header("📌 Pinned")
        for f in [f for f in self.local_files if f in self.pinned_files and f not in self.open_tabs]:
            self._add_file_item(f, badge="Pin")
            
        self._add_section_header("🕐 Recent")
        for f in [f for f in self.local_files if f in self.recent_files and f not in self.open_tabs and f not in self.pinned_files]:
            self._add_file_item(f, badge="Recent")
            
        self._select_first()

    def _add_section_header(self, text):
        p = get_active_palette()
        item = QListWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        item.setForeground(QColor(p['BRAND_MUTED_FG']))
        self.file_list.addItem(item)

    def _add_file_item(self, filepath, subtitle=None, badge=None):
        p = get_active_palette()
        name = Path(filepath).name
        label = name
        if subtitle:
            label = f"{name}  —  {subtitle}"
        
        item = QListWidgetItem(label)
        item.setData(Qt.UserRole, {"type": "file", "path": filepath})
        item.setIcon(file_type_icon(Path(filepath).suffix, 16))
        if badge:
            item.setData(Qt.UserRole + 1, badge)
        self.file_list.addItem(item)
        # Render the badge as a tooltip-style suffix in muted color via item data
        if badge:
            item.setToolTip(f"{badge}: {filepath}")

    def _add_url_item(self, title, url, icon_name="globe", badge="Web"):
        item = QListWidgetItem(f"{title}")
        item.setData(Qt.UserRole, {"type": "url", "url": url})
        item.setIcon(icon(icon_name, size=16))
        item.setData(Qt.UserRole + 1, badge)
        item.setToolTip(f"{badge}: {url}")
        self.file_list.addItem(item)
        
    def _add_bookmark_item(self, bookmark):
        title = bookmark.get("label", "Bookmark")
        path = bookmark.get("file_path", "")
        doc_name = Path(path).name
        # Show document name first, then bookmark label, badge indicates type
        item = QListWidgetItem(f"{doc_name}  →  {title}")
        item.setData(Qt.UserRole, {"type": "file", "path": path})
        item.setIcon(icon("bookmark", size=16))
        item.setData(Qt.UserRole + 1, "Bookmark")
        item.setToolTip(f"Bookmark: {path}")
        self.file_list.addItem(item)

    def _select_first(self):
        for i in range(self.file_list.count()):
            if self.file_list.item(i).flags() & Qt.ItemIsSelectable:
                self.file_list.setCurrentRow(i)
                break

    def _on_text_changed(self, text):
        if not text.strip():
            self._cleanup_worker()
            self._populate_initial()
            return
        self.debounce_timer.start()

    def _do_search(self):
        query = self.search_input.text().strip().lower()
        if not query:
            return

        self._cleanup_worker()
        self.file_list.clear()
        self._pending_results.clear()
        
        # 1. URL Check
        if query.startswith(("http://", "https://", "www.")):
            url = query if "://" in query else f"https://{query}"
            self._add_url_item(f"🌐 Navigate to: {url}", url)
            
        # 2. Local Files (Fuzzy)
        for filepath in self.local_files:
            name = Path(filepath).name.lower()
            badge = "Tab" if filepath in self.open_tabs else ("Pin" if filepath in self.pinned_files else "Recent")
            
            # Short query -> exact substring only
            if len(query) < 3:
                if query in name:
                    self._add_file_item(filepath, badge=badge)
                    self._pending_results.append(filepath)
                continue
                
            # Fuzzy match with density check
            idx = 0
            first_match = -1
            last_match = -1
            for i, char in enumerate(name):
                if idx < len(query) and char == query[idx]:
                    if first_match == -1:
                        first_match = i
                    last_match = i
                    idx += 1
            
            if idx == len(query):
                span = (last_match - first_match) + 1
                if span <= max(len(query) * 4, 12):
                    self._add_file_item(filepath, badge=badge)
                    self._pending_results.append(filepath)

        # 3. Bookmarks
        if len(query) >= 2:
            for b in self.bookmarks:
                label = b.get("label", "").lower()
                path = str(b.get("file_path", "")).lower()
                filename = Path(path).name.lower()
                
                # Deduplicate: if file is already in results, skip its bookmarks? No, users might want to jump to the bookmark.
                # Just fix over-matching by checking against filename + label, not the whole directory path.
                if query in label or query in filename:
                    self._add_bookmark_item(b)
                
        # 4. Web History
        try:
            history = get_history(query, limit=5)
            for h in history:
                self._add_url_item(h.get('title', h.get('url')), h.get("url"), "clock", badge="History")
        except Exception:
            pass

        self._select_first()

        # 5. Background Vault Search
        if self.vaults:
            loading_item = QListWidgetItem("Loading vault results…")
            loading_item.setFlags(loading_item.flags() & ~Qt.ItemIsSelectable)
            loading_item.setForeground(QColor(get_active_palette()['BRAND_MUTED_FG']))
            self.file_list.addItem(loading_item)
            self._search_worker = VaultSearchWorker(self.vaults, query)
            self._search_worker.result_found.connect(self._on_vault_result)
            self._search_worker.finished.connect(self._vault_search_finished)
            self._search_worker.start()
        elif self.file_list.count() == 0:
            empty_item = QListWidgetItem("No results found.")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsSelectable)
            empty_item.setForeground(QColor(get_active_palette()['BRAND_MUTED_FG']))
            self.file_list.addItem(empty_item)

    @Slot(str, str, str, str, str)
    def _on_vault_result(self, filename, display_dir, vault_name, full_path, snippet):
        # Remove loading placeholder on first result
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item and item.text() == "Loading vault results…":
                self.file_list.takeItem(i)
                break

        if full_path in self._pending_results:
            return
        self._pending_results.append(full_path)
        
        subtitle = f"{display_dir.strip(' ()')} [{vault_name}]" if display_dir.strip(' ()') else f"[{vault_name}]"
        if snippet:
            subtitle += f" — {snippet[:60]}"
            
        self._add_file_item(full_path, subtitle, badge="Vault")
        if self.file_list.currentRow() == -1:
            self._select_first()

    def _vault_search_finished(self):
        # Remove loading placeholder if still present
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item and item.text() == "Loading vault results…":
                self.file_list.takeItem(i)
                break
        if self.file_list.count() == 0:
            empty_item = QListWidgetItem("No results found.")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsSelectable)
            empty_item.setForeground(QColor(get_active_palette()['BRAND_MUTED_FG']))
            self.file_list.addItem(empty_item)
            self._select_first()

    def select_current(self):
        current_item = self.file_list.currentItem()
        if current_item and (current_item.flags() & Qt.ItemIsSelectable):
            self.on_item_selected(current_item)

    def on_item_selected(self, item):
        data = item.data(Qt.UserRole)
        if not data:
            return
        if data["type"] == "file":
            self.file_selected.emit(data["path"])
        elif data["type"] == "url":
            self.url_selected.emit(data["url"])
        self.accept()
        
    def list_key_press(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return:
            self.select_current()
        else:
            QListWidget.keyPressEvent(self.file_list, event)
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Up, Qt.Key_Down):
            if self.search_input.hasFocus() and self.file_list.count() > 0:
                self.file_list.setFocus()
                if self.file_list.currentRow() == -1:
                    self._select_first()
                else:
                    self.file_list.keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def event(self, ev):
        if ev.type() == QEvent.WindowDeactivate:
            self.reject()
            return True
        return super().event(ev)