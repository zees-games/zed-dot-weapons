# The six attachments, each in hq_kit's frame (bore along +Y, up +Z, the gun's right on +X) with
# its origin AT ITS MOUNT, so a game parents it to the gun's socket node with an identity
# transform:
#
#   optic        on the top rail's teeth          (red_dot, scope_4x)
#   muzzle       on the bore where the flash hider starts   (suppressor)
#   underbarrel  on the bottom rail's teeth, hanging down   (foregrip)
#   side         on the right rail's teeth, standing out to +X   (laser)
#   magazine     at the top centre of where a magazine seats   (ext_mag)
#
# build(name, hi) returns (parts, glass): parts are baked onto one atlas like a gun's; glass is
# a lens or an aperture, shipped with its own plain material and never baked.
import hq_kit as K
import hq_m4

# Height of an optic's axis above the rail's teeth, mm. 30 puts the red dot's axis just above
# the carbine's iron-sight line (front post 26 mm over the rail): the irons show in the bottom
# third of the window. The aim line is measured from these by ZedWeaponPack, never guessed.
RED_DOT_AXIS = 30.0
SCOPE_AXIS = 38.0
INFO = {
    "red_dot": {"mount": "optic", "axis_mm": RED_DOT_AXIS, "hides": []},
    "scope_4x": {"mount": "optic", "axis_mm": SCOPE_AXIS, "hides": ["rear_sight"]},
    "suppressor": {"mount": "muzzle", "length_mm": 172.0, "hides": []},
    "foregrip": {"mount": "underbarrel", "hides": []},
    "laser": {"mount": "side", "hides": []},
    "ext_mag": {"mount": "magazine", "hides": ["magazine"]},
}


def clamp(name, y0, y1, hi, mat="anod", height=7.0):
    """A rail clamp sitting on the teeth (z = 0), its jaws reaching down round the rail."""
    c = K.profile_x(name, [(-13, -5.5), (-10.2, -5.5), (-10.2, 0), (10.2, 0), (10.2, -5.5), (13, -5.5),
                           (13, height - 2), (11, height), (-11, height), (-13, height - 2)], y0, y1, mat)
    return K.finish(c, hi, bevel_mm=0.7)


def knob(name, y, z, hi, r=5.0, length=8.0, mat="steel"):
    k = K.lathe(name, [(13, 0), (13, r), (13 + length - 1, r), (13 + length, r - 1), (13 + length, 0)], 12 if not hi else 40, mat, axis="X", centre=(0, y, z))
    return K.finish(k, hi, bevel_mm=0.4)


def red_dot(hi):
    a = RED_DOT_AXIS
    parts = [clamp("rd_clamp", -18, 18, hi)]
    riser = K.profile("rd_riser", [(-16, 6), (16, 6), (14, a - 12), (-14, a - 12)], -9, 9, "anod")
    parts.append(K.finish(riser, hi, bevel_mm=0.8))
    n = 24 if not hi else 64
    tube = K.lathe("rd_tube", [(-34, 14.5), (-34, 18.0), (-30, 18.0), (-28, 15.5), (24, 15.5), (26, 18.2),
                               (36, 18.2), (36, 14.5), (32, 13.5), (-30, 13.5)], n, "anod", centre=(0, 0, a))
    parts.append(K.finish(tube, hi, bevel_mm=0.5))
    turret_top = K.lathe("rd_turret_t", [(14, 0), (14, 8), (22, 8), (22.5, 7.3), (25, 7.3), (25.5, 6.5), (25.5, 0)], 16 if not hi else 48, "anod", axis="Z")
    K.transform(turret_top, K.at((0, -2, a)))
    parts.append(K.finish(turret_top, hi, bevel_mm=0.4))
    turret_side = K.lathe("rd_turret_s", [(14, 0), (14, 8), (22, 8), (22.5, 7.3), (25, 7.3), (25.5, 6.5), (25.5, 0)], 16 if not hi else 48, "anod", axis="X", centre=(0, -2, a))
    parts.append(K.finish(turret_side, hi, bevel_mm=0.4))
    parts.append(knob("rd_knob", 0, -2, hi))
    glass = [
        K.cyl("rd_lens_r", -27, -26.5, 13.6, 24, "glass", centre=(0, 0, a)),
        K.cyl("rd_lens_f", 28, 28.5, 13.6, 24, "glass", centre=(0, 0, a)),
        K.cyl("rd_dot", 0, 0.3, 0.55, 8, "dot", centre=(0, 0, a)),
    ]
    return parts, glass


