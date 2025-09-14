# extract_letter_holes.py  (Blender 4.x)
import bpy, bmesh, mathutils, os, json, math, hashlib
from mathutils import Vector
from datetime import datetime

# ----------------- CONFIG -----------------
COPPER_NAME_HINTS = ["CopperSheet","Copper","Kryptos.Part.CopperSheet"]
OUTPUT_DIR = bpy.path.abspath("//")
READING_MODE = "serpentine"  # or "left_to_right"
ROW_TOL = 0.015              # meters; adjust ONLY if rows mis-bucket
UV_METHOD = "plane"          # or "cylinder"
DROP_SMALLEST_AREA = 1e-6    # m^2; holes smaller than this -> discard
MAX_HOLES = 2000             # safety guard
ANCHOR_WINDOWS = { "EAST":(21,25), "NORTHEAST":(25,34), "BERLIN":(63,69), "CLOCK":(69,74) }
# ------------------------------------------

def find_copper_object():
    cand=[]
    for o in bpy.data.objects:
        if o.type=='MESH' and any(h.lower() in o.name.lower() for h in COPPER_NAME_HINTS):
            cand.append(o)
    if not cand:
        raise RuntimeError("Copper sheet object not found. Update COPPER_NAME_HINTS.")
    # choose the one with most faces
    return sorted(cand, key=lambda o: len(o.data.polygons), reverse=True)[0]

def duplicate_for_bmesh(obj):
    temp = obj.copy()
    temp.data = obj.data.copy()
    temp.name = obj.name + ".TEMP"
    bpy.context.collection.objects.link(temp)
    return temp

def loop_area_and_centroid(loop_verts, plane_center, plane_normal):
    # project to plane and compute polygon area, centroid
    # build an orthonormal basis on plane
    z = plane_normal.normalized()
    x = Vector((1,0,0))
    if abs(z.dot(x))>0.9: x = Vector((0,1,0))
    y = z.cross(x).normalized()
    x = y.cross(z).normalized()
    pts2d = []
    for v in loop_verts:
        p = v.co - plane_center
        u = p.dot(x); w = p.dot(y)
        pts2d.append(Vector((u,w)))
    # area & centroid (shoelace)
    A=0.0; C=Vector((0.0,0.0))
    n=len(pts2d)
    for i in range(n):
        p=pts2d[i]; q=pts2d[(i+1)%n]
        cross = p.x*q.y - p.y*q.x
        A += cross
        C += (p+q)*cross
    A *= 0.5
    if abs(A) < 1e-12:
        return 0.0, plane_center
    C = C*(1.0/(6.0*A))
    # back to 3D
    centroid3d = plane_center + x*C.x + y*C.y
    return abs(A), centroid3d

def best_fit_plane(verts):
    # simple PCA for plane of all letter loops: use copper object bbox midplane as fallback
    pts=[v.co for v in verts]
    mean = sum(pts, Vector())/len(pts)
    # covariance
    C = mathutils.Matrix(((0,0,0),(0,0,0),(0,0,0)))
    for p in pts:
        d = p-mean
        for i in range(3):
            for j in range(3):
                C[i][j]+=d[i]*d[j]
    # eigenvectors via SVD
    U, S, V = C.svd()
    normal = U.col(2)  # smallest variance axis
    return mean, normal

