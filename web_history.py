import json
from datetime import datetime
from paths import APP_DATA_DIR

HISTORY_FILE = APP_DATA_DIR / "web_history.json"
MAX_HISTORY_ITEMS = 500

def _load_history_data():
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_history_data(data):
    try:
        # Atomic write pattern per Rule 5
        import tempfile
        import os
        from save_utils import atomic_write
        atomic_write(str(HISTORY_FILE), json.dumps(data, indent=2))
    except Exception:
        pass

def add_to_history(url, title=""):
    if not url or url.startswith("devtools://") or url == "about:blank":
        return
        
    history = _load_history_data()
    
    # Remove existing entry if it exists (so we can move it to the top)
    history = [item for item in history if item.get("url") != url]
    
    history.insert(0, {
        "url": url,
        "title": title or url,
        "timestamp": datetime.now().isoformat()
    })
    
    if len(history) > MAX_HISTORY_ITEMS:
        history = history[:MAX_HISTORY_ITEMS]
        
    _save_history_data(history)

def get_history(query=None, limit=20):
    history = _load_history_data()
    
    if not query:
        return history[:limit]
        
    query = query.lower()
    results = []
    for item in history:
        if query in item.get("title", "").lower() or query in item.get("url", "").lower():
            results.append(item)
            if len(results) >= limit:
                break
    return results
