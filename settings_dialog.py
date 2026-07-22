from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QSpinBox, QPushButton, QFormLayout, QTabWidget,
    QComboBox, QWidget, QListWidget, QFileDialog
)
from PySide6.QtCore import QEvent, Qt

from settings import load_settings, save_settings, DEFAULT_SETTINGS, DEFAULT_WEB_TABS
from theme import (
    MARKDOWN_ICON_SIZE_MIN, MARKDOWN_ICON_SIZE_MAX,
    resolve_markdown_icon_size,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(520, 420)
        self.settings = load_settings()
        # Close (reject / keep existing settings) when window loses focus
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setWindowModality(Qt.ApplicationModal)

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
        self.launch_combo = QComboBox()
        self.launch_combo.addItems(["remembered", "maximized", "default"])
        self.launch_combo.setCurrentText(self.settings.get("launch_behavior", "remembered"))
        form.addRow("Launch window size:", self.launch_combo)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["blue", "purple", "green"])
        self.theme_combo.setCurrentText(self.settings.get("theme_accent", "blue"))
        form.addRow("Theme accent color:", self.theme_combo)

        self.autosave_check = QCheckBox("Enable background auto-save to file")
        self.autosave_check.setChecked(self.settings.get("autosave_enabled", True))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(2, 300)
        self.interval_spin.setSuffix(" sec")
        self.interval_spin.setValue(self.settings.get("autosave_interval_seconds", 5))
        form.addRow(self.autosave_check)
        form.addRow("Auto-save interval:", self.interval_spin)

        self.draft_autosave_check = QCheckBox("Enable draft recovery buffer (power-loss safety net)")
        self.draft_autosave_check.setChecked(self.settings.get("draft_autosave_enabled", True))
        form.addRow(self.draft_autosave_check)
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

        folder_layout = QHBoxLayout()
        self.save_folder_input = QLineEdit()
        self.save_folder_input.setText(self.settings.get("default_save_folder", ""))
        self.save_folder_input.setPlaceholderText("(Current Working Directory)")
        browse_btn = QPushButton("Browse...")
        def _browse():
            from PySide6.QtWidgets import QFileDialog
            folder = QFileDialog.getExistingDirectory(self, "Select Default Save Folder")
            if folder:
                self.save_folder_input.setText(folder)
        browse_btn.clicked.connect(_browse)
        folder_layout.addWidget(self.save_folder_input)
        folder_layout.addWidget(browse_btn)
        form.addRow("Default Save Folder:", folder_layout)

        self.vault_list = QListWidget()
        paths = self.settings.get("vault_paths", [])
        self.vault_list.addItems(paths)
        
        vault_controls = QVBoxLayout()
        btn_add = QPushButton("Add...")
        btn_edit = QPushButton("Edit...")
        btn_remove = QPushButton("Remove")
        
        def _add_vault():
            folder = QFileDialog.getExistingDirectory(self, "Select Vault Folder")
            if folder:
                self.vault_list.addItem(folder)
                
        def _edit_vault():
            current = self.vault_list.currentItem()
            if current:
                folder = QFileDialog.getExistingDirectory(self, "Select Vault Folder", current.text())
                if folder:
                    current.setText(folder)
                    
        def _remove_vault():
            row = self.vault_list.currentRow()
            if row >= 0:
                self.vault_list.takeItem(row)
                
        btn_add.clicked.connect(_add_vault)
        btn_edit.clicked.connect(_edit_vault)
        btn_remove.clicked.connect(_remove_vault)
        
        vault_controls.addWidget(btn_add)
        vault_controls.addWidget(btn_edit)
        vault_controls.addWidget(btn_remove)
        vault_controls.addStretch()
        
        vault_layout = QHBoxLayout()
        vault_layout.addWidget(self.vault_list)
        vault_layout.addLayout(vault_controls)
        
        form.addRow("Open vaults:", vault_layout)
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
        vaults = []
        for i in range(self.vault_list.count()):
            vaults.append(self.vault_list.item(i).text())
            
        self.settings.update({
            "launch_behavior": self.launch_combo.currentText(),
            "theme_accent": self.theme_combo.currentText(),
            "autosave_enabled": self.autosave_check.isChecked(),
            "autosave_interval_seconds": self.interval_spin.value(),
            "draft_autosave_enabled": self.draft_autosave_check.isChecked(),
            "markdown_default_mode": self.md_mode_combo.currentText(),
            "markdown_icon_size": self.md_icon_spin.value(),
            "pdf_fit_mode": self.pdf_fit_combo.currentText(),
            "pdf_render_quality": self.pdf_quality_combo.currentText(),
            "vault_show_all_files": self.vault_show_all.isChecked(),
            "default_save_folder": self.save_folder_input.text().strip(),
            "web_url": self.web_url_input.text().strip() or DEFAULT_SETTINGS["web_url"],
            "vault_paths": vaults,
        })
        save_settings(self.settings)
        self.accept()

    def get_settings(self):
        return self.settings
