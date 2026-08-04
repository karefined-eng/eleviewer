import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from quick_switcher import QuickSwitcher

def get_app():
    return QApplication.instance() or QApplication([])

def test_quick_switcher_initialization():
    app = get_app()
    recent = ["C:/doc1.txt", "C:/doc2.md"]
    pinned = ["C:/important.pdf"]
    open_tabs = ["C:/doc1.txt"]
    
    qs = QuickSwitcher(recent, pinned, open_tabs)
    assert qs.file_list.count() == 6

def test_quick_switcher_fuzzy_search():
    app = get_app()
    recent = ["C:/my_secret_doc.txt", "C:/hello_world.md"]
    qs = QuickSwitcher(recent, [], [])
    qs.bookmarks = [] # Prevent local state contamination
    
    qs.search_input.setText("msd")
    qs._do_search()
    assert any("my_secret_doc.txt" in qs.file_list.item(i).text() for i in range(qs.file_list.count()))
    
    qs.search_input.setText("hlw")
    qs._do_search()
    assert any("hello_world.md" in qs.file_list.item(i).text() for i in range(qs.file_list.count()))
    
    qs.search_input.setText("zzz_impossible_match")
    qs._do_search()
    assert not any("zzz_impossible_match" in qs.file_list.item(i).text() for i in range(qs.file_list.count()))

def test_quick_switcher_selection():
    app = get_app()
    recent = ["C:/doc1.txt", "C:/doc2.md"]
    qs = QuickSwitcher(recent, [], [])
    
    qs.search_input.setText("doc2")
    qs._do_search()
    qs.file_list.setCurrentRow(0)
    
    selected_path = None
    def on_selected(path):
        nonlocal selected_path
        selected_path = path
        
    qs.file_selected.connect(on_selected)
    qs.select_current()
    
    assert selected_path == "C:/doc2.md"

