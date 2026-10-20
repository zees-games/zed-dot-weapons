# The pump shotgun, part by part, in millimetres (hq_kit's frame: bore on +Y at z = 0, up +Z,
# the ejection port on +X): an 18-inch barrel with a tube magazine under it, a fore-end that
# slides on the tube, a steel receiver with a loading port in its belly, a ghost-ring rear sight
# and a post at the muzzle, and a polymer stock with a pistol grip.
# build(hi) returns ({group: parts}, glass), see hq_m4.build.
import math

import hq_kit as K
from hq_pistol import pin

BARREL_R = 10.5
TUBE_Z = -23.0
TUBE_R = 9.6
MUZZLE = 500.0
SIGHT_Z = 44.0
SOCKETS = {
    "socket_optic": (0, -24, 22),
    "socket_muzzle": (0, MUZZLE, 0),
    "socket_underbarrel": (0, 320, -44),
    "socket_side": (17, 170, -12),
    "sight_rear": (0, -86, SIGHT_Z),
    "sight_front": (0, 492, SIGHT_Z),
}


def receiver(hi):
    parts = []
    pts = [(-102, -30), (-102, 18), (-96, 22), (40, 22), (46, 16), (46, -30)]
    r = K.profile("receiver", pts, -14.0, 14.0, "steel")
    for sx in (1, -1):
        K.cut(r, K.profile_x("w", [(sx * 14.2, 17), (sx * 14.2, 22.5), (sx * 10, 22.5)], -105, 50, None))
    # Ejection port on the right, the loading port in the belly.
    K.cut(r, K.box("port", (14.0, -26, 6), (3.6, 56, 14), None))
    K.cut(r, K.box("load", (0, -4, -30), (15, 56, 8), None))
    # Scallops on the sides, the milled look.
    for sx in (1, -1):
        K.cut(r, K.box("scallop", (sx * 13.7, -66, -6), (1.4, 44, 22), None))
    K.finish(r, hi, bevel_mm=0.9)
    parts.append(r)
    bolt = K.box("bolt", (11.6, -26, 6), (1.2, 46, 8), "anod")
    parts.append(K.finish(bolt, hi, bevel_mm=0.3))
    # Shell stop and carrier showing in the loading port.
    carrier = K.box("carrier", (0, -4, -26.5), (11, 40, 2.4), "anod")
    parts.append(K.finish(carrier, hi, bevel_mm=0.3))
    for y in (-92, 36):
        for sx in (1, -1):
            parts.append(pin(y, -14, sx, hi, r=3.6, name="pin"))
    # Safety: a cross-bolt button through the back of the trigger guard.
    sb = K.lathe("safety", [(-9, 0), (-9, 4.2), (9, 4.2), (9, 0)], 14 if not hi else 32, "steel", axis="X", centre=(0, -78, -34))
    parts.append(K.finish(sb, hi, bevel_mm=0.4))
    return parts


def lower(hi):
    parts = []
    guard = K.profile("guard", [(-86, -30), (-86, -60), (-80, -66), (-30, -66), (-18, -52), (-18, -30)], -6, 6, "steel")
    K.cut(guard, K.profile("gin", [(-77, -28), (-77, -57), (-73, -61), (-36, -61), (-27, -51), (-27, -28)], -9, 9, None))
    parts.append(K.finish(guard, hi, bevel_mm=0.8))
    trig = K.profile("trigger", [(-56, -30), (-51, -30), (-50, -42), (-46, -52), (-54, -54), (-56, -42)], -2.4, 2.4, "steel")
    parts.append(K.finish(trig, hi, bevel_mm=0.5))
    g = [(-104, -26), (-142, -26), (-148, -36), (-162, -100), (-154, -108), (-136, -108), (-124, -66), (-117, -40)]
    parts.append(K.finish(K.profile("grip", g, -14.5, 14.5, "grip"), hi, round_mm=3.6))
    return parts


def stock(hi):
    parts = []
    s = [(-100, 20), (-215, 18), (-338, 8), (-350, 4), (-354, -70), (-344, -76), (-300, -62), (-215, -34), (-100, -30)]
    st = K.profile("stock", s, -15.5, 15.5, "poly")
    for sx in (1, -1):
        K.cut(st, K.profile("pocket", [(-196, 4), (-262, 6), (-306, -20), (-300, -40), (-228, -16)], sx * 13.6, sx * 17, None))
    K.finish(st, hi, round_mm=2.6)
    parts.append(st)
    pad = K.profile("butt_pad", [(-354, 6), (-364, 6), (-366, -72), (-356, -78)], -16.5, 16.5, "rubber")
    for z in range(-70, 2, 9):
        K.cut(pad, K.box("rib", (0, -366.5, z), (36, 2.0, 2.2), None))
    parts.append(K.finish(pad, hi, bevel_mm=1.4))
    return parts


