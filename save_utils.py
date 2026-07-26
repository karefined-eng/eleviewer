import os
import tempfile
import time
from pathlib import Path


def atomic_write(file_path, content):
    """
    Write content to file_path atomically via a temp file in the same directory.
    content: str (text) or bytes (binary).
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    mode = "wb" if isinstance(content, bytes) else "w"
    kwargs = {} if isinstance(content, bytes) else {"encoding": "utf-8"}

    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=".eleviewer_", suffix=".tmp")
    os.close(fd)
    try:
        with open(tmp_path, mode, **kwargs) as f:
            f.write(content)
        for attempt in range(5):
            try:
                os.replace(tmp_path, path)
                break
            except (PermissionError, OSError):
                if attempt == 4:
                    raise
                time.sleep(0.05 * (attempt + 1))
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        raise
