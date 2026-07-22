import os
import json
import time
import hashlib
from pathlib import Path
from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QMessageBox

from paths import APP_DATA_DIR

DRAFTS_DIR = APP_DATA_DIR / "drafts"

class DraftManager(QObject):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.snapshot_all)
        
        from settings import load_settings
        settings = load_settings()
        if settings.get("draft_autosave_enabled", True):
            interval = settings.get("draft_autosave_interval_seconds", 60)
            self.timer.start(interval * 1000)

    def snapshot_all(self):
        if not self.main_window:
            return
            
        tabs = self.main_window.tabs
        for i in range(tabs.count()):
            editor = tabs.widget(i)
            if getattr(editor, "is_modified", False) and hasattr(editor, "toPlainText"):
                path = getattr(editor, "file_path", None)
                tab_title = tabs.tabText(i)
                content = editor.toPlainText()
                
                stable_id = path if path else f"untitled_{id(editor)}"
                file_hash = hashlib.md5(stable_id.encode()).hexdigest()
                
                draft_path = DRAFTS_DIR / f"{file_hash}.draft.txt"
                meta_path = DRAFTS_DIR / f"{file_hash}.draft.meta.json"
                
                # atomic writes
                temp_txt = draft_path.with_suffix(".txt.tmp")
                with open(temp_txt, "w", encoding="utf-8") as f:
                    f.write(content)
                os.replace(temp_txt, draft_path)
                
                temp_meta = meta_path.with_suffix(".json.tmp")
                with open(temp_meta, "w", encoding="utf-8") as f:
                    json.dump({
                        "original_path": path,
                        "tab_title": tab_title,
                        "timestamp": time.time()
                    }, f)
                os.replace(temp_meta, meta_path)

    def cleanup(self, path=None, editor_id=None):
        if path:
            stable_id = path
        elif editor_id:
            stable_id = f"untitled_{editor_id}"
        else:
            return
            
        file_hash = hashlib.md5(stable_id.encode()).hexdigest()
        draft_path = DRAFTS_DIR / f"{file_hash}.draft.txt"
        meta_path = DRAFTS_DIR / f"{file_hash}.draft.meta.json"
        
        try:
            if draft_path.exists():
                draft_path.unlink()
            if meta_path.exists():
                meta_path.unlink()
        except Exception:
            pass

    def list_recoverable(self):
        recoverable = []
        for meta_file in DRAFTS_DIR.glob("*.draft.meta.json"):
            draft_file = meta_file.with_name(meta_file.name.replace(".meta.json", ".txt"))
            if not draft_file.exists():
                continue
                
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                recoverable.append({
                    "meta_path": meta_file,
                    "draft_path": draft_file,
                    "original_path": meta.get("original_path"),
                    "tab_title": meta.get("tab_title"),
                    "timestamp": meta.get("timestamp")
                })
            except Exception:
                pass
        return recoverable

    def check_and_recover(self):
        if not self.main_window:
            return
            
        recoverable = self.list_recoverable()
        if not recoverable:
            return
            
        open_paths = []
        for i in range(self.main_window.tabs.count()):
            editor = self.main_window.tabs.widget(i)
            p = getattr(editor, "file_path", None)
            if p:
                open_paths.append(p)
                
        to_recover = [r for r in recoverable if r["original_path"] not in open_paths]
        
        if not to_recover:
            return
            
        reply = QMessageBox.question(
            self.main_window, 
            "Draft Recovery", 
            f"Found {len(to_recover)} unsaved draft(s) from a previous session.\nWould you like to recover them?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from editor import EditorTab
            for r in to_recover:
                try:
                    with open(r["draft_path"], "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    editor = EditorTab()
                    if r["original_path"]:
                        editor.file_path = r["original_path"]
                        editor.setPlainText(content)
                        editor.is_modified = True
                        self.main_window._add_editor_tab(editor, os.path.basename(r["original_path"]) + " (Recovered)")
                    else:
                        editor.setPlainText(content)
                        editor.is_modified = True
                        self.main_window._add_editor_tab(editor, r["tab_title"] + " (Recovered)")
                        
                except Exception as e:
                    print(f"Failed to recover draft: {e}")
        
        # Cleanup all after asking
        for r in recoverable:
            try:
                r["draft_path"].unlink()
                r["meta_path"].unlink()
            except Exception:
                pass
