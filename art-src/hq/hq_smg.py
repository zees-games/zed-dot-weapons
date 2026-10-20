# The compact submachine gun, part by part, in millimetres (hq_kit's frame: bore on +Y at z = 0,
# up +Z, the ejection port on +X): a square receiver with a top rail, a vented handguard and an
# integral suppressor shroud, a pistol grip with the magazine ahead of it, flip-up iron sights
# and a short collapsed stock. build(hi) returns ({group: parts}, glass), see hq_m4.build.
import math

import hq_kit as K
import hq_m4
from hq_pistol import pin

RAIL_BASE = 21.5
RAIL_TOP = 26.5
HG_BACK = 34.0
HG_FRONT = 176.0
MUZZLE_END = 252.0
SIGHT_Z = 40.0
SOCKETS = {
    "socket_optic": (0, -58, RAIL_TOP),
    "socket_muzzle": (0, MUZZLE_END, 0),
    "socket_underbarrel": (0, 120, -RAIL_BASE),
    "socket_side": (RAIL_BASE, 110, 0),
    "socket_magazine": (0, 6, -22),
    "sight_rear": (0, -98, SIGHT_Z),
    "sight_front": (0, 162.5, SIGHT_Z),
}


def receiver(hi):
    parts = []
    pts = [(-128, -22), (-128, 18), (-122, 22), (HG_BACK, 22), (HG_BACK, -22)]
    r = K.profile("receiver", pts, -13.0, 13.0, "anod")
    for sx in (1, -1):
        K.cut(r, K.profile_x("w", [(sx * 13.2, 17), (sx * 13.2, 22.5), (sx * 9, 22.5)], -130, 40, None))
    K.cut(r, K.box("port", (13.0, -52, 5), (2.8, 48, 15), None))
    K.cut(r, K.box("tslot", (0, -44, -22), (7, 26, 8), None))
    # Pockets in the sides, the stamped look.
    for sx in (1, -1):
        K.cut(r, K.box("pocket", (sx * 12.7, -92, -6), (1.2, 40, 18), None))
    K.finish(r, hi, bevel_mm=0.9)
    parts.append(r)
    bolt = K.box("bolt", (12.0, -54, 5), (1.2, 40, 9), "steel")
    parts.append(K.finish(bolt, hi, bevel_mm=0.3))
    defl = K.profile("deflector", [(-78, -2), (-70, -2), (-70, 14), (-76, 14), (-78, 8)], 13, 19, "anod")
    parts.append(K.finish(defl, hi, bevel_mm=0.7))
    parts.append(hq_m4.rail("top_rail", -122, HG_BACK, "top", RAIL_BASE, hi, top=RAIL_TOP))
    # The cocking handle on the left: a knob on a stem, in a slot.
    ch = K.lathe("cocking", [(-13, 0), (-13, 4), (-21, 4), (-23.5, 6.5), (-27, 6.5), (-27, 0)], 12 if not hi else 32, "steel", axis="X", centre=(0, -66, 10))
    parts.append(K.finish(ch, hi, bevel_mm=0.4))
    # End cap and the stock hinge.
    cap = K.profile("end_cap", [(-134, -22), (-128, -22), (-128, 18), (-134, 18)], -12, 12, "steel")
    parts.append(K.finish(cap, hi, bevel_mm=0.5))
    for y in (-110, 18):
        for sx in (1, -1):
            parts.append(pin(y, -16, sx, hi, r=3.4, name="pin"))
    return parts


