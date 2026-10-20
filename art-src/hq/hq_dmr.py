# The bolt-action marksman rifle, part by part, in millimetres (hq_kit's frame: bore on +Y at
# z = 0, up +Z, the bolt handle on +X): a heavy 600 mm barrel with a ported brake, a round
# receiver with a top rail and a bolt knob, a fore-end, a thumbhole-free polymer stock with an
# adjustable cheek piece, a five-round box magazine and a fixed 6-24x scope on rings.
# The scope is part of the rifle (the pack's `_scoped` art looks through it), so it is in
# `body` and the sight marks sit on its axis.
# build(hi) returns ({group: parts}, glass), see hq_m4.build.
import hq_kit as K
from hq_pistol import pin
from hq_m4 import magazine_parts

AXIS = 46.0              # the scope's axis: the aimed view's line
MUZZLE = 640.0
SOCKETS = {
    "socket_muzzle": (0, MUZZLE, 0),
    "socket_underbarrel": (0, 360, -34),
    "socket_side": (18, 300, 0),
    "socket_magazine": (0, 6, -30),
    "sight_rear": (0, -52, AXIS),
    "sight_front": (0, 160, AXIS),
}


def receiver(hi):
    parts = []
    n = 28 if not hi else 64
    # The round action: a tube with a flat-bottomed block under it for the magazine well.
    tube = K.lathe("action", [(-80, 0), (-80, 17.5), (-74, 18.5), (170, 18.5), (176, 17.0), (176, 0)], n, "steel")
    # Ejection port on the right, the bolt visible in it.
    K.cut(tube, K.box("port", (15, 40, 8), (14, 58, 14), None))
    parts.append(K.finish(tube, hi, bevel_mm=0.6))
    block = K.profile("well", [(-60, -8), (-60, -34), (-52, -38), (60, -38), (68, -34), (68, -8)], -15, 15, "steel")
    K.cut(block, K.box("mag", (0, 6, -38), (22, 56, 12), None))
    parts.append(K.finish(block, hi, bevel_mm=0.8))
    # Top rail: a bridge across the action with cross slots.
    rail = K.profile_x("rail", [(-10.5, 17), (10.5, 17), (10.5, 20.5), (-10.5, 20.5)], -70, 168, "anod")
    cuts = [K.box("slot", (0, -64 + i * 8.0, 20.5), (22, 3.0, 2.4), None) for i in range(28)]
    K.cut(rail, K.merge("slots", cuts))
    parts.append(K.finish(rail, hi, bevel_mm=0.5))
    # Bolt body and shroud at the back, a cocking piece sticking out of it.
    shroud = K.lathe("shroud", [(-124, 0), (-124, 11.0), (-120, 12.2), (-80, 12.2), (-80, 0)], n, "steel")
    parts.append(K.finish(shroud, hi, bevel_mm=0.5))
    cock = K.lathe("cocking", [(-132, 0), (-132, 5.0), (-124, 5.0), (-124, 0)], 14 if not hi else 32, "steel")
    parts.append(K.finish(cock, hi, bevel_mm=0.4))
    # Bolt handle: a stem raked back and down, and a round knob.
    stem = K.cyl("bolt_stem", 17, 68, 4.4, 12 if not hi else 28, "steel", axis="X", centre=(0, 24, 4))
    parts.append(K.finish(stem, hi, bevel_mm=0.3))
    knob = K.lathe("bolt_knob", [(68, 0), (68, 5.0), (74, 10.5), (88, 11.5), (96, 8.0), (98, 0)], 16 if not hi else 40, "grip", axis="X", centre=(0, 24, 4))
    parts.append(K.finish(knob, hi, bevel_mm=0.8))
    for sx in (1, -1):
        parts.append(pin(120, -12, sx, hi, r=4.0, name="pin"))
        parts.append(pin(-40, -26, sx, hi, r=4.0, name="pin"))
    return parts


