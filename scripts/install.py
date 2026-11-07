#!/usr/bin/env python3
"""Build the Warp customization from a pinned, separately obtained Noctua source."""

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from urllib.request import urlopen

try:
    import tomllib
except ImportError:
    sys.exit("Erro: o instalador requer Python 3.11 ou posterior para validar TOML.")

from style import PARTS, apply, apply_titles
from customize import apply_customizations

ROOT = Path(__file__).resolve().parent.parent


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def obtain_source(metadata, destination, local=None):
    """Read only the allowlisted regular files, verifying every input hash."""
    archive = None
    if local is None:
        url = (f"https://codeload.github.com/{metadata['repository']}/tar.gz/"
               f"{metadata['revision']}")
        print(f"Obtendo Noctua: {metadata['revision']}")
        with urlopen(url, timeout=60) as response:
            data = response.read(32 * 1024 * 1024 + 1)
        if len(data) > 32 * 1024 * 1024:
            raise ValueError("O arquivo de dependência excede o limite de tamanho.")
        archive = tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")
    try:
        for relative, expected in metadata["files"].items():
            if Path(relative).is_absolute() or ".." in Path(relative).parts:
                raise ValueError(f"Caminho inválido: {relative}")
            if local is not None:
                source = local / relative
                if source.is_symlink() or not source.is_file():
                    raise ValueError(f"Dependência ausente ou inválida: {relative}")
                payload = source.read_bytes()
            else:
                prefix = f"noctua-layout-{metadata['revision']}/"
                member = archive.getmember(prefix + relative)
                if not member.isfile() or member.size > 4 * 1024 * 1024:
                    raise ValueError(f"Entrada inválida: {relative}")
                with archive.extractfile(member) as stream:
                    payload = stream.read()
            if hashlib.sha256(payload).hexdigest() != expected:
                raise ValueError(f"Noctua não corresponde à revisão esperada: {relative}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    finally:
        if archive is not None:
            archive.close()


def node(tree, identifier):
    if tree.get("id") == identifier:
        return tree
    for child in tree.get("children", []):
        result = node(child, identifier)
        if result is not None:
            return result
    return None


def make_layout(source, version):
    tree = load_json(source / "layouts/noctua.json")
    tree = json.loads(json.dumps(tree).replace('"noctua-', '"warp-'))
    tree.update(cloned_from={"name": "noctua", "version": version},
                theme="warp-gruvbox", font="JetBrainsMono Nerd Font", font_size=13,
                terminal_opacity=0.84, ui_font="Roboto", preview="layouts/warp-gruvbox.svg")
    for identifier, pixels in {"sidebar": 248, "brand": 68, "tabs": 36,
                               "sidebar-footer": 32, "status": 24}.items():
        node(tree, identifier)["size"] = {"px": pixels}
    node(tree, "work-body")["gap"] = 4
    node(tree, "status")["hidden"] = True
    pane = node(tree, "main")["content"]["pane"]
    pane.update(gap=4, radius=4, background="canvas", lone=False,
                border={"width": 1, "color": "border"},
                focus={"width": 1, "color": "border"})
    pane["header"].update(height=24, reveal="hover")
    return tree


def build(source, output, metadata):
    for part in PARTS:
        original = source / "mods" / f"noctua-{part}"
        target = output / "mods" / f"warp-{part}"
        shutil.copytree(original, target)
        manifest = load_json(target / "mod.json")
        manifest["cloned_from"] = {"name": f"noctua-{part}",
                                   "version": metadata["herdr_version"]}
        write_json(target / "mod.json", manifest)
    apply(output, ROOT / "assets/warp")
    apply_titles(output)
    apply_customizations(output, ROOT)
    shutil.copy2(ROOT / "licenses/Warp-AGPL-3.0.txt",
                 output / "mods/warp-chrome/LICENSE-Warp-AGPL-3.0.txt")
    shutil.copytree(ROOT / "fonts", output / "fonts")
    shutil.copytree(ROOT / "themes", output / "themes")
    shutil.copytree(ROOT / "licenses", output / "licenses/herdr-warp")
    write_json(output / "layouts/warp-gruvbox.json",
               make_layout(source, metadata["herdr_version"]))
    shutil.copy2(ROOT / "layouts/warp-gruvbox.svg", output / "layouts/warp-gruvbox.svg")


def prepare_keys(home, output):
    path = home / "keys.json"
    keys = load_json(path) if path.exists() else {}
    if not isinstance(keys, dict) or not isinstance(keys.get("terminal", {}), dict):
        raise ValueError("keys.json precisa conter um objeto e uma seção terminal válida.")
    keys.setdefault("terminal", {})["ctrl-v"] = "terminal.paste"
    write_json(output / "keys.json", keys)


def disable_notes(text):
    """Change only the root notes boolean, preserving the rest of the TOML text."""
    import re

    original = tomllib.loads(text)
    if "notes" in original and type(original["notes"]) is not bool:
        raise ValueError("herdr-core/config.toml: notes precisa ser true ou false.")
    if original.get("notes") is False:
        return text
    expected = dict(original, notes=False)
    if "notes" not in original:
        result = "notes = false\n" + text
        if tomllib.loads(result) == expected:
            return result
    else:
        # Validate each candidate against the whole document: assignments inside
        # tables or multiline strings must never be mistaken for the root key.
        pattern = r"(?m)^([^\r\n]*?=[ \t]*)true(?=[ \t]*(?:#[^\r\n]*)?\r?$)"
        for match in re.finditer(pattern, text):
            try:
                if tomllib.loads(match.group(1) + "true") != {"notes": True}:
                    continue
                start = match.end() - len("true")
                result = text[:start] + "false" + text[match.end():]
                if tomllib.loads(result) == expected:
                    return result
            except tomllib.TOMLDecodeError:
                continue
    raise ValueError("Não foi possível alterar somente notes em herdr-core/config.toml.")


def check_target(target, home):
    if target.is_symlink() or any(parent.is_symlink() for parent in target.parents
                                  if parent != home.parent and home in parent.parents):
        raise ValueError(f"Destino contém link simbólico: {target}")
    if target.exists() and not target.is_file():
        raise ValueError(f"Destino não é um arquivo: {target}")


def install(output, home, dry_run=False, core_home=None):
    files = sorted(path for path in output.rglob("*") if path.is_file())
    for path in files:
        target = home / path.relative_to(output)
        check_target(target, home)
    core = None
    if core_home is not None:
        core_path = core_home / "config.toml"
        if any(parent.is_symlink() for parent in (core_path, *core_path.parents)):
            raise ValueError(f"Destino contém link simbólico: {core_path}")
        check_target(core_path, core_home)
        previous = core_path.read_bytes() if core_path.exists() else b""
        updated = disable_notes(previous.decode("utf-8")).encode("utf-8")
        if updated != previous:
            mode = stat.S_IMODE(core_path.stat().st_mode) if core_path.exists() else 0o600
            core = (core_path, updated, mode)
    if dry_run:
        print(f"Dry run: {len(files)} arquivos seriam instalados em {home}:")
        for path in files:
            print(f"  {path.relative_to(output)}")
        if core_home is not None:
            action = "definir notes = false" if core else "notes já está false; preservar"
            print(f"Core: {core_home / 'config.toml'} — {action}")
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = home / "backups" / f"herdr-warp-{stamp}"
    backup.mkdir(parents=True, mode=0o700)
    manifest = {"home": str(home), "previous": [], "new": []}
    # Complete the backup before changing any destination file.
    for path in files:
        relative = path.relative_to(output)
        target = home / relative
        if target.exists():
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
            manifest["previous"].append(str(relative))
        else:
            manifest["new"].append(str(relative))
    if core:
        core_path, payload, mode = core
        saved = None
        if core_path.exists():
            saved = "core/config.toml"
            (backup / "core").mkdir()
            shutil.copy2(core_path, backup / saved)
        manifest["core"] = {"path": str(core_path), "previous": saved}
    write_json(backup / "manifest.json", manifest)
    writes = [(home / path.relative_to(output), path.read_bytes(), 0o644) for path in files]
    if core:
        writes.append(core)
    for target, payload, mode in writes:
        target.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replacement of each file avoids partial reads by Herdr's watcher.
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".herdr-warp-",
                                         delete=False) as temporary:
            temporary.write(payload)
            temporary_path = Path(temporary.name)
        temporary_path.chmod(mode)
        temporary_path.replace(target)
    print(f"Instalados {len(files)} arquivos em {home}")
    print(f"Backup: {backup}")
    if core_home is not None:
        print(f"Mensagens automáticas desativadas: {core_home / 'config.toml'} (notes = false)")
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path,
                        default=Path(os.environ.get("HERDR_APP_HOME", "~/.config/herdr-app")).expanduser())
    parser.add_argument("--core-home", type=Path,
                        default=Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser() / "herdr-core",
                        help="Diretório do core para definir notes = false (padrão: XDG_CONFIG_HOME/herdr-core ou ~/.config/herdr-core)")
    parser.add_argument("--noctua-source", type=Path, help="Cópia local da revisão Noctua fixada")
    parser.add_argument("--dry-run", action="store_true", help="Validar e listar sem alterar o destino")
    parser.add_argument("--ctrl-v", action="store_true", help="Mesclar somente Ctrl+V → colar em keys.json")
    parser.add_argument("--activate", action="store_true", help="Ativar o layout após instalar")
    args = parser.parse_args()
    args.home = args.home.expanduser().resolve()
    args.core_home = args.core_home.expanduser().absolute()
    if args.activate and not args.dry_run and not shutil.which("herdr-app"):
        parser.error("--activate requer herdr-app no PATH e uma janela aberta.")
    metadata = load_json(ROOT / "upstream.json")
    with tempfile.TemporaryDirectory(prefix="herdr-warp-") as directory:
        work = Path(directory)
        source, output = work / "source", work / "output"
        obtain_source(metadata, source, args.noctua_source)
        build(source, output, metadata)
        if args.ctrl_v:
            prepare_keys(args.home, output)
        install(output, args.home, args.dry_run, core_home=args.core_home)
    if args.activate and not args.dry_run:
        environment = dict(os.environ, HERDR_APP_HOME=str(args.home))
        subprocess.run(["herdr-app", "do", "layout.switch", "--name", "warp-gruvbox"],
                       env=environment, check=True)
    elif not args.dry_run:
        print("Para ativar: herdr-app do layout.switch --name warp-gruvbox")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, tarfile.TarError, subprocess.CalledProcessError) as error:
        sys.exit(f"Erro: {error}")
