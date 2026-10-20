# Builds the guns from zed_guns.py and writes them where ZedWeaponPack reads them.
#
#   blender -b --python art-src/guns/build.py -- [--out <dir>] [--preview <dir>] [gun ...]
#
# Default out is assets/kitbash/. Prints each gun's size (Godot axes: x wide, y tall, z long) and
# writes them to art-src/guns/out/measure.json: the heights ZedWeaponPack.art() lifts each gun
# by come from there. --preview also renders each gun's side view (Workbench, flat) as <gun>.png.
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import zed_kit  # noqa: E402
import zed_guns  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = os.path.join(zed_kit.REPO, "assets", "kitbash")
preview = None
if "--out" in args:
    i = args.index("--out")
    out = os.path.abspath(args[i + 1])
    del args[i:i + 2]
if "--preview" in args:
    i = args.index("--preview")
    preview = os.path.abspath(args[i + 1])
    del args[i:i + 2]
names = args or list(zed_guns.RECIPES)
os.makedirs(out, exist_ok=True)
report = {}


def side_view(gun, path):
    sc = bpy.context.scene
    lo, hi = zed_kit.bounds(gun)
    c = (lo + hi) / 2
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x = 1200
    sc.render.resolution_y = 500
    sc.display.shading.light = "FLAT"
    sc.display.shading.color_type = "MATERIAL"
    sc.world = bpy.data.worlds.new("w")
    sc.world.color = (0.9, 0.9, 0.9)
    cam = bpy.data.objects.new("c", bpy.data.cameras.new("c"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(hi.y - lo.y, (hi.z - lo.z) * 2.4) * 1.1
    cam.location = (c.x + 20, c.y, c.z)
    cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


for name in names:
    zed_kit.reset()
    gun, length = zed_guns.RECIPES[name]()
    if preview:
        os.makedirs(preview, exist_ok=True)
        side_view(gun, os.path.join(preview, name + ".png"))
    tris = sum(len(p.vertices) - 2 for p in gun.data.polygons)
    size = zed_kit.export_standing(gun, os.path.join(out, name + ".glb"), length)
    report[name] = {"size": size, "tris": tris}
    print("GUN %-17s size %s tris %d" % (name, size, tris))
meas = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(meas, exist_ok=True)
path = os.path.join(meas, "measure.json")
old = json.load(open(path)) if os.path.exists(path) else {}
old.update(report)
json.dump(old, open(path, "w"), indent=1, sort_keys=True)
