#!/usr/bin/env python3
import re, json, sys, pathlib

root = pathlib.Path(".")
with open("scripts/scrub_map.json") as f:
    rules = [(re.compile(k), v) for k,v in json.load(f).items()]

def should_edit(p: pathlib.Path) -> bool:
    if p.is_dir(): return False
    s = str(p)
    if any(s.startswith(x) for x in ["results", "release", "archive"]): return False
    if p.suffix.lower() in [".md", ".py", ".json", ".txt", ".yml", ".yaml"]:
        return True
    return False

changed = 0
for p in root.rglob("*"):
    if not should_edit(p): continue
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except:
        continue
    orig = text
    for rx, rep in rules:
        text = rx.sub(rep, text)
    if text != orig:
        p.write_text(text, encoding="utf-8")
        print(f"SCRUBBED {p}")
        changed += 1
print(f"Files changed: {changed}")