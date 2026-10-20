# Builds the high-detail guns and attachments: model (low and high), unwrap, bake, export.
#
#   blender -b --python art-src/hq/build_hq.py -- [--out <dir>] [--px <size>] [--quick] [name ...]
#
# Names: m4_carbine, and the attachments in hq_attachments.BUILDERS. Default: all of them.
# Writes <out>/<name>.glb (default assets/hq/), the baked maps as art-src/hq/out/maps/<name>_*.png for
# looking at, and art-src/hq/out/measure.json: each model's triangles per node, size, and its
# sockets in Godot's axes (x right... of a +Z-facing model: -X is its right; y up; z forward).
# --quick bakes at 8 samples for a look at the shapes; never ship a quick bake.
#
# On staging02 (RTX 2070) the bakes run on OptiX/CUDA; elsewhere on the CPU (slow, but works).
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import hq_kit as K  # noqa: E402
import hq_m4  # noqa: E402
import hq_pistol  # noqa: E402
import hq_smg  # noqa: E402
import hq_pump  # noqa: E402
import hq_attachments as A  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def opt(flag, default):
    if flag in args:
        i = args.index(flag)
        v = args[i + 1]
        del args[i:i + 2]
        return v
    return default


out = os.path.abspath(opt("--out", os.path.join(REPO, "assets", "hq")))
px_override = opt("--px", None)
ship_override = opt("--ship", None)
quick = "--quick" in args
if quick:
    args.remove("--quick")

# name: (builder, sockets, bake px, shipped px). The bake runs at the first size and the maps are
# scaled to the second; what ships is the .scn Godot imports (Basis Universal, whose size follows
# the pixels), so the shipped size is what the download budget is spent on. Shipped sizes are
# (albedo, ORM, normal): measured on the carbine, the ORM map costs about four times the albedo
# (three unrelated channels) and the normal map almost nothing, so the ORM is the one halved.
GUNS = {
    "m4_carbine": (hq_m4.build, hq_m4.SOCKETS, 2048, (1024, 512, 1024)),
    "service_pistol": (hq_pistol.build, hq_pistol.SOCKETS, 2048, (1024, 512, 1024)),
    "tactical_smg": (hq_smg.build, hq_smg.SOCKETS, 2048, (1024, 512, 1024)),
    "pump_shotgun": (hq_pump.build, hq_pump.SOCKETS, 2048, (1024, 512, 1024)),
}
# About the carbine's texel density (2048 over 0.77 m): the small ones need no more than 512.
ATTACH_PX = {"scope_4x": 1024, "ext_mag": 512, "laser": 512, "red_dot": 512, "suppressor": 512, "foregrip": 512}
names = args or (list(GUNS) + list(A.BUILDERS))
MAPS = os.path.join(HERE, "out", "maps")  # for looking at; never under assets/ (Godot would import them)
os.makedirs(MAPS, exist_ok=True)


def tag_group(obj, group):
    vg = obj.vertex_groups.new(name="g_" + group)
    vg.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")


def split_groups(joined, groups):
    """Separates the joined, baked mesh back into one object per group (vertex groups)."""
    result = {}
    first = groups[0]
    for g in groups[1:]:
        K.activate(joined)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")
        joined.vertex_groups.active_index = joined.vertex_groups["g_" + g].index
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.separate(type="SELECTED")
        bpy.ops.object.mode_set(mode="OBJECT")
        new = [o for o in bpy.context.selected_objects if o is not joined][0]
        new.name = g
        new.data.name = g
        result[g] = new
    joined.name = first
    joined.data.name = first
    result[first] = joined
    for o in result.values():
        o.vertex_groups.clear()
    return result


def glass_mats():
    clear = K.glass_material("lens", tint=(0.03, 0.06, 0.07))
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = 0.22
    bsdf.inputs["Specular IOR Level"].default_value = 1.0
    try:
        clear.surface_render_method = "BLENDED"
    except AttributeError:
        clear.blend_method = "BLEND"
    dot = K.glass_material("emitter", tint=(0.5, 0.02, 0.01), emit=(1.0, 0.05, 0.02))
    return {"glass": clear, "dot": dot}


