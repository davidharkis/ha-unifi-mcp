import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import yaml

spec = importlib.util.spec_from_file_location("update", Path(__file__).resolve().parents[1] / "scripts/update.py")
update = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update)


class UpdateTests(unittest.TestCase):
    def test_only_stable_non_yanked_newer_versions_are_advertised(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / "unifi_network_mcp"
            app.mkdir()
            (app / "config.yaml").write_text("name: Test\nversion: 1.0.0-1\n")
            (app / "requirements.txt").write_text("unifi-network-mcp==1.0.0\n")
            (app / "CHANGELOG.md").write_text("## Initial\n")
            releases = {"releases": {"1.0.0": [{}], "1.1.0": [{}], "2.0.0rc1": [{}],
                                     "3.0.0": [{"yanked": True}], "4.0.0": []}}
            with patch.object(update, "ROOT", root), patch.object(update.urllib.request, "urlopen",
                    return_value=io.BytesIO(json.dumps(releases).encode())), patch.dict("os.environ", {"GITHUB_OUTPUT": str(root / "output")}):
                update.main()
            self.assertEqual(yaml.safe_load((app / "config.yaml").read_text())["version"], "1.1.0-1")
            self.assertEqual((app / "requirements.txt").read_text(), "unifi-network-mcp==1.1.0\n")
            self.assertIn("changed=true", (root / "output").read_text())

    def test_network_failure_leaves_release_files_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / "unifi_network_mcp"
            app.mkdir()
            config = "version: 1.0.0-1\n"
            (app / "config.yaml").write_text(config)
            (app / "requirements.txt").write_text("unifi-network-mcp==1.0.0\n")
            with patch.object(update, "ROOT", root), patch.object(update.urllib.request, "urlopen", side_effect=OSError("offline")):
                with self.assertRaises(OSError):
                    update.main()
            self.assertEqual((app / "config.yaml").read_text(), config)
