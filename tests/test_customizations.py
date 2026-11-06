import contextlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from customize import apply_customizations, digest

spec = importlib.util.spec_from_file_location("agy_title_install", ROOT / "integrations/antigravity/install.py")
agy_install = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agy_install)


class CustomizationTests(unittest.TestCase):
    def test_revision_guard_rejects_wrong_input_before_modification(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "customizations").mkdir()
            output = root / "output"
            output.mkdir()
            target = output / "main.js"
            target.write_text("unexpected\n")
            (root / "customizations/mods.json").write_text(json.dumps([
                {"path": "main.js", "base_sha256": digest("expected\n"), "edits": []}
            ]))
            with self.assertRaisesRegex(ValueError, "baseline mismatch"):
                apply_customizations(output, root)
            self.assertEqual(target.read_text(), "unexpected\n")

    def test_insertions_and_deletions_reproduce_verified_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "customizations/mods").mkdir(parents=True)
            output = root / "output"
            output.mkdir()
            (output / "main.js").write_text("first\nremoved\nlast\n")
            expected = "first\nlast\nadded\n"
            (root / "customizations/mods.json").write_text(json.dumps([
                {"path": "main.js", "base_sha256": digest("first\nremoved\nlast\n"),
                 "result_sha256": digest(expected), "edits": [
                     {"start": 1, "end": 2, "text": ""},
                     {"start": 3, "end": 3, "text": "added\n"},
                 ]}
            ]))
            (root / "customizations/mods/helper.js").write_text("helper\n")
            apply_customizations(output, root)
            self.assertEqual((output / "main.js").read_text(), expected)
            self.assertEqual((output / "mods/helper.js").read_text(), "helper\n")

    def test_agy_install_preserves_settings_permissions_and_backups(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder) / "agy"
            home.mkdir()
            original = {"theme": "custom", "statusLine": {"enabled": True}}
            settings = home / "settings.json"
            settings.write_text(json.dumps(original))
            settings.chmod(0o600)
            (home / "title.py").write_text("previous helper\n")
            with contextlib.redirect_stdout(io.StringIO()):
                backup = agy_install.configure(home)
            current = json.loads(settings.read_text())
            self.assertEqual({k: v for k, v in current.items() if k != "title"}, original)
            self.assertEqual(current["title"]["command"], str(home / "title.py"))
            self.assertEqual(stat.S_IMODE(settings.stat().st_mode), 0o600)
            self.assertEqual(json.loads((backup / "settings.json").read_text()), original)
            self.assertEqual((backup / "title.py").read_text(), "previous helper\n")

    def test_agy_dry_run_never_creates_target(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder) / "agy"
            with contextlib.redirect_stdout(io.StringIO()):
                agy_install.configure(home, dry_run=True)
            self.assertFalse(home.exists())

    def test_agy_title_uses_name_and_plain_fallback_without_logging_payload(self):
        for payload, expected in [
            ({"conversation_title": "Refinar layout", "email": "unused@example.com"}, "Refinar layout\n"),
            ({}, "Antigravity\n"),
            ({"conversation_title": "\n\t"}, "Antigravity\n"),
            ({"conversation_title": "Nome\ncom\tquebras\x07"}, "Nome com quebras\n"),
            ([], "Antigravity\n"),
        ]:
            result = subprocess.run([sys.executable, str(ROOT / "integrations/antigravity/title.py")],
                                    input=json.dumps(payload), text=True, capture_output=True, check=True)
            self.assertEqual(result.stdout, expected)
            self.assertEqual(result.stderr, "")
