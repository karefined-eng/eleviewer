import os
import tempfile
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
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
