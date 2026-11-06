import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from install import install, obtain_source, prepare_keys


class InstallerTests(unittest.TestCase):
    def test_dry_run_does_not_create_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output, home = root / "output", root / "home"
            output.mkdir()
            (output / "example.json").write_text("{}")
            with contextlib.redirect_stdout(io.StringIO()):
                install(output, home, dry_run=True)
            self.assertFalse(home.exists())

    def test_backup_is_complete_and_unrelated_files_survive(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output, home = root / "output", root / "home"
            output.mkdir()
            home.mkdir()
            (output / "existing.json").write_text("new")
            (output / "added.json").write_text("added")
            (home / "existing.json").write_text("old")
            (home / "settings.json").write_text('{"zoom":1.2}')
            with contextlib.redirect_stdout(io.StringIO()):
                backup = install(output, home)
            self.assertEqual((backup / "existing.json").read_text(), "old")
            self.assertEqual((home / "existing.json").read_text(), "new")
            self.assertEqual((home / "settings.json").read_text(), '{"zoom":1.2}')
            manifest = json.loads((backup / "manifest.json").read_text())
            self.assertEqual(manifest["previous"], ["existing.json"])
            self.assertEqual(manifest["new"], ["added.json"])

    def test_ctrl_v_preserves_all_other_bindings(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            home, output = root / "home", root / "output"
            home.mkdir()
            original = {"global": {"ctrl-t": "tab.new"},
                        "terminal": {"ctrl-v": "terminal.paste_image", "ctrl-c": "send:ctrl-c"}}
            (home / "keys.json").write_text(json.dumps(original))
            prepare_keys(home, output)
            expected = json.loads(json.dumps(original))
            expected["terminal"]["ctrl-v"] = "terminal.paste"
            self.assertEqual(json.loads((output / "keys.json").read_text()), expected)
            self.assertEqual(json.loads((home / "keys.json").read_text()), original)

    def test_wrong_dependency_hash_stops_before_installation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source"
            source.mkdir()
            (source / "file.js").write_text("changed upstream")
            metadata = {"files": {"file.js": hashlib.sha256(b"expected").hexdigest()}}
            with self.assertRaisesRegex(ValueError, "revisão esperada"):
                obtain_source(metadata, root / "destination", source)
            self.assertFalse((root / "destination").exists())

    def test_symlink_destination_is_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            home, output, outside = root / "home", root / "output", root / "outside"
            for path in (home, output, outside):
                path.mkdir()
            (home / "mods").symlink_to(outside, target_is_directory=True)
            (output / "mods").mkdir()
            (output / "mods/example.js").write_text("example")
            with self.assertRaisesRegex(ValueError, "link simbólico"):
                install(output, home)
            self.assertFalse((outside / "example.js").exists())
            self.assertFalse((home / "backups").exists())


if __name__ == "__main__":
    unittest.main()
