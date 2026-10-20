# hq_kit: the modelling, baking and export helpers behind the high-detail guns (hq_m4.py,
# hq_attachments.py). Run through build_hq.py, never on its own.
#
# The method, and why each step is the way it is:
#
#  * Every part is built twice from one recipe: a LOW mesh (what ships: one-segment chamfers on
#    every hard edge, hardened normals, about 8-10k triangles for a rifle) and a HIGH mesh (the
#    same part with three-segment rounded bevels, engraved markings and denser cylinders). The
#    high one is never exported; its rounded edges, its markings and its procedural surface are
#    baked onto the low one's single UV atlas. A chamfer alone reads as faceted under a moving
#    light; a chamfer plus a normal map baked from a round edge reads as machined metal.
#  * Surfaces are procedural shaders on the high mesh (anodised aluminium, phosphated steel,
#    polymer, brass), with edge wear from the Bevel node's normal against the true normal, dirt in
#    the cavities from the AO node, and stretched-noise scratches along the barrel axis. There is
#    no external texture at all, so no licence to track: every pixel is computed here.
#  * Colour, roughness and metalness are baked as emission (each value wired into an Emission
#    shader, bake type EMIT), because a DIFFUSE bake of a metal is black and a ROUGHNESS bake has
#    no metallic counterpart. Normal and AO are baked as themselves.
#  * The atlas is packed into glTF's layout (ORM: R occlusion, G roughness, B metal) and the
#    albedo carries a share of the AO too, because a browser build has no screen-space AO to
#    darken a crevice for us.
#
# Frame while modelling: metres, the bore along +Y (muzzle at +Y), up +Z, the gun's right side
# (the ejection port) on +X. export_glb() turns it half a circle about Z, so the file's muzzle is
# glTF +Z and its right side -X, which is how zed's models are laid out (ZedWeaponPack).
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

MM = 0.001


def reset():
    # The routing table names materials of the previous model, gone after this.
    _SOCKETS.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.curves):
        for block in list(coll):
            coll.remove(block)


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


# --- Primitives ---------------------------------------------------------------------------------

def _from_bm(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    obj = link(bpy.data.objects.new(name, me))
    if mat is not None:
        obj["hq_mat"] = mat
    return obj


def profile(name, pts_yz, x0, x1, mat, scale=MM):
    """A side profile (points (y, z) in mm, any winding) extruded across X from x0 to x1 (mm)."""
    bm = bmesh.new()
    vs = [bm.verts.new((x0 * scale, y * scale, z * scale)) for y, z in pts_yz]
    face = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    moved = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=((x1 - x0) * scale, 0, 0))
    return _from_bm(name, bm, mat)


def profile_x(name, pts_xz, y0, y1, mat, scale=MM):
    """A cross-section (points (x, z) in mm) extruded along Y from y0 to y1 (mm)."""
    bm = bmesh.new()
    vs = [bm.verts.new((x * scale, y0 * scale, z * scale)) for x, z in pts_xz]
    face = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    moved = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=moved, vec=(0, (y1 - y0) * scale, 0))
    return _from_bm(name, bm, mat)


