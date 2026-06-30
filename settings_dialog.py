from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QSpinBox, QPushButton, QFormLayout, QTabWidget,
    QComboBox, QWidget,
)

from settings import load_settings, save_settings, DEFAULT_SETTINGS, DEFAULT_WEB_TABS
from theme import (
    MARKDOWN_ICON_SIZE_MIN, MARKDOWN_ICON_SIZE_MAX,
    resolve_markdown_icon_size,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(520, 380)
        self.settings = load_settings()

        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        tabs.addTab(self._build_general_tab(), "Startup & Defaults")
        tabs.addTab(self._build_editor_tab(), "Text Editing")
        tabs.addTab(self._build_pdf_tab(), "PDF Reading")
        tabs.addTab(self._build_vault_tab(), "Folders & Organization")
        tabs.addTab(self._build_web_tab(), "Web Browser Panel")
        layout.addWidget(tabs)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

    def _build_general_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self.autosave_check = QCheckBox("Enable automatic background saving")
        self.autosave_check.setChecked(self.settings.get("autosave_enabled", True))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(2, 300)
        self.interval_spin.setSuffix(" sec")
        self.interval_spin.setValue(self.settings.get("autosave_interval_seconds", 5))
        form.addRow(self.autosave_check)
        form.addRow("Autosave interval:", self.interval_spin)
        return w

    def _build_editor_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self.md_mode_combo = QComboBox()
        self.md_mode_combo.addItems(["view", "simple", "syntax"])
        current = self.settings.get("markdown_default_mode", "view")
        self.md_mode_combo.setCurrentText(current)
        self.md_icon_spin = QSpinBox()
        self.md_icon_spin.setRange(MARKDOWN_ICON_SIZE_MIN, MARKDOWN_ICON_SIZE_MAX)
        self.md_icon_spin.setValue(resolve_markdown_icon_size(self.settings.get("markdown_icon_size")))
        form.addRow("Default markdown mode:", self.md_mode_combo)
        form.addRow("Mode icon size (px):", self.md_icon_spin)
        return w

    def _build_pdf_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self.pdf_fit_combo = QComboBox()
        self.pdf_fit_combo.addItems(["page", "width"])
        self.pdf_fit_combo.setCurrentText(self.settings.get("pdf_fit_mode", "width"))
        self.pdf_quality_combo = QComboBox()
        self.pdf_quality_combo.addItems(["normal", "high"])
        self.pdf_quality_combo.setCurrentText(self.settings.get("pdf_render_quality", "high"))
        form.addRow("Default fit mode:", self.pdf_fit_combo)
        form.addRow("Render quality:", self.pdf_quality_combo)
        return w

    def _build_vault_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self.vault_show_all = QCheckBox("Show all files in vault (not just documents)")
        self.vault_show_all.setChecked(self.settings.get("vault_show_all_files", False))
        form.addRow(self.vault_show_all)
        paths = self.settings.get("vault_paths", [])
        paths_label = QLabel("\n".join(paths) if paths else "(no vaults open)")
        paths_label.setWordWrap(True)
        paths_label.setStyleSheet("color: #aaa; font-size: 12px;")
        form.addRow("Open vaults:", paths_label)
        return w

    def _build_web_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self.web_url_input = QLineEdit()
        self.web_url_input.setPlaceholderText("https://example.com")
        self.web_url_input.setText(self.settings.get("web_url", DEFAULT_SETTINGS["web_url"]))
        form.addRow("Default URL for new tabs:", self.web_url_input)
        tab_count = len(self.settings.get("web_tabs", DEFAULT_WEB_TABS))
        form.addRow("Saved web tabs:", QLabel(str(tab_count)))
        return w

    def _save(self):
        self.settings = load_settings()
        self.settings.update({
            "autosave_enabled": self.autosave_check.isChecked(),
            "autosave_interval_seconds": self.interval_spin.value(),
            "markdown_default_mode": self.md_mode_combo.currentText(),
            "markdown_icon_size": self.md_icon_spin.value(),
            "pdf_fit_mode": self.pdf_fit_combo.currentText(),
            "pdf_render_quality": self.pdf_quality_combo.currentText(),
            "vault_show_all_files": self.vault_show_all.isChecked(),
            "web_url": self.web_url_input.text().strip() or DEFAULT_SETTINGS["web_url"],
        })
        save_settings(self.settings)
        self.accept()

    def get_settings(self):
        return self.settings
