# The M4-pattern carbine, part by part, in millimetres (hq_kit's frame: bore on +Y at z = 0, up
# +Z, the ejection port on +X). Proportions are the real carbine's (14.5 in barrel, flat-top
# upper, four-rail handguard, A-frame front sight, collapsible stock); every surface is modelled
# here, nothing is imported.
#
# build(hi) returns (body, magazine, sockets): the body and magazine are lists of finished parts
# (low or high, see hq_kit.finish), the sockets are where hq_attachments' parts mount.
import math

import hq_kit as K

# Where the attachments go, in mm. Each attachment is modelled with its origin at its mount.
RAIL_TOP = 25.4          # top of the picatinny teeth, upper receiver and handguard alike
HG_FRONT = 205.0
HG_RAIL_TOP = 21.4       # the handguard's rails: low profile, so they stay out of the aimed view
MUZZLE_BASE = 362.0      # where the flash hider starts: a suppressor slides over it from here
MUZZLE_END = 402.0
# Height of the sight line over the bore. A real carbine's is about 66 mm; the first version
# kept it at 46, 20 mm over the rails, and the handguard's top rail filled the bottom of the
# aimed view like a slab. Taller sights and a handguard rail 4 mm lower than the receiver's
# (HG_RAIL_TOP) put the rail's near end well below the line, out of the sight picture.
SIGHT_Z = 76.0
SOCKETS = {
    "socket_optic": (0, -62, RAIL_TOP),
    "socket_muzzle": (0, MUZZLE_BASE, 0),
    "socket_underbarrel": (0, 150, -HG_RAIL_TOP),
    "socket_side": (HG_RAIL_TOP, 178, 0),
    "socket_magazine": (0, -24, -20),
    # Not sockets: the iron sight's line, through the rear aperture and the front post's tip.
    # zee aims along these instead of measuring the mesh and building a sight of its own.
    "sight_rear": (0, -133, SIGHT_Z),
    "sight_front": (0, 276.75, SIGHT_Z),
}


def rail(name, y0, y1, side, base, hi, mat="anod", top=RAIL_TOP):
    """A picatinny rail from y0 to y1 on one side ('top', 'bottom', 'right', 'left'), its foot at
    `base` mm from the bore, with the cross slots cut every 10 mm."""
    h = top - base
    sec = [(-8.0, 0), (8.0, 0), (8.0, h - 4.2), (10.6, h - 2.0), (10.6, h - 1.0), (9.6, h),
           (-9.6, h), (-10.6, h - 1.0), (-10.6, h - 2.0), (-8.0, h - 4.2)]
    r = K.profile_x(name, [(x, z + base) for x, z in sec], y0, y1, mat)
    slots = []
    y = y0 + 6.0
    while y + 5.3 < y1 - 3.0:
        slots.append(K.box(name + "_s", (0, y + 2.65, base + h - 1.4), (24, 5.3, 3.2), None))
        y += 10.0
    if slots:
        cutter = K.merge(name + "_cut", slots)
        K.cut(r, cutter)
    K.finish(r, hi, bevel_mm=0.45, segs_lo=0)
    turn = {"top": 0, "right": 90, "bottom": 180, "left": -90}[side]
    if turn:
        K.transform(r, K.rot_y(turn))
    return r