def scope_4x(hi):
    a = SCOPE_AXIS
    parts = []
    for y in (-42, 38):
        parts.append(clamp("sc_base", y - 11, y + 11, hi, height=6))
        ring = K.lathe("sc_ring", [(y - 8, 15.3), (y - 8, 19.5), (y + 8, 19.5), (y + 8, 15.3)], 20 if not hi else 64, "anod", centre=(0, 0, a))
        parts.append(K.finish(ring, hi, bevel_mm=0.6))
        web = K.profile("sc_web", [(y - 8, 5), (y + 8, 5), (y + 8, a - 16), (y - 8, a - 16)], -7, 7, "anod")
        parts.append(K.finish(web, hi, bevel_mm=0.6))
        parts.append(knob("sc_knob", y, -1, hi, r=4.5, length=6))
    n = 24 if not hi else 72
    # Solid to the axis, with a shallow recess at each end for the lens: an earlier profile
    # with a hollow bore had its inner wall cross the outer one, and the bake went black there.
    prof = [(-106, 0), (-106, 16.5), (-112, 17.5), (-112, 20.5), (-84, 20.5), (-80, 18.5), (-74, 15), (60, 15),
            (70, 17), (84, 24.5), (124, 24.5), (126, 23.5), (126, 21.5), (116, 21), (116, 0)]
    body = K.lathe("sc_tube", prof, n, "anod", centre=(0, 0, a))
    # The power ring's grip ribs.
    for i in range(6):
        y = -78 + i * 3.2
        K.cut(body, K.lathe("groove", [(y, 0), (y, 22), (y + 1.2, 22), (y + 1.2, 0)], 24, None, centre=(0, 0, a))) if hi else None
    parts.append(K.finish(body, hi, bevel_mm=0.5))
    saddle = K.lathe("sc_saddle", [(-16, 0), (-16, 18.5), (16, 18.5), (16, 0)], 20 if not hi else 64, "anod", centre=(0, 0, a))
    parts.append(K.finish(saddle, hi, bevel_mm=0.6))
    for axis, c in (("Z", None), ("X", (0, 0, a))):
        t = K.lathe("sc_turret", [(15, 0), (15, 9.5), (24, 9.5), (24.6, 8.6), (31, 8.6), (31.5, 7.5), (31.5, 0)], 16 if not hi else 64, "anod", axis=axis, centre=c or (0, 0, 0))
        if axis == "Z":
            K.transform(t, K.at((0, 0, a)))
        if hi:
            for i in range(12):
                rib = K.box("knurl", (8.6, 0, 28), (1.0, 1.0, 5.5), None)
                M = K.rot_z(i * 30) if axis == "Z" else K.rot_x(i * 30)
                if axis == "X":
                    rib = K.box("knurl", (28, 0, 8.6), (5.5, 1.0, 1.0), None)
                K.transform(rib, M)
                K.transform(rib, K.at((0, 0, a)))
                K.cut(t, rib)
        parts.append(K.finish(t, hi, bevel_mm=0.4))
    glass = [
        K.cyl("sc_lens_r", -106.6, -106.1, 16.4, 32, "glass", centre=(0, 0, a)),
        K.cyl("sc_lens_f", 116.1, 116.6, 20.9, 32, "glass", centre=(0, 0, a)),
    ]
    return parts, glass


