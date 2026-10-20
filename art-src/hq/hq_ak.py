# The AK-pattern rifle, part by part, in millimetres (hq_kit's frame: bore on +Y at z = 0, up +Z,
# the charging handle on +X): a stamped receiver with a ribbed dust cover, a gas tube over a
# 415 mm barrel, a slant muzzle brake, wood handguard, pistol grip and stock, a tangent rear
# sight on the barrel and a hooded front post, and a strongly curved 30-round magazine.
# build(hi) returns ({group: parts}, glass), see hq_m4.build.
import hq_kit as K
from hq_pistol import pin
from hq_m4 import magazine_parts

SIGHT_Z = 44.0           # tops of both sights: the aimed view's line runs parallel to the bore
MUZZLE = 472.0
SOCKETS = {
    "socket_optic": (0, -40, 26),
    "socket_muzzle": (0, MUZZLE, 0),
    "socket_underbarrel": (0, 300, -31),
    "socket_side": (20, 280, 0),
    "socket_magazine": (0, 24, -26),
    "sight_rear": (0, 205, SIGHT_Z),
    "sight_front": (0, 413, SIGHT_Z),
}


def receiver(hi):
    parts = []
    # The stamped body: a box open at the top, the dust cover closing it.
    body = K.profile("receiver", [(-112, -26), (-112, 14), (-100, 18), (186, 18), (194, 12), (194, -26)], -18.0, 18.0, "steel")
    # The magazine well's opening in the belly and the ejection port on the right.
    K.cut(body, K.box("well", (0, 24, -26), (22, 52, 14), None))
    K.cut(body, K.box("port", (18, 20, 8), (6, 70, 10), None))
    K.finish(body, hi, bevel_mm=0.9)
    parts.append(body)
    cover = K.profile("dust_cover", [(-108, 14), (-104, 24), (-60, 28), (80, 28), (170, 24), (188, 20), (188, 14)], -16.5, 16.5, "steel")
    # Three long ribs pressed into the cover.
    for sx in (1, -1):
        K.cut(cover, K.box("rib", (sx * 16.5, 30, 22), (2.4, 190, 2.2), None))
    K.finish(cover, hi, round_mm=3.0)
    parts.append(cover)
    # The trunnion block at the front of the receiver, riveted: three rivets a side.
    trun = K.profile("trunnion", [(168, -26), (168, 22), (214, 22), (214, -26)], -17.5, 17.5, "steel")
    parts.append(K.finish(trun, hi, bevel_mm=1.0))
    for sx in (1, -1):
        for y, z in ((-80, -14), (150, -14), (176, 10), (-90, 8)):
            parts.append(pin(y, z, sx, hi, r=3.0, name="rivet"))
    # Charging handle: a bar out of the right side with a hooked knob.
    bar = K.profile("charging_bar", [(0, 8), (26, 8), (26, 14), (0, 14)], 17.5, 20.5, "steel")
    parts.append(K.finish(bar, hi, bevel_mm=0.4))
    knob = K.lathe("charging_knob", [(20.5, 0), (20.5, 4.4), (36, 4.4), (38, 3.2), (38, 0)], 12 if not hi else 28, "steel", axis="X", centre=(0, 20, 11))
    parts.append(K.finish(knob, hi, bevel_mm=0.4))
    # Selector lever: a long plate down the right side.
    sel = K.profile("selector", [(-60, -6), (-18, -6), (-8, 6), (-60, 6)], 18.0, 19.4, "steel")
    parts.append(K.finish(sel, hi, bevel_mm=0.3))
    # Trigger guard and trigger.
    guard = K.profile("guard", [(-70, -24), (-70, -58), (-60, -64), (-8, -64), (4, -52), (4, -24)], -6, 6, "steel")
    K.cut(guard, K.profile("gin", [(-61, -26), (-61, -54), (-55, -58), (-14, -58), (-2, -50), (-2, -26)], -9, 9, None))
    parts.append(K.finish(guard, hi, bevel_mm=0.7))
    trig = K.profile("trigger", [(-40, -24), (-33, -24), (-31, -42), (-28, -52), (-37, -54), (-41, -42)], -2.4, 2.4, "steel")
    parts.append(K.finish(trig, hi, bevel_mm=0.5))
    return parts