def upper(hi):
    parts = []
    pts = [(-152, -14), (22, -14), (22, 11.5), (17, 15.5), (-147, 15.5), (-152, 11)]
    u = K.profile("upper", pts, -13.5, 13.5, "anod")
    # Rounded shoulders on the top: chamfer the long top edges by cutting two wedges.
    for sx in (1, -1):
        w = K.profile_x("w", [(sx * 13.6, 9), (sx * 13.6, 16), (sx * 8.5, 16)], -160, 30, None)
        K.cut(u, w)
    # Ejection port (right) and its recess, the forward-assist boss, the brass deflector.
    K.cut(u, K.box("port", (13.5, -64, 2.5), (2.6, 58, 13), None))
    K.finish(u, hi, bevel_mm=0.9)
    parts.append(u)
    dust = K.box("dust", (12.7, -64, 2.5), (0.8, 56, 12), "anod")
    K.cut(dust, K.box("rib", (13.4, -64, 4.5), (1.0, 52, 1.2), None))
    parts.append(K.finish(dust, hi, bevel_mm=0.3))
    bolt = K.box("bolt", (12.0, -66, 2.5), (1.0, 50, 9), "steel")
    parts.append(K.finish(bolt, hi, bevel_mm=0.3))
    boss = K.profile("fa_boss", [(-124, -6), (-100, -6), (-96, 2), (-104, 12), (-124, 12)], 12.5, 18.5, "anod")
    parts.append(K.finish(boss, hi, bevel_mm=1.0))
    fa = K.lathe("fa", [(17, 6.4), (24, 6.4), (24.5, 6.0), (27.5, 6.0), (28, 5.0), (28, 0)], 16 if not hi else 32, "anod", axis="X", centre=(0, -112, 3))
    K.transform(fa, K.at((0, -112, 3)) @ K.rot_z(-20) @ K.at((0, 112, -3)))
    parts.append(K.finish(fa, hi, bevel_mm=0.5))
    defl = K.profile("deflector", [(-104, -2), (-94, -2), (-94, 12), (-100, 12), (-104, 6)], 13, 19, "anod")
    parts.append(K.finish(defl, hi, bevel_mm=0.8))
    # Charging handle: the T at the rear of the top.
    ch = K.profile_x("charging", [(-16, 9), (16, 9), (16, 15), (14, 17), (-14, 17), (-16, 15)], -161, -152, "anod")
    parts.append(K.finish(ch, hi, bevel_mm=0.6))
    latch = K.box("ch_latch", (-17, -157, 12.5), (6, 7, 5), "anod")
    parts.append(K.finish(latch, hi, bevel_mm=0.5))
    parts.append(rail("upper_rail", -147, 17, "top", 15.5, hi))
    # Barrel nut between the receiver and the handguard.
    nut = K.lathe("nut", [(22, 0), (22, 17), (24, 18.5), (30, 18.5), (31, 17), (31, 0)], 24 if not hi else 48, "steel")
    parts.append(K.finish(nut, hi, bevel_mm=0.5))
    return parts


