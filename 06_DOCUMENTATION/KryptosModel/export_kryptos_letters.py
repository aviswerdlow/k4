# export_kryptos_letters.py
# Works in Blender 2.79–3.x. Exports per-letter data for the Kryptos screen.

import bpy, json, mathutils, os, re

# -------------------- CONFIG / HEURISTICS --------------------
OUTPUT_DIR = bpy.path.abspath("//")  # same folder as .blend

# Heuristic 1: object name carries letter and optional index, e.g. "K4_C_063" or "Letter_E_21"
NAME_PATTERNS = [
    re.compile(r".*[_\-]([A-Z\?])[_\-]?(\d+)?$"),     # last letter + optional digits
    re.compile(r"^([A-Z\?])(\d+)$"),                  # e.g. E21
]

# Heuristic 2: custom property 'char' on the object or a child text object with body
LOOK_FOR_CUSTOM_PROP = "char"

# Control which objects to include (likely the screen collection / name filter)
INCLUDE_NAME_SUBSTRINGS = ["Kryptos", "Screen", "Panel", "Letter", "K4"]  # adjust if needed

# Reading order: "serpentine" in rows, or "left_to_right"
READING_MODE = "serpentine"  # or "left_to_right"
ROW_TOL = 0.015  # merge letters into the same row if y within this (meters)
# -------------------------------------------------------------

def guess_letter_from_name(name):
    for pat in NAME_PATTERNS:
        m = pat.match(name.upper())
        if m:
            letter = m.group(1)
            if letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ?":
                idx = m.group(2)
                return letter, (int(idx) if idx and idx.isdigit() else None)
    return None, None

def guess_letter_from_props(obj):
    # custom property
    if LOOK_FOR_CUSTOM_PROP in obj.keys():
        v = str(obj[LOOK_FOR_CUSTOM_PROP]).upper()
        if len(v) == 1 and v in "ABCDEFGHIJKLMNOPQRSTUVWXYZ?":
            return v
    # child text object
    for child in obj.children:
        if child.type == 'FONT' and hasattr(child.data, "body"):
            body = str(child.data.body).strip().upper()
            if len(body) >= 1 and body[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ?":
                return body[0]
    return None

def world_normal(obj):
    # compute averaged normal from first polygon if mesh
    if obj.type != 'MESH' or not obj.data.polygons:
        return (0.0, 0.0, 1.0)
    poly = obj.data.polygons[0]
    n = poly.normal.copy()
    n_world = (obj.matrix_world.to_3x3() * n).normalized()
    return tuple(n_world)

def collect_letter_objs():
    letters = []
    for obj in bpy.data.objects:
        if obj.type not in {'MESH', 'FONT'}:
            continue
        # crude inclusion filter
        name_u = obj.name.upper()
        if not any(s.upper() in name_u for s in INCLUDE_NAME_SUBSTRINGS):
            continue

        # try name
        ch, idx_hint = guess_letter_from_name(obj.name)
        # try properties/text if needed
        if not ch:
            ch = guess_letter_from_props(obj)

        # only accept single-letter glyphs
        if ch and len(ch) == 1 and ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ?":
            loc = obj.matrix_world.translation
            nx, ny, nz = world_normal(obj)
            sx, sy, sz = obj.scale
            letters.append({
                "obj": obj,
                "obj_name": obj.name,
                "char": ch,
                "idx_hint": idx_hint,
                "x": float(loc.x),
                "y": float(loc.y),
                "z": float(loc.z),
                "nx": float(nx), "ny": float(ny), "nz": float(nz),
                "sx": float(sx), "sy": float(sy), "sz": float(sz),
                "collection": obj.users_collection[0].name if obj.users_collection else "",
            })
    return letters

def serpentine_sort(letters):
    # Group by Y into rows, then within each row sort by X; alternate left->right / right->left
    rows = []
    letters_sorted = sorted(letters, key=lambda d: d["y"], reverse=True)  # top to bottom
    for d in letters_sorted:
        placed = False
        for row in rows:
            if abs(row["y_ref"] - d["y"]) <= ROW_TOL:
                row["items"].append(d)
                row["y_values"].append(d["y"])
                placed = True
                break
        if not placed:
            rows.append({"y_ref": d["y"], "y_values":[d["y"]], "items":[d]})
    # refine y_ref by median
    for row in rows:
        ys = sorted(row["y_values"])
        row["y_ref"] = ys[len(ys)//2]
    # re-sort rows by y_ref descending
    rows.sort(key=lambda r: r["y_ref"], reverse=True)
    # serpentine within rows
    idx = 0
    for r_i, row in enumerate(rows):
        items = sorted(row["items"], key=lambda d: d["x"])
        if r_i % 2 == 1:  # alternate direction
            items = list(reversed(items))
        for d in items:
            d["idx"] = idx
            idx += 1
    return rows

def ltr_sort(letters):
    # Simple top-to-bottom rows, left-to-right within row
    rows = []
    letters_sorted = sorted(letters, key=lambda d: (-d["y"], d["x"]))
    current_y = None
    for d in letters_sorted:
        if current_y is None or abs(current_y - d["y"]) > ROW_TOL:
            rows.append([])
            current_y = d["y"]
        rows[-1].append(d)
    idx = 0
    for row in rows:
        for d in row:
            d["idx"] = idx
            idx += 1
    return rows

def write_outputs(letters):
    # Flatten by idx
    flat = sorted([d for d in letters if "idx" in d], key=lambda d: d["idx"])
    # CSV
    csv_path = os.path.join(OUTPUT_DIR, "kryptos_letters.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("idx,char,obj_name,collection,x,y,z,nx,ny,nz,sx,sy,sz\n")
        for d in flat:
            f.write("{idx},{char},{obj_name},{collection},{x},{y},{z},{nx},{ny},{nz},{sx},{sy},{sz}\n".format(**d))
    # JSON
    json_path = os.path.join(OUTPUT_DIR, "kryptos_letters.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([{
            k: d[k] for k in ("idx","char","obj_name","collection","x","y","z","nx","ny","nz","sx","sy","sz")
        } for d in flat], f, indent=2)
    # K4 line heuristic: take the last 97 letters if the model includes all K1–K4
    k4 = flat[-97:] if len(flat) >= 97 else flat
    k4_path = os.path.join(OUTPUT_DIR, "k4_line.csv")
    with open(k4_path, "w", encoding="utf-8") as f:
        f.write("k4_idx,char,obj_name,x,y,z\n")
        for i, d in enumerate(k4):
            f.write("{},{},{},{},{},{}\n".format(i, d["char"], d["obj_name"], d["x"], d["y"], d["z"]))
    print("Wrote:", csv_path, json_path, k4_path)

def main():
    letters = collect_letter_objs()
    if not letters:
        print("No letters found with current heuristics. Adjust INCLUDE_NAME_SUBSTRINGS / NAME_PATTERNS.")
        return
    if READING_MODE.lower().startswith("serp"):
        rows = serpentine_sort(letters)
    else:
        rows = ltr_sort(letters)
    # Assign contiguous idx inside rows already
    write_outputs(letters)

if __name__ == "__main__":
    main()