def make(name):
    t0 = time.time()
    K.reset()
    if name in GUNS:
        builder, sockets, px, ship = GUNS[name]
        lo_groups, glass = builder(False)
        hi_groups, hi_glass = builder(True)
        origin = None
    else:
        sockets, px = {}, ATTACH_PX.get(name, 1024)
        ship = (min(px, 512), min(px, 512) // 2, min(px, 512))
        lo_groups, glass = A.build(name, False)
        hi_groups, hi_glass = A.build(name, True)
        origin = (0, 0, 0)
    if px_override:
        px = int(px_override)
    for o in hi_glass:
        bpy.data.objects.remove(o, do_unlink=True)

    order = list(lo_groups)
    parts = sorted(((K.tris(o), o.name) for g in order for o in lo_groups[g]), reverse=True)
    print("PARTS", " ".join("%s:%d" % (n, t) for t, n in parts[:18]))
    lows = []
    for g in order:
        obj = K.merge(g, lo_groups[g])
        tag_group(obj, g)
        lows.append(obj)
    joined = K.merge(name, lows)
    highs = [p for g in hi_groups for p in hi_groups[g]]
    K.assign_hi(highs)
    K.triangulate(joined)
    K.unwrap(joined, margin=6.0 / px)
    maps = K.bake(joined, highs, px, samples=8 if quick else 96)
    color, orm, normal = K.finish_maps(maps)
    if ship_override:
        ship = (int(ship_override),) * 3
    color, orm, normal = (K.downscale(m, min(s, px)) for m, s in zip((color, orm, normal), ship))
    mdir = MAPS
    ci = K.save_png(name + "_albedo", color, os.path.join(mdir, name + "_albedo.png"), False)
    oi = K.save_png(name + "_orm", orm, os.path.join(mdir, name + "_orm.png"), True)
    ni = K.save_png(name + "_normal", normal, os.path.join(mdir, name + "_normal.png"), True)
    mat = K.low_material(name, ci, oi, ni)
    joined.data.materials.clear()
    joined.data.materials.append(mat)
    for h in highs:
        bpy.data.objects.remove(h, do_unlink=True)
    bpy.data.orphans_purge(do_recursive=True)
    nodes = split_groups(joined, order)

    gm = glass_mats()
    for gobj in glass:
        kind = gobj.get("hq_mat", "glass")
        gobj.data.materials.clear()
        gobj.data.materials.append(gm.get(kind, gm["glass"]))
    if glass:
        g = K.merge(name + "_glass", glass)
        nodes[name + "_glass"] = g

    empties = [K.socket(s, p) for s, p in sockets.items()]
    meshes = list(nodes.values())
    lo, hi = K.bounds(meshes)
    if origin is None:
        origin = (0.0, (lo.y + hi.y) / 2 / K.MM, lo.z / K.MM)  # x on the bore, not the bounds' middle
    report = {"tris": {k: K.tris(v) for k, v in nodes.items()}, "px": px, "ship_px": list(ship), "quick": quick}
    report["tris_total"] = sum(report["tris"].values())
    K.export_glb(os.path.join(out, name + ".glb"), meshes + empties, origin)
    lo, hi = K.bounds(meshes)
    size = hi - lo
    report["size"] = [round(size.x, 4), round(size.z, 4), round(size.y, 4)]
    report["sockets"] = {e.name: [round(e.location.x, 4), round(e.location.z, 4), round(-e.location.y, 4)] for e in empties}
    report["origin_mm"] = [round(c, 2) for c in origin]
    report["seconds"] = round(time.time() - t0, 1)
    print("HQ %-12s tris %s size %s %.0fs" % (name, report["tris"], report["size"], report["seconds"]))
    return report


meas_dir = os.path.join(HERE, "out")
os.makedirs(meas_dir, exist_ok=True)
path = os.path.join(meas_dir, "measure.json")
report = json.load(open(path)) if os.path.exists(path) else {}
for n in names:
    report[n] = make(n)
    json.dump(report, open(path, "w"), indent=1, sort_keys=True)
info = {k: v for k, v in A.INFO.items()}
json.dump(info, open(os.path.join(meas_dir, "attachments.json"), "w"), indent=1, sort_keys=True)
