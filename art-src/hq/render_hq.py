# Cycles contact frames of the exported GLBs (the files that ship, not the build scene), with
# attachments parented to the gun's socket nodes exactly as the game does it.
#
#   blender -b --python art-src/hq/render_hq.py -- <glb dir> <out dir> <px> <samples> <setup> ...
#
# A setup is "<gun>" or "<gun>+<attachment>+<attachment>..." (e.g. m4_carbine+red_dot+laser);
# each renders as <setup>_<view>.png for the views in VIEWS. Hides what an attachment replaces
# (the magazine under an extended one, the rear sight under a scope), as ZedWeaponPack does.
import json
import math
import os
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
glb_dir, out_dir, px, samples, setups = args[0], args[1], int(args[2]), int(args[3]), args[4:]
os.makedirs(out_dir, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
INFO = json.load(open(os.path.join(HERE, "out", "attachments.json")))
MOUNT = {"optic": "socket_optic", "muzzle": "socket_muzzle", "underbarrel": "socket_underbarrel",
         "side": "socket_side", "magazine": "socket_magazine"}

# (name, camera direction from the gun's centre in Blender axes after import (glTF +Z muzzle ->
# Blender -Y), framing scale, look-at offset as a fraction of the size)
VIEWS = [
    ("right", Vector((-1, 0, 0.02)), 1.0, (0, 0, 0)),
    ("left", Vector((1, 0, 0.02)), 1.0, (0, 0, 0)),
    ("front34", Vector((-0.8, -0.75, 0.35)), 0.95, (0, 0, 0)),
    ("rear34", Vector((-0.55, 0.85, 0.45)), 0.95, (0, 0, 0)),
    ("receiver", Vector((-1, 0.25, 0.25)), 0.42, (0, 0.12, 0.05)),
    ("muzzle", Vector((-0.9, -0.5, 0.3)), 0.38, (0, -0.33, 0.06)),
]


def use_gpu(sc):
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = kind
            prefs.get_devices()
        except TypeError:
            continue
        found = [d for d in prefs.devices if d.type == kind]
        if found:
            for d in prefs.devices:
                d.use = d in found
            sc.cycles.device = "GPU"
            return
    sc.cycles.device = "CPU"


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def area(name, loc, energy, size, target=Vector((0, 0, 0))):
    light = bpy.data.lights.new(name, "AREA")
    light.energy = energy
    light.size = size
    obj = bpy.data.objects.new(name, light)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = loc
    d = target - Vector(loc)
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return obj


def studio(sc):
    sc.render.engine = "CYCLES"
    use_gpu(sc)
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x = px
    sc.render.resolution_y = int(px * 9 / 16)
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.11, 0.115, 0.12, 1)
    bg.inputs[1].default_value = 0.6
    sc.world = w
    area("key", (-1.2, -0.6, 1.4), 70, 1.2)
    area("fill", (1.3, -0.4, 0.5), 18, 1.5)
    area("rim", (0.3, 1.6, 0.9), 60, 0.8)
    floor = bpy.data.meshes.new("floor")
    floor.from_pydata([(-5, -5, 0), (5, -5, 0), (5, 5, 0), (-5, 5, 0)], [], [(0, 1, 2, 3)])
    fo = bpy.data.objects.new("floor", floor)
    sc.collection.objects.link(fo)
    m = bpy.data.materials.new("floor")
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (0.05, 0.052, 0.055, 1)
    b.inputs["Roughness"].default_value = 0.7
    floor.materials.append(m)
    return fo


def bounds(objs):
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for o in objs:
        if o.type != "MESH" or o.hide_render:
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


for setup in setups:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    floor = studio(sc)
    names = setup.split("+")
    gun = import_glb(os.path.join(glb_dir, names[0] + ".glb"))
    objs = list(gun)
    bpy.context.view_layer.update()
    for att in names[1:]:
        info = INFO[att]
        sock = bpy.data.objects.get(MOUNT[info["mount"]])
        parts = import_glb(os.path.join(glb_dir, att + ".glb"))
        for p in parts:
            if p.parent is None:
                p.parent = sock
                p.matrix_parent_inverse.identity()
        objs += parts
        for hide in info.get("hides", []):
            o = bpy.data.objects.get(hide)
            if o:
                o.hide_render = True
    bpy.context.view_layer.update()
    lo, hi = bounds(objs)
    floor.location.z = lo.z - 0.02
    centre = (lo + hi) / 2
    size = max((hi - lo).length, 0.2)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = 70
    for view, direction, scale, off in VIEWS:
        target = centre + Vector((off[0], off[1], off[2])) * size
        d = direction.normalized()
        dist = size * scale * 1.55
        cam.location = target + d * dist
        cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out_dir, "%s_%s.png" % (setup.replace("+", "-"), view))
        bpy.ops.render.render(write_still=True)
        print("RENDERED", sc.render.filepath)
