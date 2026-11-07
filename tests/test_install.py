import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import tomllib
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from install import disable_notes, install, obtain_source, prepare_keys


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

    def test_disable_notes_preserves_toml_comments_sections_and_multiline_strings(self):
        original = ('# Core preferences\r\n'
                    'description = """example:\r\nnotes = true\r\n"""\r\n'
                    '"notes" = true  # automatic messages\r\n'
                    'shell = ["bash", "-l"]\r\n'
                    '[custom]\r\nnotes = true\r\n')
        expected = original.replace('"notes" = true', '"notes" = false')
        self.assertEqual(disable_notes(original), expected)
        self.assertEqual(tomllib.loads(expected)["custom"]["notes"], True)

    def test_missing_notes_is_added_at_root_and_false_is_idempotent(self):
        for original in ['', '# comment\n[custom]\nnotes = true\n']:
            with self.subTest(original=original):
                updated = disable_notes(original)
                self.assertEqual(updated, 'notes = false\n' + original)
                self.assertEqual(disable_notes(updated), updated)
        quoted = '"\\u006eotes" = true # escaped key\n'
        self.assertEqual(disable_notes(quoted), quoted.replace('true', 'false'))

    def test_core_config_backup_permissions_and_unrelated_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output, home, core = root / 'output', root / 'app', root / 'core'
            output.mkdir()
            core.mkdir()
            (output / 'example.json').write_text('{}')
            config = core / 'config.toml'
            original = '# keep this comment\nnotes = true\nhistory_mb = 12\n'
            config.write_text(original)
            config.chmod(0o600)
            with contextlib.redirect_stdout(io.StringIO()):
                backup = install(output, home, core_home=core)
            self.assertEqual(config.read_text(), original.replace('true', 'false'))
            self.assertEqual(config.stat().st_mode & 0o777, 0o600)
            self.assertEqual((backup / 'core/config.toml').read_text(), original)
            manifest = json.loads((backup / 'manifest.json').read_text())
            self.assertEqual(manifest['core'], {'path': str(config), 'previous': 'core/config.toml'})
            self.assertEqual(backup.stat().st_mode & 0o777, 0o700)
            with contextlib.redirect_stdout(io.StringIO()):
                again = install(output, home, core_home=core)
            self.assertNotIn('core', json.loads((again / 'manifest.json').read_text()))

    def test_core_dry_run_does_not_create_or_modify_either_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output, home, core = root / 'output', root / 'app', root / 'core'
            output.mkdir()
            (output / 'example.json').write_text('{}')
            with contextlib.redirect_stdout(io.StringIO()):
                install(output, home, dry_run=True, core_home=core)
            self.assertFalse(home.exists())
            self.assertFalse(core.exists())
            core.mkdir()
            config = core / 'config.toml'
            config.write_text('notes = true\n')
            with contextlib.redirect_stdout(io.StringIO()):
                install(output, home, dry_run=True, core_home=core)
            self.assertEqual(config.read_text(), 'notes = true\n')
            self.assertFalse(home.exists())

    def test_missing_core_config_is_created_with_manifest_for_reversal(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output, home, core = root / 'output', root / 'app', root / 'core'
            output.mkdir()
            with contextlib.redirect_stdout(io.StringIO()):
                backup = install(output, home, core_home=core)
            config = core / 'config.toml'
            self.assertEqual(config.read_text(), 'notes = false\n')
            self.assertEqual(config.stat().st_mode & 0o777, 0o600)
            self.assertIsNone(json.loads((backup / 'manifest.json').read_text())['core']['previous'])

    def test_invalid_core_or_symlink_stops_before_app_writes(self):
        for text in ['notes = invalid\n', 'notes = "true"\n']:
            with self.subTest(text=text), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                output, home, core = root / 'output', root / 'app', root / 'core'
                output.mkdir()
                core.mkdir()
                config = core / 'config.toml'
                config.write_text(text)
                with self.assertRaises(ValueError):
                    install(output, home, core_home=core)
                self.assertFalse(home.exists())
                self.assertEqual(config.read_text(), text)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output, home, core, outside = root / 'output', root / 'app', root / 'core', root / 'outside'
            output.mkdir()
            outside.mkdir()
            (outside / 'config.toml').write_text('notes = true\n')
            core.symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'link simbólico'):
                install(output, home, core_home=core)
            self.assertFalse(home.exists())
            self.assertEqual((outside / 'config.toml').read_text(), 'notes = true\n')


if __name__ == "__main__":
    unittest.main()
