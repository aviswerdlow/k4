from pathlib import Path
import hashlib
import json

def read_text(p: str) -> str:
    return Path(p).read_text(encoding="utf-8")

def write_text(p: str, s: str) -> None:
    Path(p).write_text(s, encoding="utf-8")

def read_json(p: str) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))

def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def list_files_recursive(root: Path):
    return [p for p in root.rglob("*") if p.is_file()]