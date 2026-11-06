#!/usr/bin/env python3
"""Install the optional AGY title helper without changing other settings."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile


def configure(home, dry_run=False):
    home = home.expanduser().resolve()
    settings, script = home / "settings.json", home / "title.py"
    original = json.loads(settings.read_text(encoding="utf-8")) if settings.exists() else {}
    if not isinstance(original, dict):
        raise ValueError("settings.json precisa conter um objeto JSON.")
    updated = dict(original)
    updated["title"] = {"type": "command", "command": str(script), "enabled": True}
    if dry_run:
        print(f"Seriam instalados {script} e somente a chave title em {settings}.")
        return None
    home.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = home / "backups" / f"herdr-warp-title-{stamp}"
    backup.mkdir(parents=True, mode=0o700)
    for target in (settings, script):
        if target.exists():
            shutil.copy2(target, backup / target.name)
    source = Path(__file__).with_name("title.py")
    for target, payload, mode in [
        (script, source.read_bytes(), 0o755),
        (settings, (json.dumps(updated, ensure_ascii=False, indent=2) + "\n").encode(),
         stat.S_IMODE(settings.stat().st_mode) if settings.exists() else 0o600),
    ]:
        with tempfile.NamedTemporaryFile(dir=home, prefix=".herdr-warp-title-", delete=False) as temporary:
            temporary.write(payload)
            temporary_path = Path(temporary.name)
        temporary_path.chmod(mode)
        temporary_path.replace(target)
    print(f"Configurado. Backup: {backup}")
    print("Na sessão AGY aberta, execute diretamente: /title on")
    return backup


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home() / ".gemini/antigravity-cli")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    configure(args.home, args.dry_run)