def barrel(hi):
    parts = []
    n = 24 if not hi else 56
    b = K.lathe("barrel", [(40, 0), (40, BARREL_R), (MUZZLE - 6, BARREL_R), (MUZZLE - 1, BARREL_R - 0.8), (MUZZLE, BARREL_R - 1.2), (MUZZLE, 0)], n, "steel")
    K.cut(b, K.cyl("bore", MUZZLE - 60, MUZZLE + 4, 8.2, 20 if not hi else 40, None))
    parts.append(K.finish(b, hi, bevel_mm=0.4))
    t = K.lathe("tube", [(40, 0), (40, TUBE_R), (440, TUBE_R), (440, 0)], 20 if not hi else 40, "steel", centre=(0, 0, TUBE_Z))
    parts.append(K.finish(t, hi, bevel_mm=0.3))
    cap = K.lathe("tube_cap", [(440, 0), (440, 11.2), (452, 11.2), (454, 9.6), (454, 0)], 20 if not hi else 40, "anod", centre=(0, 0, TUBE_Z))
    parts.append(K.finish(cap, hi, bevel_mm=0.5))
    web = K.box("web", (0, 240, -12), (5, 400, 7), "steel")
    parts.append(K.finish(web, hi, bevel_mm=0.3))
    band = K.profile_x("band", [(-8.5, 12), (8.5, 12), (12, 9), (12, -30), (8.5, -34), (-8.5, -34), (-12, -30), (-12, 9)], 408, 424, "anod")
    parts.append(K.finish(band, hi, bevel_mm=0.7))
    # Front sight: a ramp with a post, its tip at SIGHT_Z.
    ramp = K.profile("fs_ramp", [(470, 8.5), (496, 8.5), (495, 15), (486, 19), (474, 19)], -5, 5, "steel")
    parts.append(K.finish(ramp, hi, bevel_mm=0.5))
    post = K.profile("fs_post", [(489.5, 18), (494, 18), (493.6, SIGHT_Z - 0.8), (492.8, SIGHT_Z), (490.7, SIGHT_Z), (489.9, SIGHT_Z - 0.8)], -1.4, 1.4, "steel")
    parts.append(K.finish(post, hi, bevel_mm=0.25))
    return parts


def foreend(hi):
    parts = []
    f = K.profile("foreend", [(140, -2), (292, -2), (300, -10), (300, -42), (292, -50), (140, -50), (132, -42), (132, -10)], -17.5, 17.5, "poly")
    K.cut(f, K.cyl("tube_h", 125, 305, TUBE_R + 0.4, 20, None, centre=(0, 0, TUBE_Z)))
    K.cut(f, K.cyl("barrel_h", 125, 305, BARREL_R + 0.3, 24, None))
    # Ribs across the grip surface, both sides and underneath.
    cuts = []
    for i in range(9):
        y = 168 + i * 11
        for sx in (1, -1):
            cuts.append(K.box("rib", (sx * 17.5, y, -26), (2.4, 3.2, 28), None))
        cuts.append(K.box("rib", (0, y, -50), (28, 3.2, 2.4), None))
    K.cut(f, K.merge("ribs", cuts))
    K.finish(f, hi, round_mm=3.0)
    parts.append(f)
    # Action bars: two rods from the fore-end back toward the receiver.
    for sx in (1, -1):
        bar = K.cyl("action_bar", 40, 140, 2.6, 10 if not hi else 20, "steel", centre=(sx * 11, 0, -12))
        parts.append(K.finish(bar, hi, bevel_mm=0.2))
    return parts


def rear_sight(hi):
    parts = []
    base = K.profile("rs_base", [(-104, 22), (-70, 22), (-70, 26), (-76, 29.0), (-98, 29.0), (-104, 26)], -9, 9, "steel")
    parts.append(K.finish(base, hi, bevel_mm=0.5))
    ring = K.profile("ghost_ring", [(-90, 22), (-82, 22), (-83, SIGHT_Z + 7), (-89, SIGHT_Z + 7)], -7, 7, "steel")
    K.cut(ring, K.cyl("aperture", -95, -78, 3.6, 16 if not hi else 32, None, centre=(0, 0, SIGHT_Z)))
    parts.append(K.finish(ring, hi, bevel_mm=0.3))
    return parts


def markings():
    return [K.text("mk_l", "TMC ARMORY  PUMP 12 GA", 3.0, (-13.85, -30, -6.0), "-X", "paint"),
            K.text("mk_ser", "SER  TMC07744", 2.2, (-13.85, -64, 10.0), "-X", "paint"),
            K.text("mk_r", "12 GA  3 IN", 2.6, (13.85, -66, -6.0), "+X", "paint")]


def build(hi):
    body = receiver(hi) + lower(hi) + stock(hi) + barrel(hi) + foreend(hi)
    if hi:
        body += markings()
    return {"body": body, "rear_sight": rear_sight(hi)}, []