def lower(hi):
    parts = []
    well = K.profile("magwell", [(-14, -22), (34, -22), (36, -62), (-12, -62)], -12.8, 12.8, "anod")
    K.finish(well, hi, bevel_mm=0.8)
    parts.append(well)
    g = [(-64, -20), (-98, -20), (-100, -30), (-114, -102), (-110, -110), (-90, -110), (-64, -38)]
    grip = K.profile("grip", g, -14, 14, "grip")
    parts.append(K.finish(grip, hi, round_mm=3.6))
    guard = K.profile("guard", [(-64, -22), (-64, -52), (-58, -58), (-28, -58), (-18, -48), (-18, -22)], -5, 5, "anod")
    K.cut(guard, K.profile("gin", [(-59, -20), (-59, -47), (-54, -52), (-31, -52), (-24, -45), (-24, -20)], -8, 8, None))
    parts.append(K.finish(guard, hi, bevel_mm=0.7))
    trig = K.profile("trigger", [(-46, -22), (-41, -22), (-40, -34), (-37, -43), (-44, -45), (-46, -34)], -2.2, 2.2, "steel")
    parts.append(K.finish(trig, hi, bevel_mm=0.5))
    sel = K.profile("selector", [(-90, -6), (-76, -8), (-75, -12), (-89, -11)], -15, -12.6, "steel")
    parts.append(K.finish(sel, hi, bevel_mm=0.4))
    hub = K.cyl("sel_hub", -12.6, -15.5, 5.0, 12 if not hi else 32, "steel", axis="X", centre=(0, -88, -8.5))
    parts.append(K.finish(hub, hi, bevel_mm=0.4))
    parts.append(pin(-52, -30, 1, hi, r=4.2, name="mag_release"))
    return parts


def stock(hi):
    parts = []
    hinge = K.box("hinge", (0, -140, 0), (24, 12, 40), "steel")
    parts.append(K.finish(hinge, hi, bevel_mm=0.8))
    s = [(-138, 14), (-138, -12), (-152, -14), (-232, -72), (-248, -78), (-262, -78), (-262, 6), (-254, 16)]
    st = K.profile("stock", s, -11, 11, "poly")
    for sx in (1, -1):
        K.cut(st, K.profile("win", [(-170, -6), (-226, -52), (-238, -52), (-238, -22), (-196, 4)], sx * 8.5, sx * 12, None))
    K.finish(st, hi, bevel_mm=1.0)
    parts.append(st)
    pad = K.profile("butt_pad", [(-262, 6), (-270, 6), (-272, 0), (-272, -76), (-268, -80), (-262, -80)], -12, 12, "rubber")
    for z in range(-70, 0, 9):
        K.cut(pad, K.box("rib", (0, -272.5, z), (30, 2.0, 2.2), None))
    parts.append(K.finish(pad, hi, bevel_mm=1.2))
    return parts


def front(hi):
    parts = []
    segs = 8
    r = 21.0 / math.cos(math.pi / segs)
    hg = K.lathe("handguard", [(HG_BACK, 0), (HG_BACK, r), (HG_FRONT, r), (HG_FRONT, 0)], segs, "anod", phase=math.pi / segs)
    vents = []
    for k in range(4):
        ang = 45 + 90 * k
        for i in range(5):
            v = K.merge("vent", [K.box("vslot", (0, 0, 0), (9, 12, 8.0), None),
                                 K.cyl("vend", -4.5, 4.5, 4.0, 12, None, axis="X", centre=(0, -6, 0)),
                                 K.cyl("vend", -4.5, 4.5, 4.0, 12, None, axis="X", centre=(0, 6, 0))])
            K.transform(v, K.at((0, 62 + i * 22, 0)) @ K.rot_y(ang) @ K.at((21.5, 0, 0)))
            vents.append(v)
    K.cut(hg, K.merge("vents", vents))
    K.cut(hg, K.cyl("bore", HG_BACK - 3, HG_FRONT + 3, 12.0, 16, None))
    K.finish(hg, hi, bevel_mm=0.8)
    parts.append(hg)
    parts.append(hq_m4.rail("hg_top", HG_BACK + 2, HG_FRONT - 2, "top", RAIL_BASE, hi, top=RAIL_TOP))
    for side in ("bottom", "right", "left"):
        parts.append(hq_m4.rail("hg_" + side, HG_BACK + 6, HG_FRONT - 6, side, RAIL_BASE - 1.5, hi, top=RAIL_BASE + 3.0))
    # Integral suppressor: a jacket over the barrel, ringed, closed by a cap with the bore through it.
    n = 20 if not hi else 48
    jacket = K.lathe("jacket", [(HG_FRONT, 0), (HG_FRONT, 14.5), (MUZZLE_END - 8, 14.5), (MUZZLE_END - 8, 15.6),
                                (MUZZLE_END - 3, 15.6), (MUZZLE_END - 2, 12.5), (MUZZLE_END, 12.5), (MUZZLE_END, 0)], n, "steel")
    K.cut(jacket, K.cyl("jbore", MUZZLE_END - 8, MUZZLE_END + 3, 4.8, 16, None))
    rings = []
    for y in (HG_FRONT + 22, HG_FRONT + 44, HG_FRONT + 66):
        rings.append(K.cyl("gr", y, y + 2.4, 16.5, 20 if not hi else 40, None))
    # Grooves cut round the jacket, with a smaller radius body behind them.
    for c in rings:
        pass
    parts.append(K.finish(jacket, hi, bevel_mm=0.4))
    for y in (HG_FRONT + 22, HG_FRONT + 44, HG_FRONT + 66):
        ring = K.lathe("band", [(y, 0), (y, 15.7), (y + 2.6, 15.7), (y + 2.6, 0)], n, "anod")
        parts.append(K.finish(ring, hi, bevel_mm=0.3))
    # Front sight on the handguard's rail: base, wings, post (its tip at SIGHT_Z).
    base = K.profile("fs_base", [(154, RAIL_TOP), (172, RAIL_TOP), (170, 32), (156, 32)], -8.5, 8.5, "steel")
    parts.append(K.finish(base, hi, bevel_mm=0.5))
    for sx in (1, -1):
        w = K.profile("fs_wing", [(157, 32), (167, 32), (167, 42), (157, 42)], sx * 4.2, sx * 7.0, "steel")
        parts.append(K.finish(w, hi, bevel_mm=0.4))
    post = K.profile("fs_post", [(160, 32), (165, 32), (164.4, SIGHT_Z - 0.6), (163.6, SIGHT_Z), (161.4, SIGHT_Z), (160.6, SIGHT_Z - 0.6)], -1.3, 1.3, "steel")
    parts.append(K.finish(post, hi, bevel_mm=0.25))
    return parts