def suppressor(hi):
    n = 28 if not hi else 64
    prof = [(-2, 0), (-2, 11.5), (0, 13.5), (34, 13.5), (36, 16), (40, 19.2), (164, 19.2), (168, 17.5),
            (172, 15.5), (172, 4.6), (166, 4.6), (166, 0)]
    s = K.lathe("suppressor", prof, n, "cerakote")
    # Wrench flats and grip grooves on the mount collar.
    for i in range(5):
        y = 6 + i * 5.5
        if hi:  # on the low mesh the normal map carries them: five cut rings cost 1.3k triangles
            K.cut(s, K.lathe("groove", [(y, 0), (y, 20), (y + 1.6, 20), (y + 1.6, 0)], 64, None, phase=0.1))
    K.finish(s, hi, bevel_mm=0.6)
    return [s], []


def foregrip(hi):
    parts = []
    c = clamp("fg_clamp", -22, 22, hi, mat="poly", height=8)
    K.transform(c, K.rot_y(180))
    parts.append(c)
    n = 16 if not hi else 48
    prof = [(-8, 0), (-8, 15.5), (-14, 15.0), (-30, 14.2), (-36, 13.0), (-42, 14.2), (-58, 13.6), (-64, 12.4),
            (-70, 13.6), (-88, 13.0), (-94, 12.0), (-96, 0)]
    g = K.lathe("fg_body", prof, n, "grip", axis="Z")
    K.transform(g, K.at((0, 4, 0)))
    parts.append(K.finish(g, hi, round_mm=2.0))
    cap = K.lathe("fg_cap", [(-96, 0), (-96, 13), (-101, 12), (-102, 9), (-102, 0)], n, "poly", axis="Z")
    K.transform(cap, K.at((0, 4, 0)))
    parts.append(K.finish(cap, hi, bevel_mm=0.8))
    return parts, []


def laser(hi):
    parts = []
    c = clamp("lz_clamp", -20, 20, hi, mat="tan", height=6)
    K.transform(c, K.rot_y(90))
    parts.append(c)
    body = K.profile_x("lz_body", [(5, -15), (30, -15), (33, -12), (33, 12), (30, 15), (5, 15)], -42, 38, "tan")
    K.cut(body, K.box("lz_groove", (33, -2, 0), (3, 60, 4), None))
    K.finish(body, hi, bevel_mm=1.4)
    parts.append(body)
    for z, r in ((7, 4.0), (-6, 6.5)):
        hood = K.lathe("lz_hood", [(38, 0), (38, r + 2.5), (44, r + 2.5), (44, r), (40, r), (40, 0)], 16 if not hi else 40, "tan", centre=(19, 0, z))
        parts.append(K.finish(hood, hi, bevel_mm=0.5))
    for y in (-30, -18):
        b = K.box("lz_button", (19, y, 16.5), (10, 7, 3), "rubber")
        parts.append(K.finish(b, hi, bevel_mm=0.8))
    for y, z in ((-36, 10), (-36, -10), (30, 10), (30, -10)):
        sc = K.cyl("lz_screw", 33, 34.2, 1.8, 8 if not hi else 24, "steel", axis="X", centre=(0, y, z))
        parts.append(K.finish(sc, hi, bevel_mm=0.2))
    glass = [
        K.cyl("lz_lens_laser", 41, 41.5, 4.0, 16, "dot", centre=(19, 0, 7)),
        K.cyl("lz_lens_light", 41, 41.5, 6.5, 16, "glass", centre=(19, 0, -6)),
    ]
    return parts, glass


def ext_mag(hi):
    return hq_m4.magazine_parts("ext_mag", hi, length=236.0, curve=0.2, mat="tan", window=True), []


def build(name, hi):
    parts, glass = BUILDERS[name](hi)
    return {name: parts}, glass


BUILDERS = {
    "red_dot": red_dot,
    "scope_4x": scope_4x,
    "suppressor": suppressor,
    "foregrip": foregrip,
    "laser": laser,
    "ext_mag": ext_mag,
}