def box(name, c, size, mat, scale=MM):
    """A box centred on c (mm) with full size (mm)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, verts=bm.verts, vec=Vector(size) * scale)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(c) * scale)
    return _from_bm(name, bm, mat)


def lathe(name, prof, segs, mat, axis="Y", centre=(0, 0, 0), phase=0.0, scale=MM, cap=True):
    """A solid of revolution: prof is [(along, radius), ...] in mm, swept round `axis` through
    `centre`. Radius 0 points close the ends; otherwise the ends are capped with an n-gon."""
    bm = bmesh.new()
    rings = []
    for a, r in prof:
        ring = []
        n = 1 if r <= 0 else segs
        for i in range(n):
            t = phase + 2 * math.pi * i / segs
            u, v = r * math.cos(t), r * math.sin(t)
            if axis == "Y":
                p = (u, a, v)
            elif axis == "X":
                p = (a, u, v)
            else:
                p = (u, v, a)
            ring.append(bm.verts.new(Vector(p) * scale + Vector(centre) * scale))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        if len(r0) == 1 and len(r1) == 1:
            continue
        for i in range(segs):
            if len(r0) == 1:
                bm.faces.new((r0[0], r1[i], r1[(i + 1) % segs]))
            elif len(r1) == 1:
                bm.faces.new((r0[i], r0[(i + 1) % segs], r1[0]))
            else:
                bm.faces.new((r0[i], r0[(i + 1) % segs], r1[(i + 1) % segs], r1[i]))
    if cap:
        if len(rings[0]) > 2:
            bm.faces.new(rings[0])
        if len(rings[-1]) > 2:
            bm.faces.new(list(reversed(rings[-1])))
    return _from_bm(name, bm, mat)


def cyl(name, a0, a1, r, segs, mat, axis="Y", centre=(0, 0, 0), phase=0.0):
    return lathe(name, [(a0, r), (a1, r)], segs, mat, axis, centre, phase)


def text(name, body, size, where, facing, mat, depth=0.25):
    """Raised lettering for the HIGH mesh only (markings baked into colour and normal).
    facing '-X' reads correctly from the gun's left, '+X' from its right; size and depth in mm."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size * MM
    cu.extrude = depth * MM / 2
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    tmp = link(bpy.data.objects.new(name + "_c", cu))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    obj = link(bpy.data.objects.new(name, me))
    if facing == "-X":
        rot = Matrix(((0, 0, -1), (-1, 0, 0), (0, 1, 0))).to_4x4()
    else:
        rot = Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0))).to_4x4()
    me.transform(rot)
    me.transform(Matrix.Translation(Vector(where) * MM))
    obj["hq_mat"] = mat
    return obj


# --- Operations ---------------------------------------------------------------------------------

def apply_mods(obj):
    activate(obj)
    for m in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def cut(obj, *cutters, union=False):
    """Boolean every cutter out of (or into) obj, then delete the cutters."""
    for c in cutters:
        m = obj.modifiers.new("cut", "BOOLEAN")
        m.operation = "UNION" if union else "DIFFERENCE"
        m.object = c
        m.solver = "EXACT"
        apply_mods(obj)
        bpy.data.objects.remove(c, do_unlink=True)
    return obj


def merge(name, objs):
    """Joins objs into one object (no boolean: overlapping solids, which is fine to render)."""
    objs = [o for o in objs if o is not None]
    activate(objs[0])
    for o in objs[1:]:
        o.select_set(True)
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]


def transform(obj, mat):
    obj.data.transform(mat)
    return obj


def rot_y(deg):
    return Matrix.Rotation(math.radians(deg), 4, "Y")


def rot_x(deg):
    return Matrix.Rotation(math.radians(deg), 4, "X")


def rot_z(deg):
    return Matrix.Rotation(math.radians(deg), 4, "Z")


def at(mm_xyz):
    return Matrix.Translation(Vector(mm_xyz) * MM)


def finish(obj, hi, bevel_mm=0.8, angle=32, segs_lo=1, segs_hi=3, round_mm=None):
    """Shading and edges: sharp edges by angle, a bevel on every edge sharper than `angle`, and
    hardened normals on the low mesh (so a one-segment chamfer shades as a flat face with a crisp
    highlight, not a smeared gradient). round_mm gives soft parts (a grip) a wider, rounder edge."""
    w = (round_mm if round_mm else bevel_mm) * MM
    obj.data.shade_smooth()
    if not hi and segs_lo == 0:
        # No chamfer on the low mesh at all: flat-shaded hard edges, the bevel's highlight
        # carried by the normal map alone. For many small repeated edges (rail teeth), where a
        # chamfer per edge costs more triangles than everything else on the gun.
        obj.data.shade_flat()
        return obj
    m = obj.modifiers.new("bevel", "BEVEL")
    m.width = w
    m.segments = (segs_hi + (2 if round_mm else 0)) if hi else (segs_lo + (1 if round_mm else 0))
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(angle)
    m.use_clamp_overlap = True
    m.harden_normals = not hi
    m.profile = 0.5
    if not hi:
        m.miter_outer = "MITER_SHARP"
    apply_mods(obj)
    if hi:
        sm = obj.modifiers.new("smooth", "NODES")
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        except Exception:
            pass
        obj.modifiers.remove(sm)
    else:
        wn = obj.modifiers.new("wn", "WEIGHTED_NORMAL")
        wn.keep_sharp = True
        wn.weight = 50
        apply_mods(obj)
    return obj