def lower(hi):
    parts = []
    pts = [(-152, -14), (-152, -32), (-140, -38), (-104, -38), (-98, -36), (-66, -36), (-64, -58),
           (-60, -63), (14, -63), (17, -58), (14, -36), (20, -30), (24, -22), (26, -14)]
    lo = K.profile("lower", pts, -12, 12, "anod")
    # The magazine well, open at the bottom; its flared lips are the outer profile's foot.
    K.cut(lo, K.box("well", (0, -24, -48), (21.5, 66, 54), None))
    # Trigger slot.
    K.cut(lo, K.box("tslot", (0, -84, -34), (6.5, 24, 10), None))
    # Recessed panels on both sides of the well (machined pockets on a forged lower).
    for sx in (1, -1):
        K.cut(lo, K.box("pocket", (sx * 12.3, -24, -46), (1.4, 60, 22), None))
    K.finish(lo, hi, bevel_mm=1.0)
    parts.append(lo)
    # Trigger guard: a bar under the trigger, up into the grip and the well.
    guard = K.profile("guard", [(-66, -44), (-62, -44), (-62, -62), (-66, -66), (-104, -66), (-110, -60),
                                (-110, -44), (-106, -44), (-106, -58), (-102, -62), (-68, -62)], -5, 5, "anod")
    parts.append(K.finish(guard, hi, bevel_mm=0.7))
    trig = K.profile("trigger", [(-84, -36), (-79, -36), (-78, -46), (-81, -55), (-86, -58), (-88, -56),
                                 (-84, -50), (-83, -44)], -2.2, 2.2, "steel")
    parts.append(K.finish(trig, hi, bevel_mm=0.6))
    # Pistol grip, raked back, with a finger bump and a beaver tail.
    g = [(-100, -36), (-134, -36), (-140, -40), (-147, -60), (-158, -112), (-156, -120), (-146, -124),
         (-124, -124), (-118, -116), (-114, -96), (-110, -84), (-108, -78), (-112, -72), (-110, -64),
         (-103, -48)]
    grip = K.profile("grip", g, -15, 15, "grip")
    parts.append(K.finish(grip, hi, round_mm=4.5))
    # Selector (left), magazine release (right), bolt catch (left), pins (both sides).
    sel = K.profile("selector", [(-104, -24), (-92, -27), (-91, -31), (-103, -30)], -16, -12, "steel")
    parts.append(K.finish(sel, hi, bevel_mm=0.5))
    hub = K.cyl("sel_hub", -12, -14.5, 5.5, 12 if not hi else 32, "steel", axis="X", centre=(0, -100, -28))
    parts.append(K.finish(hub, hi, bevel_mm=0.4))
    mr = K.lathe("mag_release", [(12, 0), (12, 5.0), (14.5, 5.0), (15.2, 4.2), (15.2, 0)], 12 if not hi else 32, "steel", axis="X", centre=(0, -58, -30))
    parts.append(K.finish(mr, hi, bevel_mm=0.3))
    fence = K.profile("fence", [(-64, -24), (-50, -24), (-50, -35), (-64, -38)], 12, 14, "anod")
    parts.append(K.finish(fence, hi, bevel_mm=0.5))
    bc = K.profile("bolt_catch", [(-10, -16), (8, -16), (10, -22), (-8, -26)], -15, -12, "steel")
    parts.append(K.finish(bc, hi, bevel_mm=0.4))
    for y in (-144, 15):
        for sx in (1, -1):
            pin = K.lathe("pin", [(0, 0), (0, 3.4), (1.6, 3.4), (2.2, 2.8), (2.2, 0)], 12 if not hi else 24, "steel", axis="X", centre=(0, y, -21))
            if sx < 0:
                K.transform(pin, K.at((0, y, -21)) @ K.rot_z(180) @ K.at((0, -y, 21)))
            K.transform(pin, K.at((sx * 12, 0, 0)))
            parts.append(K.finish(pin, hi, bevel_mm=0.3))
    return parts


def stock(hi):
    parts = []
    tube = K.lathe("buffer_tube", [(-152, 0), (-152, 14.6), (-330, 14.6), (-334, 13), (-334, 0)], 20 if not hi else 48, "anod", centre=(0, 0, 0))
    K.transform(tube, K.at((0, 0, 1)))
    parts.append(K.finish(tube, hi, bevel_mm=0.6))
    castle = K.lathe("castle_nut", [(-152, 0), (-152, 18), (-160, 18), (-160, 0)], 8 if not hi else 8, "steel", phase=math.pi / 8)
    K.transform(castle, K.at((0, 0, 1)))
    parts.append(K.finish(castle, hi, bevel_mm=0.6))
    plate = K.profile("end_plate", [(-161, -18), (-163, -18), (-163, 22), (-161, 22)], -16, 16, "steel")
    parts.append(K.finish(plate, hi, bevel_mm=0.4))
    s = [(-252, -12), (-250, 15), (-256, 20), (-338, 23), (-346, 26), (-354, 25), (-356, 18),
         (-356, -98), (-348, -103), (-334, -102), (-318, -70), (-298, -40), (-272, -22)]
    st = K.profile("stock", s, -16.5, 16.5, "poly")
    # Lightening pockets in each side of the lower web, and the channel the tube runs in.
    for sx in (1, -1):
        p = K.profile("pocket", [(-300, -36), (-322, -68), (-340, -90), (-340, -40), (-330, -24)], sx * 14.5, sx * 20, None)
        K.cut(st, p)
    K.cut(st, K.cyl("chan", -240, -320, 15.2, 24, None, centre=(0, 0, 1)))
    K.finish(st, hi, bevel_mm=1.2)
    parts.append(st)
    pad = K.profile("butt_pad", [(-356, 26), (-366, 26), (-368, 20), (-368, -100), (-364, -105), (-356, -103)], -17.5, 17.5, "rubber")
    for z in range(-90, 20, 9):
        K.cut(pad, K.box("rib", (0, -368.5, z), (40, 2.0, 2.4), None))
    parts.append(K.finish(pad, hi, bevel_mm=1.5))
    lever = K.profile("lever", [(-262, -18), (-292, -26), (-292, -32), (-276, -32), (-262, -24)], -5, 5, "poly")
    parts.append(K.finish(lever, hi, bevel_mm=0.6))
    return parts