def extract_boundary_loops(obj):
    # Build bmesh
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)  # robust loops
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Tag boundary edges (edges with only one face)
    boundary_edges = [e for e in bm.edges if len(e.link_faces)==1]
    if not boundary_edges:
        # copper might be closed (thickness). Try marking sharp edges as boundary proxy
        boundary_edges = [e for e in bm.edges if e.smooth==False or e.calc_face_angle() > math.radians(45)]
        if not boundary_edges:
            raise RuntimeError("No boundary edges found; solid sheet? Need a mid-plane slice to expose holes.")

    # Build edge-loop connectivity
    edge_to_verts = {}
    for e in boundary_edges:
        edge_to_verts.setdefault(e.verts[0], []).append(e)
        edge_to_verts.setdefault(e.verts[1], []).append(e)

    loops=[]
    visited=set()
    for e in boundary_edges:
        if e in visited: continue
        loop=[e]
        visited.add(e)
        v_curr = e.verts[1]
        e_curr = e
        # walk around
        while True:
            next_edges=[ed for ed in edge_to_verts[v_curr] if ed in boundary_edges and ed not in visited]
            if not next_edges:
                break
            # choose edge that continues loop
            # heuristic: share exactly one vertex with current
            found=None
            for ed in next_edges:
                if e_curr.verts[0] in ed.verts or e_curr.verts[1] in ed.verts:
                    found=ed; break
            if not found: found = next_edges[0]
            loop.append(found)
            visited.add(found)
            # step
            v_curr = found.verts[1] if found.verts[0]==v_curr else found.verts[0]
            e_curr = found
            # close?
            if v_curr in (loop[0].verts[0], loop[0].verts[1]):
                break
        # collect unique verts
        vset=[]
        seen=set()
        for ed in loop:
            for v in ed.verts:
                if v not in seen:
                    vset.append(v); seen.add(v)
        loops.append(vset)

    # Compute plane once for all
    all_verts=[]
    for l in loops: all_verts+=l
    center, normal = best_fit_plane(all_verts)

    # Compute area, centroid for each loop
    loop_info=[]
    for vset in loops:
        A, C = loop_area_and_centroid(vset, center, normal)
        loop_info.append(dict(area=A, centroid=C, verts=[v for v in vset]))

    # Drop largest loop (outer border)
    loop_info=sorted(loop_info, key=lambda d:d["area"], reverse=True)
    if loop_info:
        outer=loop_info[0]
        candidates = loop_info[1:]
    else:
        candidates=[]
    # Drop tiny junk
    candidates=[d for d in candidates if d["area"]>=DROP_SMALLEST_AREA]
    if len(candidates)>MAX_HOLES:
        raise RuntimeError("Too many candidate holes; check DROP_SMALLEST_AREA.")
    return candidates, center, normal

def create_empties_for_loops(candidates, collection_name="LetterHoles"):
    # make a new collection
    col = bpy.data.collections.get(collection_name) or bpy.data.collections.new(collection_name)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    empties=[]
    for i, d in enumerate(candidates):
        e = bpy.data.objects.new(f"K_HOLE_{i:03d}", None)
        e.empty_display_type='SPHERE'
        e.empty_display_size=0.01
        e.location = d["centroid"]
        col.objects.link(e)
        empties.append(e)
    return empties

