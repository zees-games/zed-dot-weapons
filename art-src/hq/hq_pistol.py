# The service pistol, part by part, in millimetres (hq_kit's frame: bore on +Y at z = 0, up +Z,
# the ejection port on +X). A striker-fired polymer-frame 9 mm of the usual proportions: a
# 185 mm slide with front and rear serrations, three-dot sights, a grip raked 21 degrees, a
# rail on the dust cover, a double-stack magazine.
#
# build(hi) returns ({group: parts}, glass): see hq_m4.build.
import math

import hq_kit as K

SLIDE_TOP = 19.0
SIGHT_Z = 24.0           # tops of both sights: the aimed view's line runs parallel to the bore
SLIDE_BACK = -86.0
SLIDE_FRONT = 97.0
RAKE = 0.39              # grip: mm backwards per mm down
MAG_TOP = -14.0
MAG_Y = -70.0            # the magazine's centre at its top
SOCKETS = {
    "socket_optic": (0, -30, SLIDE_TOP),
    "socket_muzzle": (0, 99.5, 0),
    "socket_underbarrel": (0, 34, -27),
    "socket_magazine": (0, MAG_Y, MAG_TOP),
    "sight_rear": (0, -84, SIGHT_Z),
    "sight_front": (0, 87, SIGHT_Z),
}


def pin(y, z, sx, hi, r=3.4, name="pin"):
    p = K.lathe(name, [(0, 0), (0, r), (1.4, r), (2.0, r - 0.6), (2.0, 0)], 12 if not hi else 28, "steel", axis="X", centre=(0, y, z))
    if sx < 0:
        K.transform(p, K.at((0, y, z)) @ K.rot_z(180) @ K.at((0, -y, -z)))
    K.transform(p, K.at((sx * 12.0, 0, 0)))
    return K.finish(p, hi, bevel_mm=0.3)


def slide(hi):
    parts = []
    pts = [(SLIDE_BACK, -10), (SLIDE_BACK, 17), (SLIDE_BACK + 3, SLIDE_TOP), (90, SLIDE_TOP),
           (SLIDE_FRONT - 1, 14), (SLIDE_FRONT, 10), (SLIDE_FRONT, -10)]
    s = K.profile("slide", pts, -12.5, 12.5, "cerakote")
    # Rounded shoulders on top.
    for sx in (1, -1):
        K.cut(s, K.profile_x("w", [(sx * 12.7, 15), (sx * 12.7, 19.5), (sx * 8.5, 19.5)], -90, 100, None))
    # The channel the frame's rails run in, open at the bottom.
    K.cut(s, K.box("chan", (0, 5, -9.5), (17.5, 200, 6), None))
    # Serrations, front and rear, both sides.
    cuts = []
    for sx in (1, -1):
        for i in range(7):
            cuts.append(K.box("serr", (sx * 12.5, -81 + i * 2.8 + 8.0, 4.5), (2.4, 1.3, 22), None))
        for i in range(5):
            cuts.append(K.box("serr", (sx * 12.5, 55 + i * 2.8, 4.5), (2.4, 1.3, 20), None))
    K.cut(s, K.merge("serrs", cuts))
    # Ejection port on the right, the barrel hood visible through it.
    K.cut(s, K.box("port", (9.5, 10, 9.5), (7, 38, 12), None))
    # The barrel's hole at the muzzle, a little larger than the barrel.
    K.cut(s, K.cyl("muz", 90, SLIDE_FRONT + 3, 7.4, 20 if not hi else 40, None))
    # Dovetails for the rear sight and the front sight.
    K.cut(s, K.box("dtr", (0, -78, SLIDE_TOP), (11.4, 12, 1.0), None))
    K.finish(s, hi, bevel_mm=0.7)
    parts.append(s)
    hood = K.box("hood", (1, 10, 9.5), (10, 38, 12), "steel")
    parts.append(K.finish(hood, hi, bevel_mm=0.4))
    bar = K.lathe("barrel", [(50, 0), (50, 6.6), (SLIDE_FRONT - 3, 6.6), (SLIDE_FRONT + 1.5, 6.0), (SLIDE_FRONT + 2.5, 5.4),
                             (SLIDE_FRONT + 2.5, 0)], 18 if not hi else 40, "steel")
    K.cut(bar, K.cyl("bore", SLIDE_FRONT - 6, SLIDE_FRONT + 4, 4.1, 16 if not hi else 32, None))
    parts.append(K.finish(bar, hi, bevel_mm=0.3))
    # Recoil-spring guide visible in the hole is not modelled: the barrel fills it.
    return parts


def sights(hi):
    parts = []
    rear = K.profile("rear_sight", [(-85, 18), (-72, 18), (-72, 22), (-74, SIGHT_Z), (-84, SIGHT_Z), (-85, 22)],
                     -5.5, 5.5, "steel")
    K.cut(rear, K.box("notch", (0, -80, SIGHT_Z), (3.4, 20, 5.0), None))
    parts.append(K.finish(rear, hi, bevel_mm=0.35))
    for sx in (1, -1):
        parts.append(K.finish(K.cyl("rdot", -85.9, -84.2, 1.05, 12 if not hi else 24, "paint", centre=(sx * 3.9, 0, 21.4)), hi, bevel_mm=0.15))
    front = K.profile("front_sight", [(82, 18), (91, 18), (90, SIGHT_Z), (84, SIGHT_Z)], -1.9, 1.9, "steel")
    parts.append(K.finish(front, hi, bevel_mm=0.3))
    parts.append(K.finish(K.cyl("fdot", 82.4, 83.9, 1.15, 12 if not hi else 24, "paint", centre=(0, 0, 21.4)), hi, bevel_mm=0.15))
    return parts