def handguard(hi):
    parts = []
    segs = 8
    r = 17.0 / math.cos(math.pi / segs)
    body = K.lathe("handguard", [(31, 0), (31, r), (HG_FRONT, r), (HG_FRONT, 0)], segs, "anod", phase=math.pi / segs)
    # Vents in the four diagonal faces.
    vents = []
    for k in range(4):
        ang = 45 + 90 * k
        for i in range(6):
            y = 52 + i * 25
            v = K.merge("vent", [K.box("vslot", (0, 0, 0), (10, 12, 8.4), None),
                                 K.cyl("vend", -5, 5, 4.2, 12, None, axis="X", centre=(0, -6, 0)),
                                 K.cyl("vend", -5, 5, 4.2, 12, None, axis="X", centre=(0, 6, 0))])
            K.transform(v, K.at((0, y, 0)) @ K.rot_y(ang) @ K.at((18.5, 0, 0)))
            vents.append(v)
    K.cut(body, K.merge("vents", vents))
    # Hollow it, so the vents show the barrel behind them.
    K.cut(body, K.cyl("bore", 25, HG_FRONT + 5, 13.5, 16, None))
    K.finish(body, hi, bevel_mm=0.8)
    parts.append(body)
    for side in ("top", "bottom", "right", "left"):
        parts.append(rail("hg_rail_" + side, 33, HG_FRONT - 2, side, 16.0, hi, top=HG_RAIL_TOP))
    # Bolt heads at the corners of the front, one per side.
    for k in range(4):
        b = K.lathe("bolt_head", [(0, 0), (0, 3.2), (1.8, 3.2), (2.2, 2.6), (2.2, 0)], 6 if not hi else 24, "steel", axis="X")
        K.transform(b, K.at((0, HG_FRONT - 10, 0)) @ K.rot_y(45 + 90 * k) @ K.at((16.6, 0, 0)))
        parts.append(K.finish(b, hi, bevel_mm=0.3))
    return parts