def index_rows(letters, mode="serpentine", row_tol=ROW_TOL):
    # letters: list of dicts {obj, p, ...} using obj.location
    # project to plane uv first (filled later) – for now use world Y for row bucketing
    pts=sorted(letters, key=lambda d:d["p"].y, reverse=True)
    rows=[]
    for d in pts:
        placed=False
        for r in rows:
            if abs(r["y_ref"]-d["p"].y)<=row_tol:
                r["items"].append(d); placed=True; break
        if not placed:
            rows.append(dict(y_ref=d["p"].y, items=[d]))
    # refine y_ref
    for r in rows:
        ys=sorted([it["p"].y for it in r["items"]]); r["y_ref"]=ys[len(ys)//2]
    rows.sort(key=lambda r:r["y_ref"], reverse=True)
    # index within rows
    idx=0
    for ri,r in enumerate(rows):
        items=sorted(r["items"], key=lambda d:d["p"].x)
        if mode=="serpentine" and (ri%2==1): items=list(reversed(items))
        for it in items:
            it["idx"]=idx; it["row"]=ri; idx+=1
    return rows

def plane_uv(letters):
    # PCA plane fit for positions -> (u,v) in [0,1]
    P=[d["p"] for d in letters]
    mean=sum(P, Vector())/len(P)
    C=mathutils.Matrix(((0,0,0),(0,0,0),(0,0,0)))
    for p in P:
        d=p-mean
        for i in range(3):
            for j in range(3):
                C[i][j]+=d[i]*d[j]
    U,S,V = C.svd()
    n = U.col(2)
    t = U.col(0); b = U.col(1)
    umin=umin=1e9; umax=-1e9; vmin=1e9; vmax=-1e9
    for d in letters:
        u=(d["p"]-mean).dot(t); v=(d["p"]-mean).dot(b)
        d["u_raw"]=u; d["v_raw"]=v
        umin=min(umin,u); umax=max(umax,u); vmin=min(vmin,v); vmax=max(vmax,v)
    for d in letters:
        d["u"]=(d["u_raw"]-umin)/(umax-umin+1e-9)
        d["v"]=(d["v_raw"]-vmin)/(vmax-vmin+1e-9)

def cylinder_uv(letters):
    P=[d["p"] for d in letters]
    mean=sum(P, Vector())/len(P)
    zmin=min(p.z for p in P); zmax=max(p.z for p in P)
    for d in letters:
        p=d["p"]-mean
        theta=math.atan2(p.y, p.x)
        d["u"]=(theta+math.pi)/(2*math.pi)
        d["v"]=(p.z - zmin)/(zmax-zmin+1e-9)

def export_csv_json(letters, blend_path):
    flat=sorted(letters, key=lambda d:d["idx"])
    # CSV
    csvp=os.path.join(OUTPUT_DIR,"letter_holes.csv")
    with open(csvp,"w",encoding="utf-8") as f:
        f.write("idx,obj_name,x,y,z,u,v,row\n")
        for d in flat:
            f.write("{idx},{obj_name},{x},{y},{z},{u},{v},{row}\n".format(
                idx=d["idx"], obj_name=d["obj_name"], x=d["p"].x, y=d["p"].y, z=d["p"].z, u=d["u"], v=d["v"], row=d["row"]))
    # JSON
    jsonp=os.path.join(OUTPUT_DIR,"letter_holes.json")
    with open(jsonp,"w",encoding="utf-8") as f:
        json.dump([dict(idx=d["idx"], obj_name=d["obj_name"], x=d["p"].x, y=d["p"].y, z=d["p"].z, u=d["u"], v=d["v"], row=d["row"]) for d in flat], f, indent=2)
    # Receipts
    rec=os.path.join(OUTPUT_DIR,"receipts_holes.json")
    rec_d=dict(
        timestamp=datetime.utcnow().isoformat()+"Z",
        blender_version=bpy.app.version_string,
        blend_path=blend_path,
        blend_sha256=file_sha256(blend_path),
        script_sha256=file_sha256(bpy.path.abspath("//extract_letter_holes.py")),
        reading_mode=READING_MODE, uv_method=UV_METHOD,
        n_holes=len(flat)
    )
    with open(rec,"w",encoding="utf-8") as f: json.dump(rec_d,f,indent=2)
    print("Wrote:", csvp, jsonp, rec)

def overlay_png(letters):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        flat=sorted(letters, key=lambda d:d["idx"])
        xs=[d["u"] for d in flat]; ys=[d["v"] for d in flat]
        plt.figure(figsize=(8,6))
        plt.scatter(xs, ys, s=10, c="#cccccc")
        for d in flat[::7]:
            plt.text(d["u"], d["v"], str(d["idx"]), fontsize=6)
        plt.title("Letter holes (u,v) with indices")
        plt.savefig(os.path.join(OUTPUT_DIR,"overlay_holes_uv.png"), dpi=200)
        plt.close()
    except Exception as e:
        print("Overlay error:", e)

def file_sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1<<20), b''): h.update(chunk)
    return h.hexdigest()

def main():
    copper = find_copper_object()
    temp = duplicate_for_bmesh(copper)
    try:
        candidates, center, normal = extract_boundary_loops(temp)
    finally:
        # clean up temp
        try: bpy.data.objects.remove(temp, do_unlink=True)
        except: pass

    # instantiate empties
    empties = create_empties_for_loops(candidates)
    letters=[]
    for e in empties:
        letters.append(dict(obj=e, obj_name=e.name, p=e.location.copy()))

    # unwrap to uv
    if UV_METHOD=="cylinder": cylinder_uv(letters)
    else: plane_uv(letters)

    # index rows
    rows=index_rows(letters, mode=READING_MODE, row_tol=ROW_TOL)

    # export
    export_csv_json(letters, bpy.data.filepath)
    overlay_png(letters)

if __name__=="__main__":
    main()
