import json
from pathlib import Path
from typing import Iterable


def normalize_version(version: str) -> str:
    version = version.strip()
    if version.startswith("v") or version.startswith("V"):
        version = version[1:]
    return version


def sync_package_versions(root: str | Path, version: str) -> str:
    normalized = normalize_version(version)
    root_path = Path(root)

    package_files = [
        root_path / "package.json",
        root_path / "site" / "package.json",
    ]

    for package_file in package_files:
        if not package_file.exists():
            continue
        data = json.loads(package_file.read_text(encoding="utf-8"))
        data["version"] = normalized
        package_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    return normalized


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Synchronize package versions")
    parser.add_argument("version", nargs="?", default="1.0.0")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    sync_package_versions(args.root, args.version)
    print(f"Synchronized version to {args.version}")
