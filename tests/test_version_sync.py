import json
import tempfile
import unittest
from pathlib import Path

from version_sync import normalize_version, sync_package_versions


class VersionSyncTests(unittest.TestCase):
    def test_normalize_version_strips_v_prefix(self):
        self.assertEqual(normalize_version("v1.2.3"), "1.2.3")
        self.assertEqual(normalize_version("1.2.3"), "1.2.3")

    def test_sync_package_versions_updates_both_manifests(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            package_json = root / "package.json"
            site_package_json = root / "site" / "package.json"
            site_package_json.parent.mkdir(parents=True, exist_ok=True)

            package_json.write_text(json.dumps({"name": "app", "version": "0.0.0"}), encoding="utf-8")
            site_package_json.write_text(json.dumps({"name": "site", "version": "0.0.0"}), encoding="utf-8")

            synced = sync_package_versions(root, "1.2.3")

            self.assertEqual(synced, "1.2.3")
            self.assertEqual(json.loads(package_json.read_text(encoding="utf-8"))["version"], "1.2.3")
            self.assertEqual(json.loads(site_package_json.read_text(encoding="utf-8"))["version"], "1.2.3")


if __name__ == "__main__":
    unittest.main()