def tris(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def bounds(objs):
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type != "MESH":
            continue
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


def socket(name, mm_xyz):
    e = link(bpy.data.objects.new(name, None))
    e.empty_display_type = "ARROWS"
    e.empty_display_size = 0.02
    e.location = Vector(mm_xyz) * MM
    return e


# --- Materials (HIGH mesh: procedural; LOW mesh: the baked atlas) --------------------------------

# Linear base colour, roughness, metal of the coating; then of the bare metal at worn edges.
FINISHES = {
    "anod": dict(base=(0.040, 0.041, 0.044), rough=0.48, metal=0.0, wear=(0.62, 0.62, 0.64), wear_rough=0.30, wear_metal=1.0, wear_amt=1.0, bump=0.10),
    "steel": dict(base=(0.034, 0.036, 0.034), rough=0.58, metal=0.0, wear=(0.48, 0.48, 0.47), wear_rough=0.26, wear_metal=1.0, wear_amt=0.9, bump=0.18),
    "poly": dict(base=(0.036, 0.036, 0.036), rough=0.70, metal=0.0, wear=(0.10, 0.10, 0.098), wear_rough=0.52, wear_metal=0.0, wear_amt=0.6, bump=0.25),
    "grip": dict(base=(0.034, 0.034, 0.034), rough=0.78, metal=0.0, wear=(0.09, 0.09, 0.088), wear_rough=0.55, wear_metal=0.0, wear_amt=0.5, bump=1.0),
    "rubber": dict(base=(0.022, 0.022, 0.022), rough=0.88, metal=0.0, wear=(0.05, 0.05, 0.05), wear_rough=0.8, wear_metal=0.0, wear_amt=0.3, bump=0.6),
    "tan": dict(base=(0.30, 0.22, 0.13), rough=0.66, metal=0.0, wear=(0.42, 0.34, 0.24), wear_rough=0.5, wear_metal=0.0, wear_amt=0.6, bump=0.3),
    "wood": dict(base=(0.095, 0.036, 0.014), rough=0.52, metal=0.0, wear=(0.24, 0.11, 0.05), wear_rough=0.45, wear_metal=0.0, wear_amt=0.7, bump=0.35),
    "cerakote": dict(base=(0.055, 0.055, 0.052), rough=0.55, metal=0.0, wear=(0.42, 0.42, 0.41), wear_rough=0.3, wear_metal=1.0, wear_amt=0.8, bump=0.15),
    "magalu": dict(base=(0.050, 0.050, 0.048), rough=0.45, metal=0.0, wear=(0.62, 0.62, 0.64), wear_rough=0.3, wear_metal=1.0, wear_amt=1.0, bump=0.1),
    "brass": dict(base=(0.80, 0.52, 0.22), rough=0.30, metal=1.0, wear=(0.85, 0.62, 0.34), wear_rough=0.22, wear_metal=1.0, wear_amt=0.3, bump=0.05),
    "copper": dict(base=(0.75, 0.36, 0.20), rough=0.32, metal=1.0, wear=(0.8, 0.45, 0.3), wear_rough=0.25, wear_metal=1.0, wear_amt=0.3, bump=0.05),
    "paint": dict(base=(0.55, 0.55, 0.50), rough=0.80, metal=0.0, wear=(0.3, 0.3, 0.28), wear_rough=0.8, wear_metal=0.0, wear_amt=0.2, bump=0.0),
    "lens": dict(base=(0.01, 0.015, 0.02), rough=0.08, metal=0.0, wear=(0.01, 0.015, 0.02), wear_rough=0.08, wear_metal=0.0, wear_amt=0.0, bump=0.0),
    "emit": dict(base=(0.6, 0.02, 0.01), rough=0.3, metal=0.0, wear=(0.6, 0.02, 0.01), wear_rough=0.3, wear_metal=0.0, wear_amt=0.0, bump=0.0),
}

_SOCKETS = {}


def _n(nt, kind, x=0, y=0, **props):
    n = nt.nodes.new(kind)
    n.location = (x, y)
    for k, v in props.items():
        setattr(n, k, v)
    return n


def hi_material(kind):
    """The procedural surface for one finish, with its colour, roughness and metal sockets
    remembered so bake_pass() can route each into an Emission shader."""
    name = "hi_" + kind
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    f = FINISHES[kind]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = _n(nt, "ShaderNodeOutputMaterial", 1400, 0)
    bsdf = _n(nt, "ShaderNodeBsdfPrincipled", 1100, 0)
    emit = _n(nt, "ShaderNodeEmission", 1100, -400)
    tc = _n(nt, "ShaderNodeTexCoord", -1200, 0)
    geo = _n(nt, "ShaderNodeNewGeometry", -1200, -300)

    # Edge mask: how far the rounded (Bevel node) normal leans from the true one.
    bev = _n(nt, "ShaderNodeBevel", -1000, -300, samples=8)
    bev.inputs["Radius"].default_value = 0.0018
    dot = _n(nt, "ShaderNodeVectorMath", -800, -300, operation="DOT_PRODUCT")
    nt.links.new(bev.outputs["Normal"], dot.inputs[0])
    nt.links.new(geo.outputs["Normal"], dot.inputs[1])
    edge = _n(nt, "ShaderNodeMapRange", -600, -300)
    edge.inputs["From Min"].default_value = 0.9985
    edge.inputs["From Max"].default_value = 0.93
    nt.links.new(dot.outputs["Value"], edge.inputs["Value"])

    # Break the wear into patches: large noise, thresholded.
    patch = _n(nt, "ShaderNodeTexNoise", -800, -550)
    patch.inputs["Scale"].default_value = 60.0
    patch.inputs["Detail"].default_value = 6.0
    patch.inputs["Roughness"].default_value = 0.65
    nt.links.new(tc.outputs["Object"], patch.inputs["Vector"])
    pmap = _n(nt, "ShaderNodeMapRange", -600, -550)
    pmap.inputs["From Min"].default_value = 0.32
    pmap.inputs["From Max"].default_value = 0.55
    nt.links.new(patch.outputs["Fac"], pmap.inputs["Value"])
    wear = _n(nt, "ShaderNodeMath", -400, -400, operation="MULTIPLY", use_clamp=True)
    nt.links.new(edge.outputs["Result"], wear.inputs[0])
    nt.links.new(pmap.outputs["Result"], wear.inputs[1])

    # Fine scratches: noise stretched along the bore (Y), a few of them bright.
    smap = _n(nt, "ShaderNodeMapping", -1000, -800)
    smap.inputs["Scale"].default_value = (650.0, 30.0, 650.0)
    nt.links.new(tc.outputs["Object"], smap.inputs["Vector"])
    scr = _n(nt, "ShaderNodeTexNoise", -800, -800)
    scr.inputs["Scale"].default_value = 1.0
    scr.inputs["Detail"].default_value = 2.0
    nt.links.new(smap.outputs["Vector"], scr.inputs["Vector"])
    smr = _n(nt, "ShaderNodeMapRange", -600, -800)
    smr.inputs["From Min"].default_value = 0.62
    smr.inputs["From Max"].default_value = 0.70
    smr.inputs["To Max"].default_value = 0.42
    nt.links.new(scr.outputs["Fac"], smr.inputs["Value"])
    wear2 = _n(nt, "ShaderNodeMath", -200, -500, operation="MAXIMUM", use_clamp=True)
    nt.links.new(wear.outputs["Value"], wear2.inputs[0])
    nt.links.new(smr.outputs["Result"], wear2.inputs[1])
    wscale = _n(nt, "ShaderNodeMath", 0, -500, operation="MULTIPLY", use_clamp=True)
    wscale.inputs[1].default_value = f["wear_amt"]
    nt.links.new(wear2.outputs["Value"], wscale.inputs[0])

    # Dirt in the cavities: local AO, darkens and roughens.
    ao = _n(nt, "ShaderNodeAmbientOcclusion", -800, 300, only_local=True, samples=16)
    ao.inputs["Distance"].default_value = 0.012
    dirt = _n(nt, "ShaderNodeMapRange", -600, 300)
    dirt.inputs["From Min"].default_value = 1.0
    dirt.inputs["From Max"].default_value = 0.25
    nt.links.new(ao.outputs["AO"], dirt.inputs["Value"])

    # Low-frequency mottling of the coating itself.
    mot = _n(nt, "ShaderNodeTexNoise", -800, 600)
    mot.inputs["Scale"].default_value = 35.0
    mot.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], mot.inputs["Vector"])
    motc = _n(nt, "ShaderNodeMapRange", -600, 600)
    motc.inputs["To Min"].default_value = 0.62
    motc.inputs["To Max"].default_value = 1.35
    nt.links.new(mot.outputs["Fac"], motc.inputs["Value"])

    # Oil and handling streaks, long along the bore, multiplied into the mottling: they vary
    # the colour and (through the same factor) the roughness, so the sheen is never uniform.
    smap2 = _n(nt, "ShaderNodeMapping", -1000, 900)
    smap2.inputs["Scale"].default_value = (60.0, 6.0, 60.0)
    nt.links.new(tc.outputs["Object"], smap2.inputs["Vector"])
    streak = _n(nt, "ShaderNodeTexNoise", -800, 900)
    streak.inputs["Detail"].default_value = 4.0
    nt.links.new(smap2.outputs["Vector"], streak.inputs["Vector"])
    strc = _n(nt, "ShaderNodeMapRange", -600, 900)
    strc.inputs["To Min"].default_value = 0.78
    strc.inputs["To Max"].default_value = 1.2
    nt.links.new(streak.outputs["Fac"], strc.inputs["Value"])
    motx = _n(nt, "ShaderNodeMath", -500, 700, operation="MULTIPLY")
    nt.links.new(motc.outputs["Result"], motx.inputs[0])
    nt.links.new(strc.outputs["Result"], motx.inputs[1])
    motc = motx
    # Powder soot toward the muzzle (the object's Y is the bore).
    sep = _n(nt, "ShaderNodeSeparateXYZ", -1000, 1150)
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    sootm = _n(nt, "ShaderNodeMapRange", -800, 1150)
    sootm.inputs["From Min"].default_value = 0.28
    sootm.inputs["From Max"].default_value = 0.40
    sootm.inputs["To Max"].default_value = 0.8
    nt.links.new(sep.outputs["Y"], sootm.inputs["Value"])

    base = _n(nt, "ShaderNodeRGB", -400, 600)
    base.outputs[0].default_value = (*f["base"], 1)
    basem = _n(nt, "ShaderNodeMix", -200, 600, data_type="RGBA", blend_type="MULTIPLY")
    basem.inputs["Factor"].default_value = 1.0
    nt.links.new(base.outputs[0], basem.inputs[6])
    nt.links.new(motc.outputs[0], basem.inputs[7])
    grime = _n(nt, "ShaderNodeMix", 0, 450, data_type="RGBA", blend_type="MIX")
    grime.inputs[7].default_value = (0.012, 0.011, 0.010, 1)
    gfac = _n(nt, "ShaderNodeMath", -200, 400, operation="MULTIPLY", use_clamp=True)
    gfac.inputs[1].default_value = 0.95
    gmax = _n(nt, "ShaderNodeMath", -350, 400, operation="MAXIMUM", use_clamp=True)
    nt.links.new(dirt.outputs["Result"], gmax.inputs[0])
    nt.links.new(sootm.outputs["Result"], gmax.inputs[1])
    nt.links.new(gmax.outputs["Value"], gfac.inputs[0])
    nt.links.new(gfac.outputs["Value"], grime.inputs["Factor"])
    nt.links.new(basem.outputs[2], grime.inputs[6])
    wcol = _n(nt, "ShaderNodeRGB", 0, 250)
    wcol.outputs[0].default_value = (*f["wear"], 1)
    col = _n(nt, "ShaderNodeMix", 300, 400, data_type="RGBA", blend_type="MIX")
    nt.links.new(wscale.outputs["Value"], col.inputs["Factor"])
    nt.links.new(grime.outputs[2], col.inputs[6])
    nt.links.new(wcol.outputs[0], col.inputs[7])

    rough = _n(nt, "ShaderNodeMapRange", 300, 0)
    rough.inputs["From Min"].default_value = 0.0
    rough.inputs["From Max"].default_value = 1.0
    rough.inputs["To Min"].default_value = f["rough"]
    rough.inputs["To Max"].default_value = f["wear_rough"]
    nt.links.new(wscale.outputs["Value"], rough.inputs["Value"])
    rdirt = _n(nt, "ShaderNodeMath", 500, 0, operation="MULTIPLY_ADD", use_clamp=True)
    rdirt.inputs[1].default_value = 0.15
    nt.links.new(dirt.outputs["Result"], rdirt.inputs[0])
    nt.links.new(rough.outputs["Result"], rdirt.inputs[2])
    rvar = _n(nt, "ShaderNodeMath", 700, 0, operation="MULTIPLY", use_clamp=True)
    nt.links.new(rdirt.outputs["Value"], rvar.inputs[0])
    nt.links.new(motc.outputs[0], rvar.inputs[1])

    metal = _n(nt, "ShaderNodeMapRange", 300, -200)
    metal.inputs["To Min"].default_value = f["metal"]
    metal.inputs["To Max"].default_value = f["wear_metal"]
    nt.links.new(wscale.outputs["Value"], metal.inputs["Value"])

    # Surface relief: stippling on a grip, a fine cast/blast texture elsewhere.
    grain = _n(nt, "ShaderNodeTexVoronoi", -400, -1000)
    grain.inputs["Scale"].default_value = 520.0 if kind in ("grip", "rubber") else 420.0
    nt.links.new(tc.outputs["Object"], grain.inputs["Vector"])
    bump = _n(nt, "ShaderNodeBump", 800, -300)
    bump.inputs["Strength"].default_value = 0.30 * f["bump"]
    bump.inputs["Distance"].default_value = 0.0002
    nt.links.new(grain.outputs["Distance"], bump.inputs["Height"])

    nt.links.new(col.outputs[2], bsdf.inputs["Base Color"])
    nt.links.new(rvar.outputs["Value"], bsdf.inputs["Roughness"])
    nt.links.new(metal.outputs["Result"], bsdf.inputs["Metallic"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs[0], out.inputs["Surface"])
    _SOCKETS[name] = dict(out=out, bsdf=bsdf, emit=emit, color=col.outputs[2],
                         rough=rvar.outputs["Value"], metal=metal.outputs["Result"])
    return mat


def assign_hi(objs):
    for o in objs:
        if o.type == "MESH":
            o.data.materials.clear()
            o.data.materials.append(hi_material(o.get("hq_mat", "anod")))


def bake_pass(mode):
    """Routes every high material for one bake: 'bsdf' for NORMAL/AO, or a channel name."""
    for name, s in _SOCKETS.items():
        nt = bpy.data.materials[name].node_tree
        if mode == "bsdf":
            nt.links.new(s["bsdf"].outputs[0], s["out"].inputs["Surface"])
        else:
            nt.links.new(s[mode], s["emit"].inputs["Color"])
            nt.links.new(s["emit"].outputs[0], s["out"].inputs["Surface"])


# --- UV, bake, pack, export ---------------------------------------------------------------------

def use_gpu():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    found = []
    for kind in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = kind
            prefs.get_devices()
            found = [d for d in prefs.devices if d.type == kind]
        except TypeError:
            found = []
        if found:
            break
    for d in prefs.devices:
        d.use = d in found
    sc.cycles.device = "GPU" if found else "CPU"
    return sc.cycles.device


def triangulate(obj):
    """Fixed triangles before the unwrap and the bake, so the tangent basis the normal map is
    baked in is the one the exporter writes (a quad split differently in the engine would
    show the bake's seams)."""
    m = obj.modifiers.new("tri", "TRIANGULATE")
    m.quad_method = "BEAUTY"
    m.ngon_method = "BEAUTY"
    m.keep_custom_normals = True
    apply_mods(obj)


def unwrap(low, margin=0.004):
    activate(low)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(55), island_margin=margin,
                             area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    try:
        bpy.ops.uv.pack_islands(rotate=True, margin=margin, shape_method="CONCAVE")
    except TypeError:
        bpy.ops.uv.pack_islands(rotate=True, margin=margin)
    bpy.ops.object.mode_set(mode="OBJECT")


def _image(name, px, non_color, alpha=False):
    img = bpy.data.images.new(name, px, px, alpha=alpha, float_buffer=False)
    img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    return img


def bake(low, highs, px, samples=64):
    """Bakes highs onto low's atlas. Returns {channel: numpy HxWx4 float array}."""
    sc = bpy.context.scene
    use_gpu()
    sc.cycles.samples = samples
    sc.render.bake.use_selected_to_active = True
    sc.render.bake.cage_extrusion = 0.0015
    sc.render.bake.max_ray_distance = 0.004
    sc.render.bake.margin = 12
    sc.render.bake.margin_type = "EXTEND"
    if sc.world is None:
        sc.world = bpy.data.worlds.new("bake_world")
    sc.world.light_settings.distance = 0.03

    bmat = bpy.data.materials.new("bake_target")
    bmat.use_nodes = True
    low.data.materials.clear()
    low.data.materials.append(bmat)
    tex = bmat.node_tree.nodes.new("ShaderNodeTexImage")
    bmat.node_tree.nodes.active = tex

    out = {}
    jobs = [("normal", "NORMAL", "bsdf", True), ("ao", "AO", "bsdf", True),
            ("color", "EMIT", "color", False), ("rough", "EMIT", "rough", True),
            ("metal", "EMIT", "metal", True)]
    for chan, kind, route, nc in jobs:
        img = _image("bake_" + chan, px, nc)
        tex.image = img
        bake_pass(route)
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        for h in highs:
            h.select_set(True)
        low.select_set(True)
        bpy.context.view_layer.objects.active = low
        sc.cycles.samples = samples if kind == "AO" else max(8, samples // 4)
        bpy.ops.object.bake(type=kind, normal_space="TANGENT", use_clear=True)
        a = np.empty(px * px * 4, dtype=np.float32)
        img.pixels.foreach_get(a)
        out[chan] = a.reshape(px, px, 4)
    bake_pass("bsdf")
    return out


def save_png(name, arr, path, non_color):
    h, w, _ = arr.shape
    img = bpy.data.images.new(name, w, h, alpha=False)
    img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    img.pixels.foreach_set(np.ascontiguousarray(arr, dtype=np.float32).ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    return img


def finish_maps(maps, ao_in_albedo=0.45):
    """Packs the baked channels: albedo (with a share of the AO), ORM, normal."""
    ao = maps["ao"][..., :1]
    color = maps["color"].copy()
    color[..., :3] *= (1.0 - ao_in_albedo) + ao_in_albedo * ao
    color[..., 3] = 1.0
    orm = np.ones_like(color)
    orm[..., 0] = maps["ao"][..., 0]
    orm[..., 1] = maps["rough"][..., 0]
    orm[..., 2] = maps["metal"][..., 0]
    normal = maps["normal"].copy()
    normal[..., 3] = 1.0
    return color, orm, normal


def downscale(arr, px):
    """Resamples a baked map to px x px (the bake runs larger than what ships: the extra samples
    anti-alias the thin engraving and the normal map's edges). Returns a float array."""
    h = arr.shape[0]
    if px >= h:
        return arr
    img = bpy.data.images.new("ds", h, h, alpha=True, float_buffer=True)
    img.pixels.foreach_set(np.ascontiguousarray(arr, dtype=np.float32).ravel())
    img.scale(px, px)
    out = np.empty(px * px * 4, dtype=np.float32)
    img.pixels.foreach_get(out)
    bpy.data.images.remove(img)
    return out.reshape(px, px, 4)


def low_material(name, color_img, orm_img, normal_img):
    """The shipped material: Principled BSDF fed by the three images, with the occlusion wired
    into a 'glTF Material Output' group so the exporter writes it as the glTF occlusion map."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = _n(nt, "ShaderNodeOutputMaterial", 900, 0)
    bsdf = _n(nt, "ShaderNodeBsdfPrincipled", 600, 0)
    tc = _n(nt, "ShaderNodeTexImage", 0, 300, image=color_img)
    to = _n(nt, "ShaderNodeTexImage", 0, 0, image=orm_img)
    tn = _n(nt, "ShaderNodeTexImage", 0, -300, image=normal_img)
    sep = _n(nt, "ShaderNodeSeparateColor", 300, 0)
    nm = _n(nt, "ShaderNodeNormalMap", 300, -300)
    nt.links.new(tc.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(to.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs[1], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs[2], bsdf.inputs["Metallic"])
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs[0], out.inputs["Surface"])
    grp = bpy.data.node_groups.get("glTF Material Output")
    if grp is None:
        grp = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
        grp.interface.new_socket("Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
    g = nt.nodes.new("ShaderNodeGroup")
    g.node_tree = grp
    g.location = (600, -400)
    nt.links.new(sep.outputs[0], g.inputs["Occlusion"])
    return mat


def glass_material(name, tint=(0.02, 0.05, 0.06), emit=None):
    """An untextured extra material (a lens, a laser aperture). Shipped as plain factors."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*tint, 1)
    bsdf.inputs["Roughness"].default_value = 0.05
    bsdf.inputs["Metallic"].default_value = 0.0
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1)
        bsdf.inputs["Emission Strength"].default_value = 6.0
    return mat


EXPORT_TURN = Matrix.Rotation(math.pi, 4, "Z")


def export_glb(path, objs, origin_mm=None):
    """Turns everything half a circle about Z (muzzle to glTF +Z) about origin_mm, and writes
    objs (meshes and socket empties) as one GLB with the images embedded."""
    shift = Matrix.Translation(-Vector(origin_mm) * MM) if origin_mm is not None else Matrix()
    m = EXPORT_TURN @ shift
    # A new empty's matrix_world is identity until the depsgraph is evaluated: without this
    # every socket landed on the same point (the origin, turned).
    bpy.context.view_layer.update()
    for o in objs:
        if o.parent is None:
            o.matrix_world = m @ o.matrix_world
    for o in objs:
        if o.type == "EMPTY":
            # A socket keeps only its place: turned with the model it would carry the half turn
            # into every attachment parented to it, and a suppressor came out backwards.
            o.rotation_euler = (0, 0, 0)
            o.scale = (1, 1, 1)
    for o in objs:
        if o.type == "MESH" and o.parent is None:
            activate(o)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for o in bpy.context.view_layer.objects:
        o.select_set(o in objs)
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True, export_yup=True,
        export_apply=True, export_texcoords=True, export_normals=True, export_tangents=True,
        export_materials="EXPORT", export_image_format="AUTO", export_extras=False,
    )
