"""Apply the final sidebar customization to the verified baseline build."""

import hashlib
import json
from pathlib import Path
import shutil


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def apply_customizations(output, root):
    recipes = json.loads((root / "customizations/mods.json").read_text(encoding="utf-8"))
    for recipe in recipes:
        relative = Path(recipe["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Invalid customization path: {relative}")
        path = output / relative
        text = path.read_text(encoding="utf-8")
        if digest(text) != recipe["base_sha256"]:
            raise ValueError(f"Customization baseline mismatch: {relative}")
        lines = text.splitlines(keepends=True)
        previous = len(lines)
        for edit in reversed(recipe["edits"]):
            start, end = edit["start"], edit["end"]
            if not (0 <= start <= end <= previous):
                raise ValueError(f"Invalid customization range: {relative}")
            lines[start:end] = [edit["text"]]
            previous = start
        result = "".join(lines)
        if digest(result) != recipe["result_sha256"]:
            raise ValueError(f"Customization result mismatch: {relative}")
        path.write_text(result, encoding="utf-8")
    shutil.copytree(root / "customizations/mods", output / "mods", dirs_exist_ok=True)