def rear_sight(hi):
    parts = []
    base = K.profile("rs_base", [(-108, RAIL_TOP), (-88, RAIL_TOP), (-88, RAIL_TOP + 4), (-91, RAIL_TOP + 6.5),
                                 (-105, RAIL_TOP + 6.5), (-108, RAIL_TOP + 4)], -11, 11, "anod")
    parts.append(K.finish(base, hi, bevel_mm=0.6))
    for sx in (1, -1):
        w = K.profile("rs_wing", [(-104, RAIL_TOP + 5), (-92, RAIL_TOP + 5), (-93, 46), (-103, 46)], sx * 6.8, sx * 9.6, "anod")
        parts.append(K.finish(w, hi, bevel_mm=0.5))
    leaf = K.profile("rs_leaf", [(-100, RAIL_TOP + 5), (-95, RAIL_TOP + 5), (-95.6, 46), (-99.4, 46)], -5.8, 5.8, "steel")
    K.cut(leaf, K.cyl("aperture", -104, -90, 1.4, 12, None, centre=(0, 0, SIGHT_Z)))
    parts.append(K.finish(leaf, hi, bevel_mm=0.3))
    return parts


def markings():
    t = []
    t.append(K.text("mk_l", "TMC ARMORY  SMG 9 MM", 3.0, (-12.85, -30, 4.0), "-X", "paint"))
    t.append(K.text("mk_safe", "SAFE  SEMI  AUTO", 2.0, (-12.85, -92, -18.0), "-X", "paint"))
    t.append(K.text("mk_ser", "SER  TMC03318", 2.2, (-12.85, -20, -14.0), "-X", "paint"))
    t.append(K.text("mk_r", "9 X 19", 3.0, (12.85, -100, 0.0), "+X", "paint"))
    return t


def build(hi):
    body = receiver(hi) + lower(hi) + stock(hi) + front(hi)
    mag = hq_m4.magazine_parts("magazine", hi, length=150.0, curve=0.07, depth=40.0)
    for p in mag:
        K.transform(p, K.at(SOCKETS["socket_magazine"]))
    if hi:
        body += markings()
    return {"body": body, "magazine": mag, "rear_sight": rear_sight(hi)}, []