def frame(hi):
    parts = []

    def y_rear(z):
        return -92.0 + RAKE * (z + 20.0)

    def y_front(z):
        return -62.0 + 0.394 * (z + 46.0)

    outline = [(SLIDE_BACK, -8), (-90, -14), (y_rear(-20), -20), (y_rear(-108), -108), (y_rear(-112), -112),
               (y_front(-112), -112), (-62, -46), (-60, -53), (-14, -53), (-5, -44), (-3, -27), (62, -27),
               (62, -8)]
    f = K.profile("frame", outline, -12.0, 12.0, "poly")
    # The trigger guard's opening.
    K.cut(f, K.profile("tg", [(-57, -16), (-9, -16), (-9, -40), (-16, -47), (-57, -47)], -14, 14, None))
    # A tang pocket under the slide's rear, and the rail slots under the dust cover.
    for yy in (22, 36):
        K.cut(f, K.box("slot", (0, yy, -27), (26, 3.2, 3.6), None))
    # Thumb rests: a scoop on each side of the grip above the panels.
    for sx in (1, -1):
        K.cut(f, K.box("scoop", (sx * 12.1, -64, -22), (1.4, 22, 6), None))
    K.finish(f, hi, round_mm=2.2)
    parts.append(f)
    # Stippled panels on both sides of the grip, and the front and back straps.
    pan = [(y_rear(-40) + 4, -40), (y_rear(-100) + 4, -100), (y_front(-100) - 4, -100), (y_front(-40) - 4, -40)]
    for sx in (1, -1):
        p = K.profile("panel", pan, sx * 11.9, sx * 12.7, "grip")
        parts.append(K.finish(p, hi, bevel_mm=0.5))
    # Slide stop (left), takedown lever (left), magazine release (left).
    ss = K.profile("slide_stop", [(-44, -10), (-12, -10), (-9, -14.5), (-42, -15.5)], -13.5, -11.8, "steel")
    parts.append(K.finish(ss, hi, bevel_mm=0.4))
    td = K.profile("takedown", [(-8, -9), (4, -9), (6, -15), (-6, -15)], -13.5, -11.8, "steel")
    parts.append(K.finish(td, hi, bevel_mm=0.4))
    parts.append(pin(-52, -30, -1, hi, r=4.4, name="mag_release"))
    parts.append(pin(-78, -16, 1, hi, name="pin"))
    parts.append(pin(0, -18, 1, hi, name="pin"))
    parts.append(pin(-78, -16, -1, hi, name="pin"))
    # Lanyard loop at the grip's foot.
    ring = K.profile("lanyard", [(y_rear(-112) + 1, -104), (y_rear(-112) + 12, -112), (y_rear(-112) + 12, -116),
                                 (y_rear(-112) + 1, -116)], -3, 3, "steel")
    parts.append(K.finish(ring, hi, bevel_mm=0.4))
    trig = K.profile("trigger", [(-32, -14), (-25, -14), (-23, -30), (-19, -38), (-27, -40), (-31, -33)], -3.2, 3.2, "steel")
    parts.append(K.finish(trig, hi, bevel_mm=0.45))
    shoe = K.profile("trigger_safety", [(-30, -26), (-24, -26), (-24, -34), (-30, -34)], -1.2, 1.2, "poly")
    parts.append(K.finish(shoe, hi, bevel_mm=0.3))
    return parts


def magazine(hi):
    parts = []
    depth = 30.0
    L = 102.0
    outline = [(-depth / 2, 0), (-depth / 2 - RAKE * L, -L), (depth / 2 - RAKE * L, -L), (depth / 2, 0)]
    m = K.profile("magazine", outline, -10.3, 10.3, "magalu")
    for sx in (1, -1):
        for fz in (0.3, 0.5, 0.7):
            z = -L * fz
            K.cut(m, K.profile("rib", [(-9 - RAKE * -z, z), (9 - RAKE * -z, z), (9 - RAKE * -z, z - 3), (-9 - RAKE * -z, z - 3)],
                               sx * 9.6, sx * 11.0, None))
    K.cut(m, K.profile("win", [(-3 - RAKE * 0.5 * L, -0.5 * L), (3 - RAKE * 0.5 * L, -0.5 * L),
                               (3 - RAKE * 0.7 * L, -0.7 * L), (-3 - RAKE * 0.7 * L, -0.7 * L)], -11, -9.4, None))
    K.finish(m, hi, bevel_mm=0.8)
    parts.append(m)
    fl = [(-depth / 2 - RAKE * L - 1.5, -L + 2), (depth / 2 - RAKE * L + 3.5, -L + 2), (depth / 2 - RAKE * L + 3.0, -L - 5),
          (-depth / 2 - RAKE * L - 2.5, -L - 5)]
    floor = K.profile("mag_floor", fl, -11.6, 11.6, "poly")
    parts.append(K.finish(floor, hi, bevel_mm=0.9))
    return parts


def markings():
    t = []
    t.append(K.text("mk_l", "TMC ARMORY  SERVICE 9 MM", 3.0, (-12.35, 30, 5.0), "-X", "paint"))
    t.append(K.text("mk_r", "9 X 19", 3.0, (12.35, 62, 5.0), "+X", "paint"))
    t.append(K.text("mk_ser", "SER  TMC09117", 2.3, (-11.85, 30, -18.5), "-X", "paint"))
    return t


def build(hi):
    body = slide(hi) + frame(hi)
    mag = magazine(hi)
    for p in mag:
        K.transform(p, K.at((0, MAG_Y, MAG_TOP)))
    if hi:
        body += markings()
    return {"body": body, "magazine": mag, "rear_sight": sights(hi)}, []
