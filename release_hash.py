#!/usr/bin/env python3
# Run after a Nuitka build or installer packaging step to generate a verifiable release hash.
"""
EleViewer Release Hash Generator
Run after the packaged executable is available: python release_hash.py
Outputs: dist/EleViewer_SHA256.txt
"""
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUTPUT_PATH = Path("dist/EleViewer_SHA256.txt")


def find_release_artifact() -> Path:
    installer_candidates = sorted(Path("dist").glob("EleViewer_Setup_v*.exe"))
    if installer_candidates:
        return installer_candidates[-1]

    portable_exe = Path("dist/EleViewer.exe")
    if portable_exe.exists():
        return portable_exe

    raise FileNotFoundError(
        "No release artifact found. Build the Nuitka app first or produce an installer in dist/."
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    try:
        release_artifact = find_release_artifact()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        exit(1)

    digest = sha256_file(release_artifact)
    size_mb = release_artifact.stat().st_size / (1024 * 1024)

    manifest = {
        "file": release_artifact.name,
        "sha256": digest,
        "size_mb": round(size_mb, 2),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    OUTPUT_PATH.write_text(
        f"SHA-256: {digest}\n"
        f"File: {release_artifact.name}\n"
        f"Size: {size_mb:.2f} MB\n"
        f"Generated: {manifest['generated_at']}\n",
        encoding="utf-8"
    )
    print(f"✓ Hash written to {OUTPUT_PATH}")
    print(f"  SHA-256: {digest}")