def barrel(hi):
    parts = []
    n = 28 if not hi else 64
    prof = [(170, 0), (170, 15.5), (330, 15.0), (MUZZLE - 60, 12.2), (MUZZLE - 44, 12.2), (MUZZLE - 44, 0)]
    b = K.lathe("barrel", prof, n, "steel")
    parts.append(K.finish(b, hi, bevel_mm=0.5))
    # Muzzle brake: a fat cylinder with side ports, and a bore.
    br = K.lathe("brake", [(MUZZLE - 44, 0), (MUZZLE - 44, 15.5), (MUZZLE - 40, 16.5), (MUZZLE - 4, 16.5), (MUZZLE, 14.5), (MUZZLE, 0)], n, "anod")
    ports = []
    for i in range(3):
        y = MUZZLE - 34 + i * 10
        ports.append(K.box("port", (0, y, 0), (40, 4.2, 6.0), None))
    K.cut(br, K.merge("ports", ports))
    K.cut(br, K.cyl("bore", MUZZLE - 50, MUZZLE + 4, 5.2, 16 if not hi else 32, None))
    parts.append(K.finish(br, hi, bevel_mm=0.45))
    # Recoil lug and a clamp ring where the barrel leaves the action.
    ring = K.lathe("nut", [(168, 0), (168, 21), (190, 21), (190, 0)], n, "steel")
    parts.append(K.finish(ring, hi, bevel_mm=0.8))
    return parts


def stock(hi):
    parts = []
    # Chassis side profile; the comb stays below the scope (AXIS - tube radius), z <= 22.
    s = [(-124, 12), (-210, 14), (-300, 20), (-380, 22), (-392, 18), (-396, -70), (-380, -80), (-330, -70),
         (-230, -34), (-136, -34), (-110, -26), (-80, -26), (-80, 12)]
    st = K.profile("stock", s, -16.0, 16.0, "poly")
    for sx in (1, -1):
        K.cut(st, K.profile("pocket", [(-230, 4), (-312, 6), (-352, -18), (-340, -40), (-250, -20)], sx * 14.0, sx * 17, None))
    K.finish(st, hi, round_mm=3.0)
    parts.append(st)
    pad = K.profile("butt_pad", [(-392, 18), (-402, 18), (-406, -70), (-398, -80), (-396, -70)], -17, 17, "rubber")
    for z in range(-66, 14, 10):
        K.cut(pad, K.box("rib", (0, -406.5, z), (36, 2.0, 2.2), None))
    parts.append(K.finish(pad, hi, bevel_mm=1.4))
    # Pistol grip and trigger guard.
    g = [(-80, -26), (-110, -26), (-128, -40), (-150, -120), (-140, -128), (-118, -126), (-92, -60), (-72, -40)]
    parts.append(K.finish(K.profile("grip", g, -14.5, 14.5, "grip"), hi, round_mm=3.4))
    guard = K.profile("guard", [(-72, -36), (-72, -62), (-64, -68), (-8, -68), (6, -54), (6, -38)], -6, 6, "steel")
    K.cut(guard, K.profile("gin", [(-64, -38), (-64, -58), (-58, -62), (-14, -62), (-2, -52), (-2, -38)], -9, 9, None))
    parts.append(K.finish(guard, hi, bevel_mm=0.7))
    trig = K.profile("trigger", [(-40, -38), (-34, -38), (-33, -50), (-30, -58), (-38, -60), (-41, -50)], -2.4, 2.4, "steel")
    parts.append(K.finish(trig, hi, bevel_mm=0.5))
    return parts


def foreend(hi):
    parts = []
    f = K.profile("foreend", [(176, -34), (176, 12), (190, 18), (400, 18), (410, 12), (410, -30), (400, -38), (190, -38)], -19.0, 19.0, "poly")
    K.cut(f, K.cyl("barrel_h", 170, 415, 15.8, 28, None))
    cuts = []
    for i in range(6):
        y = 214 + i * 30
        for sx in (1, -1):
            cuts.append(K.box("vent", (sx * 19, y, -8), (3.0, 18, 14), None))
    K.cut(f, K.merge("vents", cuts))
    K.finish(f, hi, round_mm=3.0)
    parts.append(f)
    # Sling stud and a rail section under the fore-end.
    rail = K.profile_x("urail", [(-9.5, -38), (9.5, -38), (9.5, -42), (-9.5, -42)], 300, 400, "anod")
    parts.append(K.finish(rail, hi, bevel_mm=0.4))
    return parts