def barrel(hi):
    parts = []
    n = 18 if not hi else 48
    prof = [(31, 0), (31, 9.4), (262, 9.4), (262, 9.4), (292, 9.4), (294, 8.0), (300, 7.6), (360, 7.6),
            (MUZZLE_BASE, 7.2), (MUZZLE_BASE, 0)]
    b = K.lathe("barrel", prof, n, "steel")
    parts.append(K.finish(b, hi, bevel_mm=0.4))
    # Front sight base: the block round the barrel, the A-frame, the post between its ears.
    fsb = K.profile("fsb", [(262, -13), (292, -13), (292, 9), (287, 13), (283, 71), (270, 71), (266, 13), (262, 9)], -9.5, 9.5, "steel")
    K.cut(fsb, K.profile("fsb_win", [(271, 15), (282, 15), (279.5, 63), (273.5, 63)], -12, 12, None))
    K.cut(fsb, K.cyl("fsb_bore", 255, 300, 9.0, 24, None))
    K.finish(fsb, hi, bevel_mm=0.8)
    parts.append(fsb)
    ears = K.profile("fsb_ears", [(268, 69), (285, 69), (285, 77), (281, 84), (272, 84), (268, 77)], -8.5, 8.5, "steel")
    K.cut(ears, K.box("ear_gap", (0, 276.5, 80), (11, 30, 14), None))
    parts.append(K.finish(ears, hi, bevel_mm=0.6))
    # The post's tip is level with the rear aperture's centre (SIGHT_Z), so the sight line runs
    # parallel to the bore and the view model can hold it straight down the screen's axis.
    post = K.profile("post", [(275, 69), (278.5, 69), (278.5, 75.5), (277.8, 76.5), (275.7, 76.5), (275, 75.5)], -1.3, 1.3, "steel")
    parts.append(K.finish(post, hi, bevel_mm=0.25))
    lug = K.profile("bayonet_lug", [(274, -13), (290, -13), (290, -20), (277, -20)], -3, 3, "steel")
    parts.append(K.finish(lug, hi, bevel_mm=0.4))
    swivel = K.profile("swivel", [(262, -13), (270, -13), (270, -30), (262, -30)], -2, 2, "steel")
    K.cut(swivel, K.box("sw_hole", (0, 266, -24), (6, 4.5, 9), None))
    parts.append(K.finish(swivel, hi, bevel_mm=0.4))
    # Birdcage flash hider: three slots up and to the sides, none at the bottom.
    fh_prof = [(MUZZLE_BASE, 0), (MUZZLE_BASE, 8.6), (MUZZLE_BASE + 8, 8.6), (MUZZLE_BASE + 9, 10.6),
               (MUZZLE_END - 1.2, 10.6), (MUZZLE_END, 9.6), (MUZZLE_END, 0)]
    fh = K.lathe("flash_hider", fh_prof, n, "steel")
    slots = []
    for ang in (0, 60, 120, 180, 240):
        s = K.box("fh_slot", (0, MUZZLE_BASE + 24, 9), (2.6, 22, 8), None)
        K.transform(s, K.rot_y(ang))
        slots.append(s)
    K.cut(fh, K.merge("fh_slots", slots))
    K.cut(fh, K.cyl("fh_bore", MUZZLE_BASE + 4, MUZZLE_END + 5, 4.8, 16, None))
    K.finish(fh, hi, bevel_mm=0.4)
    parts.append(fh)
    return parts


def rear_sight(hi):
    parts = []
    base = K.profile("buis_base", [(-146, 25), (-122, 25), (-122, 31), (-126, 34), (-142, 34), (-146, 31)], -11, 11, "anod")
    K.cut(base, K.box("buis_gap", (0, -134, 33), (12, 30, 4), None))
    parts.append(K.finish(base, hi, bevel_mm=0.7))
    for sx in (1, -1):
        wing = K.profile("buis_wing", [(-142, 31), (-126, 31), (-128, 80), (-140, 80)], sx * 6.5, sx * 9.5, "anod")
        parts.append(K.finish(wing, hi, bevel_mm=0.6))
    leaf = K.profile("buis_leaf", [(-136, 31), (-130, 31), (-131, 81), (-135, 81)], -5.5, 5.5, "steel")
    K.cut(leaf, K.cyl("aperture", -140, -125, 1.4, 12, None, centre=(0, 0, SIGHT_Z)))
    parts.append(K.finish(leaf, hi, bevel_mm=0.3))
    knob = K.lathe("buis_knob", [(11, 0), (11, 4.5), (16, 4.5), (16.6, 3.8), (16.6, 0)], 12 if not hi else 32, "steel", axis="X", centre=(0, -134, 29))
    parts.append(K.finish(knob, hi, bevel_mm=0.3))
    return parts