def barrel(hi):
    parts = []
    n = 24 if not hi else 56
    b = K.lathe("barrel", [(194, 0), (194, 11.0), (400, 9.5), (432, 9.5), (432, 0)], n, "steel")
    parts.append(K.finish(b, hi, bevel_mm=0.4))
    # Gas tube over the barrel, with its vent slots, and the gas block under it.
    tube = K.lathe("gas_tube", [(262, 0), (262, 10.5), (404, 10.5), (404, 0)], n, "steel", centre=(0, 0, 25.0))
    for i in range(4):
        K.cut(tube, K.box("vent", (0, 372 + i * 6.5, 33), (14, 3.2, 8), None))
    parts.append(K.finish(tube, hi, bevel_mm=0.4))
    block = K.profile("gas_block", [(380, 8), (402, 8), (402, 34), (380, 34)], -9.5, 9.5, "steel")
    parts.append(K.finish(block, hi, bevel_mm=0.6))
    # Front sight base with a post and two protecting wings (a hood).
    base = K.profile("fs_base", [(402, 8), (424, 8), (424, 30), (402, 30)], -9, 9, "steel")
    parts.append(K.finish(base, hi, bevel_mm=0.5))
    for sx in (1, -1):
        wing = K.profile("fs_wing", [(408, 28), (420, 28), (420, SIGHT_Z - 4), (408, SIGHT_Z - 4)], sx * 4.4, sx * 6.4, "steel")
        parts.append(K.finish(wing, hi, bevel_mm=0.3))
    post = K.profile("fs_post", [(411, 28), (415, 28), (414.7, SIGHT_Z - 0.6), (414, SIGHT_Z), (412, SIGHT_Z), (411.3, SIGHT_Z - 0.6)], -1.3, 1.3, "steel")
    parts.append(K.finish(post, hi, bevel_mm=0.25))
    # Slant muzzle brake: a short drum with an angled cut across the top.
    brake = K.lathe("brake", [(432, 0), (432, 12.0), (436, 13.0), (MUZZLE - 2, 13.0), (MUZZLE, 11.5), (MUZZLE, 0)], n, "steel")
    K.cut(brake, K.cyl("bore", MUZZLE - 20, MUZZLE + 4, 4.3, 16 if not hi else 32, None))
    K.cut(brake, K.profile("slant", [(448, 7), (MUZZLE + 1, 7), (MUZZLE + 1, 20), (462, 20)], -20, 20, None))
    parts.append(K.finish(brake, hi, bevel_mm=0.45))
    # Cleaning rod under the barrel, with a swivel at the front.
    rod = K.cyl("rod", 330, 436, 2.6, 10 if not hi else 20, "steel", centre=(0, 0, -13.0))
    parts.append(K.finish(rod, hi, bevel_mm=0.2))
    return parts


def furniture(hi):
    parts = []
    # Lower handguard: wood, a barrel channel through it, finger-grooved on both sides.
    f = K.profile("handguard", [(176, -32), (176, 4), (184, 8), (350, 8), (358, 4), (358, -32), (350, -36), (184, -36)], -20.0, 20.0, "wood")
    K.cut(f, K.cyl("barrel_h", 170, 360, 11.4, 24, None))
    for sx in (1, -1):
        for i in range(4):
            K.cut(f, K.box("groove", (sx * 20, 218 + i * 28, -14), (3.2, 12, 20), None))
    K.finish(f, hi, round_mm=3.4)
    parts.append(f)
    # Upper handguard: a wood shell over the barrel, under the gas tube, wearing a sheet-steel ferrule.
    u = K.profile("upper_hg", [(236, 8), (380, 8), (380, 18), (370, 22), (246, 22), (236, 16)], -15.0, 15.0, "wood")
    K.cut(u, K.cyl("gas_h", 230, 385, 11.0, 24, None, centre=(0, 0, 25.0)))
    parts.append(K.finish(u, hi, round_mm=2.6))
    # Pistol grip, wood, raked.
    g = [(-96, -24), (-132, -24), (-142, -34), (-156, -112), (-146, -124), (-126, -122), (-108, -50), (-98, -36)]
    parts.append(K.finish(K.profile("grip", g, -15.0, 15.0, "wood"), hi, round_mm=3.6))
    # Stock: wood, a gentle drop, the comb well under the sights.
    s = [(-112, 14), (-250, 12), (-340, 17), (-384, 17), (-390, -88), (-376, -96), (-300, -66), (-200, -40), (-112, -30)]
    st = K.profile("stock", s, -16.0, 16.0, "wood")
    for sx in (1, -1):
        K.cut(st, K.profile("pocket", [(-196, 0), (-290, 4), (-330, -22), (-318, -42), (-220, -22)], sx * 14.0, sx * 17, None))
    K.finish(st, hi, round_mm=3.0)
    parts.append(st)
    pad = K.profile("butt_plate", [(-384, 18), (-392, 18), (-396, -90), (-388, -97), (-386, -88)], -16.8, 16.8, "steel")
    parts.append(K.finish(pad, hi, bevel_mm=0.9))
    return parts


def rear_sight(hi):
    parts = []
    # A ramp block on the barrel with a tangent leaf on it, notch at SIGHT_Z.
    base = K.profile("rs_base", [(194, 16), (258, 16), (258, 30), (250, 34), (202, 34), (194, 30)], -9.5, 9.5, "steel")
    K.cut(base, K.box("slot", (0, 216, 34), (6, 40, 4), None))
    parts.append(K.finish(base, hi, bevel_mm=0.6))
    leaf = K.profile("rs_leaf", [(200, 30), (226, 30), (222, SIGHT_Z), (204, SIGHT_Z)], -6.5, 6.5, "steel")
    K.cut(leaf, K.box("notch", (0, 205, SIGHT_Z), (4.0, 22, 6.5), None))
    parts.append(K.finish(leaf, hi, bevel_mm=0.35))
    return parts


def markings():
    return [K.text("mk_l", "TMC ARMORY  AR-7  7.62 X 39", 3.0, (-18.15, 20, -8.0), "-X", "paint"),
            K.text("mk_ser", "SER  TMC76239", 2.2, (-16.1, -60, 18.0), "-X", "paint"),
            K.text("mk_r", "7.62", 3.0, (18.15, 70, -12.0), "+X", "paint")]


def build(hi):
    body = receiver(hi) + barrel(hi) + furniture(hi)
    if hi:
        body += markings()
    mag = magazine_parts("magazine", hi, length=170.0, curve=0.32, mat="magalu", window=False, depth=44.0)
    for p in mag:
        K.transform(p, K.at((0, 24, -26)))
    return {"body": body, "magazine": mag, "rear_sight": rear_sight(hi)}, []
