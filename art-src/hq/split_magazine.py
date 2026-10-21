"""Splits a high-detail gun's own magazine out into assets/hq/<gun>_mag.glb, the part a reload
carries in (ZeeWeaponArt.magazine_path with magazine_loose). Origin is the gun's socket_magazine,
so the part sits where the model's magazine meets the well. Textures are scaled to 512: the
carried part is small on screen and the atlas it shares with the gun is 1024+.

  blender -b --python art-src/hq/split_magazine.py -- <assets/hq dir> <gun> [<gun>...]
"""
import sys, os
import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
out_dir, guns = argv[0], argv[1:]
for gun in guns:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(out_dir, gun + ".glb"))
    mag = next(o for o in bpy.data.objects if o.name == "magazine")
    sock = next(o for o in bpy.data.objects if o.name == "socket_magazine")
    origin = sock.matrix_world.translation.copy()
    for o in list(bpy.data.objects):
        if o is not mag:
            bpy.data.objects.remove(o)
    mag.parent = None
    mag.matrix_world.translation -= origin
    bpy.context.view_layer.objects.active = mag
    mag.select_set(True)
    for img in bpy.data.images:
        if img.size[0] > 512:
            img.scale(512, 512)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, gun + "_mag.glb"), export_format="GLB",
                              use_selection=True, export_yup=True)
    print("split", gun)