def magazine_parts(name, hi, length=170.0, curve=0.16, mat="magalu", window=False, depth=62.0):
    """A curved box magazine, its origin (0, 0, 0) at the top centre of where it seats in the
    well: so the standard and the extended one share the gun's socket_magazine."""
    parts = []
    pts_f, pts_r = [], []
    steps = 10
    for i in range(steps + 1):
        t = i / steps
        z = -t * length
        dy = curve * length * t * t
        pts_r.append((-depth / 2 + dy, z))
        pts_f.append((depth / 2 + dy - 4 * t, z))
    outline = pts_r + list(reversed(pts_f))
    m = K.profile(name, outline, -10.4, 10.4, mat)
    # Ribs pressed into each side, following the curve.
    for sx in (1, -1):
        for frac in (0.32, 0.55, 0.78):
            seg = []
            for i in range(steps + 1):
                t = i / steps
                if t < 0.2 or t > 0.92:
                    continue
                z = -t * length
                dy = curve * length * t * t
                seg.append((-depth / 2 + dy + frac * depth - 1.6, z))
            band = [(y, z) for y, z in seg] + [(y + 3.2, z) for y, z in reversed(seg)]
            K.cut(m, K.profile("rib", band, sx * 9.6, sx * 11.0, None))
    if window:
        win = [(-depth / 2 + 14, -30), (-depth / 2 + 21, -30), (-depth / 2 + 21 + curve * length * 0.35, -length * 0.8),
               (-depth / 2 + 14 + curve * length * 0.35, -length * 0.8)]
        K.cut(m, K.profile("win", win, -11, -9.3, None))
    K.finish(m, hi, bevel_mm=0.9)
    parts.append(m)
    t = 1.0
    zb = -length
    dy = curve * length
    floor = K.profile(name + "_floor", [(-depth / 2 + dy - 3, zb + 3), (depth / 2 + dy - 1, zb + 3),
                                        (depth / 2 + dy + 1, zb - 4), (-depth / 2 + dy - 4, zb - 5)], -12, 12, "poly" if mat != "tan" else "tan")
    parts.append(K.finish(floor, hi, bevel_mm=1.2))
    # The top round on the follower: brass case, copper bullet, so a reload shows it is loaded.
    case = K.lathe(name + "_case", [(-28, 0), (-28, 4.7), (10, 4.7), (13, 3.2), (16, 3.2), (16, 0)], 10 if not hi else 32, "brass", centre=(0, 0, 0))
    K.transform(case, K.at((-3, 0, 2)))
    parts.append(K.finish(case, hi, bevel_mm=0.3))
    bullet = K.lathe(name + "_bullet", [(16, 0), (16, 2.85), (22, 2.6), (26, 1.6), (28, 0.3), (28, 0)], 10 if not hi else 32, "copper")
    K.transform(bullet, K.at((-3, 0, 2)))
    parts.append(K.finish(bullet, hi, bevel_mm=0.2))
    return parts


def markings():
    """Engraved, paint-filled lettering: HIGH mesh only, baked into colour and normal."""
    t = []
    t.append(K.text("mk_safe", "SAFE", 2.6, (-12.15, -110, -18.5), "-X", "paint"))
    t.append(K.text("mk_semi", "SEMI", 2.6, (-12.15, -88, -20.0), "-X", "paint"))
    t.append(K.text("mk_auto", "AUTO", 2.6, (-12.15, -92, -34.0), "-X", "paint"))
    t.append(K.text("mk_maker", "TMC ARMORY", 3.0, (-11.72, -24, -40), "-X", "paint"))
    t.append(K.text("mk_model", "CARBINE  CAL 5.56 MM", 2.4, (-11.72, -24, -45), "-X", "paint"))
    t.append(K.text("mk_serial", "SER  TMC04251", 2.4, (-11.72, -24, -50), "-X", "paint"))
    t.append(K.text("mk_upper", "M4", 4.0, (13.55, -140, -5), "+X", "paint"))
    for i, ch in enumerate("ABCDEFGHIJKLMNOP"):
        t.append(K.text("mk_rail", str(i + 1), 1.6, (-8.12, -141 + i * 10, 17.6), "-X", "paint"))
    return t


def build(hi):
    """{group: parts}. Each group ships as its own node in the GLB, sharing one atlas: the
    magazine (a reload carries it, an extended one replaces it) and the rear sight (a scope
    hides it) have to be separable."""
    body = upper(hi) + lower(hi) + stock(hi) + handguard(hi) + barrel(hi)
    mag = magazine_parts("magazine", hi)
    for p in mag:
        K.transform(p, K.at(SOCKETS["socket_magazine"]))
    if hi:
        body += markings()
    return {"body": body, "magazine": mag, "rear_sight": rear_sight(hi)}, []
