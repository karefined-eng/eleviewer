#!/usr/bin/env python3
# Run after PyInstaller build to generate verifiable release hash
"""
EleViewer Release Hash Generator
Run after PyInstaller build: python release_hash.py
Outputs: dist/EleViewer_SHA256.txt
"""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

import sys

# Find the installer executable
setup_files = list(Path("dist").glob("EleViewer_Setup_v*.exe"))
if not setup_files:
    print("ERROR: No installer found in dist/. Run Inno Setup first.")
    exit(1)

EXE_PATH = setup_files[0]
OUTPUT_PATH = Path("dist/EleViewer_Setup_SHA256.txt")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

if __name__ == "__main__":
    if not EXE_PATH.exists():
        print(f"ERROR: {EXE_PATH} not found.")
        exit(1)

    digest = sha256_file(EXE_PATH)
    size_mb = EXE_PATH.stat().st_size / (1024 * 1024)

    manifest = {
        "file": EXE_PATH.name,
        "sha256": digest,
        "size_mb": round(size_mb, 2),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    OUTPUT_PATH.write_text(
        f"SHA-256: {digest}\n"
        f"File: {EXE_PATH.name}\n"
        f"Size: {size_mb:.2f} MB\n"
        f"Generated: {manifest['generated_at']}\n",
        encoding="utf-8"
    )
    print(f"✓ Hash written to {OUTPUT_PATH}")
    print(f"  SHA-256: {digest}")