def scope(hi):
    parts = []
    a = AXIS
    n = 28 if not hi else 72
    for y in (-26, 70):
        base = K.profile("sc_base", [(y - 14, 20.5), (y + 14, 20.5), (y + 14, 24), (y - 14, 24)], -12, 12, "anod")
        parts.append(K.finish(base, hi, bevel_mm=0.6))
        lowr = K.lathe("sc_ring", [(y - 9, 16.0), (y - 9, 21.5), (y + 9, 21.5), (y + 9, 16.0)], n, "anod", centre=(0, 0, a))
        parts.append(K.finish(lowr, hi, bevel_mm=0.6))
        web = K.profile("sc_web", [(y - 9, 22), (y + 9, 22), (y + 9, a - 18), (y - 9, a - 18)], -8, 8, "anod")
        parts.append(K.finish(web, hi, bevel_mm=0.6))
    # Solid to the axis with a shallow recess at each end (a hollow bore baked black).
    prof = [(-118, 0), (-118, 17.0), (-124, 18.0), (-124, 22.0), (-96, 22.0), (-90, 18.0), (-80, 16.0),
            (110, 16.0), (120, 18.5), (136, 26.0), (200, 26.0), (204, 25.0), (204, 22.5), (192, 22.0), (192, 0)]
    body = K.lathe("sc_tube", prof, n, "anod", centre=(0, 0, a))
    parts.append(K.finish(body, hi, bevel_mm=0.5))
    # Turrets: elevation on top, windage on the right, each a drum with a knurled cap.
    for axis in ("Z", "X"):
        t = K.lathe("sc_turret", [(15, 0), (15, 10.0), (21, 10.0), (21.5, 9.0), (30, 9.0), (30.5, 8.0), (30.5, 0)],
                    16 if not hi else 48, "anod", axis=axis, centre=(0, 0, 0) if axis == "Z" else (0, 20, a))
        if axis == "Z":
            K.transform(t, K.at((0, 20, a)))
        parts.append(K.finish(t, hi, bevel_mm=0.4))
    # Parallax wheel on the left, at the objective end.
    wheel = K.lathe("sc_wheel", [(-15, 0), (-15, 8.5), (-24, 8.5), (-24, 0)], 16 if not hi else 40, "anod", axis="X", centre=(0, 150, a))
    parts.append(K.finish(wheel, hi, bevel_mm=0.4))
    # Objective sun shade.
    shade = K.lathe("sc_shade", [(200, 24.0), (200, 27.0), (226, 27.0), (226, 24.0)], n, "anod", centre=(0, 0, a))
    parts.append(K.finish(shade, hi, bevel_mm=0.5))
    glass = [K.cyl("sc_lens_f", 203.2, 203.7, 22.0, 28, "glass", centre=(0, 0, a)),
             K.cyl("sc_lens_r", -123.8, -123.3, 19.0, 28, "glass", centre=(0, 0, a))]
    return parts, glass


def markings():
    return [K.text("mk_l", "TMC ARMORY  MARKSMAN .308", 3.0, (-19.2, 230, -8.0), "-X", "paint"),
            K.text("mk_r", ".308 WIN", 3.0, (18.9, 40, -4.0), "+X", "paint"),
            K.text("mk_ser", "SER  TMC30872", 2.2, (-16.1, -250, -5.0), "-X", "paint")]


def build(hi):
    sc, glass = scope(hi)
    body = receiver(hi) + barrel(hi) + stock(hi) + foreend(hi) + sc
    if hi:
        body += markings()
    mag = magazine_parts("magazine", hi, length=88.0, curve=0.03, mat="magalu", window=False, depth=46.0)
    for p in mag:
        K.transform(p, K.at((0, 6, -30)))
    return {"body": body, "magazine": mag}, glass
