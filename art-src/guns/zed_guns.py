# One recipe per gun of this pack: which Quaternius parts it keeps, what of ours replaces the rest,
# and its colours. Each returns (gun object, length in metres).
#
# The length is the one ZedWeaponPack's hold was tuned for with the Weapon Pack model this
# replaces, so a gun lands where the old one sat. Recipes work in natural metres; the export
# scales the whole gun to that length.
#
# u / v are fractions of a donor's own side view (u from the butt to the muzzle, v from the
# bottom up), read off a side render (art-src/guns/build.py --preview).
import bpy
import math
from mathutils import Vector

from zed_kit import (at, bevel, box, cut, cyl, donor, erase, join, kenney, lowest, move, paint,
                     place, rail, rotate, scale, shear, taper, top_at, u2y, v2z)

# Metres per source unit: the Quaternius pack shares one scale.
U = 0.174


def _holes(y0, z, r, n, step, size, material="polymer"):
    """Cooling holes round a shroud: n rings of six small blocks."""
    out = []
    for i in range(n):
        for a in range(0, 360, 60):
            p = Vector((math.cos(math.radians(a)) * r, y0 + i * step, z + math.sin(math.radians(a)) * r))
            b = box(size, "ccc", p, material, 0.1)
            rotate(b, a, "Y", about=p)
            out.append(b)
    return out


# --- Service pistol: a slab-sided duty pistol, walnut grip panels, serrated, with a hammer ------
#
# Frame, slide, trigger and guard: Quaternius Pistol_3, in stainless and blued steel.
# Ours: the slide serrations front and back, both sights (a red dot in the front), the hammer
# spur, the lanyard ring and the magazine's heel plate.

def service_pistol():
    m = {"Wood": "walnut", "DarkMetal": "blued", "LightMetal": "stainless", "Black": "polymer", "Metal": "gunmetal"}
    gun = donor("Pistol_3", unit=U, mats=m, default_mat="blued")
    bevel(gun, 0.0012)
    front = at(gun, "cfc").y
    back = at(gun, "cbc").y
    # The donor's own bounds reach up to loose sight pieces, so the slide's top is read at a place.
    top = top_at(gun, (front + back) / 2, 0.03)
    parts = [gun]
    for i in range(6):
        parts.append(box((0.062, 0.0035, 0.02), "ccu", (0, back + 0.05 + i * 0.0085, top - 0.004), "steel", 0.0))
    for i in range(4):
        parts.append(box((0.062, 0.0035, 0.018), "ccu", (0, front - 0.1 + i * 0.0085, top - 0.004), "steel", 0.0))
    parts.append(box((0.006, 0.014, 0.012), "ccd", (0, front - 0.03, top - 0.001), "blued", 0.1))
    parts.append(box((0.0025, 0.004, 0.004), "ccd", (0, front - 0.03, top + 0.011), "red", 0.0))
    parts.append(box((0.018, 0.012, 0.01), "ccd", (0, back + 0.03, top - 0.001), "blued", 0.1))
    base = lowest(gun)
    parts.append(box((0.034, 0.05, 0.008), "ccu", (0, base.y, base.z + 0.004), "polymer", 0.15))
    parts.append(cyl(0.007, 0.006, "ccc", (0, base.y - 0.03, base.z + 0.01), axis="X", material="steel", sides=8))
    return join(parts, "service_pistol"), 0.294


# --- Silenced pistol: a rail-frame pistol with a screw-on suppressor and a reflex sight ---------
#
# Frame, slide, rail and grip: Quaternius Pistol_6. Suppressor: Quaternius's Silencer_2,
# stretched, with a mount collar. Reflex sight: Kenney Blaster Kit scope-small, shrunk.
# Ours: the collar, the extended magazine heel plate, the take-down lever.

def silenced_pistol():
    m = {"Metal": "graphite", "LightMetal": "tan", "Black": "polymer", "DarkMetal": "blued"}
    gun = donor("Pistol_6", unit=U, mats=m, default_mat="graphite")
    bevel(gun, 0.001)
    front = at(gun, "cfc").y
    top = at(gun, "ccu").z
    zc = v2z(gun, 0.84)
    sil = donor("Silencer_2", unit=U * 0.62, default_mat="blued")
    k = 0.165 / (at(sil, "cfc").y - at(sil, "cbc").y)
    scale(sil, (1.0, k, 1.0))
    place(sil, "cbc", (0, front - 0.004, zc))
    collar = cyl(0.0145, 0.012, "cbc", (0, front - 0.006, zc), material="steel", sides=10)
    parts = [gun, sil, collar]
    for i in range(3):
        parts.append(cyl(0.0185, 0.004, "cbc", (0, front + 0.035 + i * 0.045, zc), material="graphite", sides=10))
    dot = kenney("scope-small", "polymer")
    kk = 0.05 / (at(dot, "cfc").y - at(dot, "cbc").y)
    scale(dot, kk)
    place(dot, "cbd", (0, at(gun, "ccc").y + 0.02, top_at(gun, at(gun, "ccc").y + 0.02, 0.03) - 0.002))
    parts.append(dot)
    base = lowest(gun)
    parts.append(box((0.03, 0.045, 0.012), "ccu", (0, base.y - 0.004, base.z + 0.004), "tan", 0.15))
    parts.append(box((0.004, 0.01, 0.01), "ccc", (at(gun, "rcc").x, at(gun, "ccc").y - 0.005, v2z(gun, 0.64)), "signal", 0.1))
    return join(parts, "silenced_pistol"), 0.41


# --- Uzi: a folded-stock machine pistol with a perforated shroud ----------------------------------
#
# Receiver, grip, magazine and guard: Quaternius SubmachineGun_3 with its wire stock and foregrip
# taken off. Ours: the folded wire stock, the vented barrel shroud over a short barrel, the
# flip-up sights, the cocking knob and the heel plate.

def uzi():
    m = {"Metal": "graphite", "DarkMetal": "blued", "Black": "polymer", "Grey": "gunmetal"}
    gun = donor("SubmachineGun_3", unit=U, mats=m, default_mat="graphite")
    erase(gun, 0.0, 0.33)
    erase(gun, 0.68, 0.9, 0.0, 0.62)
    bevel(gun, 0.0012)
    front = at(gun, "cfc").y
    back = at(gun, "cbc").y
    zc = v2z(gun, 0.8)
    top = top_at(gun, (front + back) / 2, 0.04)
    parts = [gun]
    parts.append(cyl(0.011, 0.07, "cbc", (0, front - 0.012, zc), material="steel", sides=10))
    parts.append(cyl(0.021, 0.13, "cfc", (0, front - 0.012, zc), material="gunmetal", sides=10, chamfer=0.06))
    parts += _holes(front - 0.12, zc, 0.0205, 5, 0.024, (0.004, 0.006, 0.006))
    # Folded wire stock: a stirrup lying on the left of the receiver.
    parts.append(box((0.004, 0.17, 0.004), "rcc", (-0.0225, back + 0.14, zc + 0.012), "steel", 0.0))
    parts.append(box((0.004, 0.17, 0.004), "rcc", (-0.0225, back + 0.14, zc - 0.02), "steel", 0.0))
    parts.append(box((0.004, 0.006, 0.036), "rcc", (-0.0225, back + 0.055, zc - 0.004), "steel", 0.0))
    parts.append(box((0.008, 0.008, 0.044), "rcc", (-0.0225, back + 0.222, zc - 0.004), "rubber", 0.1))
    parts.append(box((0.006, 0.014, 0.012), "ccd", (0, front - 0.03, top - 0.002), "blued", 0.1))
    parts.append(box((0.016, 0.01, 0.012), "ccd", (0, back + 0.03, top - 0.002), "blued", 0.1))
    parts.append(cyl(0.007, 0.012, "ccc", (0, back + 0.06, top + 0.002), axis="Y", material="signal", sides=8))
    grip = lowest(gun)
    parts.append(box((0.038, 0.034, 0.006), "ccu", (0, grip.y, grip.z + 0.004), "rubber", 0.1))
    return join(parts, "uzi"), 0.38


# --- Tactical SMG: a rail SMG with a long suppressor, optic and flashlight -----------------------
#
# Receiver, folding stock, grip and magazine: Quaternius SubmachineGun_5, its rail teeth kept,
# muzzle off. Suppressor: Quaternius's Silencer_2, long. Optic: Scope_3, shrunk. Light: Flashlight
# under the rail. Ours: the collar and the suppressor's rings, the stock-side marker.

def tactical_smg():
    m = {"Metal": "gunmetal", "DarkMetal": "slate", "Black": "polymer", "Grey": "polymer"}
    gun = donor("SubmachineGun_5", keep=lambda p: p.u1 < 0.94 or p.v0 > 0.5, unit=U, mats=m, default_mat="gunmetal")
    bevel(gun, 0.001)
    front = u2y(gun, 0.93)
    zc = v2z(gun, 0.80)
    sil = donor("Silencer_2", unit=U * 0.78, default_mat="polymer")
    k = 0.3 / (at(sil, "cfc").y - at(sil, "cbc").y)
    scale(sil, (1.0, k, 1.0))
    place(sil, "cbc", (0, front - 0.03, zc))
    parts = [gun, sil]
    parts.append(cyl(0.019, 0.02, "cbc", (0, front - 0.04, zc), material="steel", sides=10))
    for i in range(4):
        parts.append(cyl(0.024, 0.006, "cbc", (0, front + 0.02 + i * 0.07, zc), material="graphite", sides=10))
    opt = donor("Scope_3", unit=U * 0.7, default_mat="polymer")
    place(opt, "ccd", (0, u2y(gun, 0.55), at(gun, "ccu").z))
    parts.append(opt)
    fl = donor("Flashlight", unit=U * 1.2, default_mat="steel")
    place(fl, "ccu", (0, u2y(gun, 0.80), v2z(gun, 0.64)))
    parts.append(fl)
    parts.append(box((0.004, 0.05, 0.012), "ccc", (at(gun, "rcc").x, u2y(gun, 0.45), v2z(gun, 0.78)), "signal", 0.1))
    return join(parts, "tactical_smg"), 0.628


# --- Pump shotgun: a full-stocked field shotgun, ghost-ring sights, side shells ------------------
#
# Receiver, trigger guard, walnut stock and pump: Quaternius Shotgun_2. Ours: the muzzle collar
# and the post front, the ghost-ring rear, the pump rings, six shells on a butt cuff, the pad.

def pump_shotgun():
    m = {"Metal": "gunmetal", "DarkMetal": "blued", "Black": "polymer", "Wood": "walnut", "DarkWood": "walnut"}
    gun = donor("Shotgun_2", unit=U, mats=m, default_mat="blued")
    bevel(gun, 0.0012)
    front = at(gun, "cfc").y
    back = at(gun, "cbc").y
    zt = v2z(gun, 0.80)
    zb = v2z(gun, 0.45)
    parts = [gun]
    parts.append(cyl(0.0115, 0.04, "cbc", (0, front - 0.004, zt), material="blued", sides=12))
    parts.append(box((0.012, 0.03, 0.016), "ccd", (0, front + 0.02, zt + 0.008), "polymer", 0.15))
    parts.append(box((0.004, 0.012, 0.02), "ccd", (0, front + 0.02, zt + 0.018), "red", 0.0))
    ring = cyl(0.011, 0.01, "ccc", (0, u2y(gun, 0.32), zt + 0.027), material="blued", sides=10)
    rotate(ring, 90, "X")
    parts.append(ring)
    parts.append(box((0.01, 0.016, 0.02), "ccd", (0, u2y(gun, 0.32), zt + 0.007), "blued", 0.1))
    bz = v2z(gun, 0.55)
    parts.append(box((0.052, 0.07, 0.03), "ccc", (0, back + 0.075, bz), "polymer", 0.2))
    for i in range(6):
        parts.append(cyl(0.0078, 0.012, "ccc", (0.021 - i * 0.0083, back + 0.075, bz + 0.0185), axis="Z", material="red", sides=8))
        parts.append(cyl(0.0078, 0.006, "ccc", (0.021 - i * 0.0083, back + 0.075, bz + 0.0125), axis="Z", material="brass", sides=8))
    parts.append(box((0.04, 0.012, 0.115), "cfc", (0, back + 0.004, v2z(gun, 0.55)), "rubber", 0.2))
    return join(parts, "pump_shotgun"), 0.566


# --- Sawn-off: a double-barrelled break-action with its barrels cut, bare grip ------------------
#
# Grip, lock and trigger guard: Quaternius Shotgun_ShortStock's rear third. Ours: everything
# forward of it: two side-by-side barrels, the hinge block and its pin, both hammers, the cut
# ends, the fore-end.

def sawed_off():
    m = {"Metal": "gunmetal", "DarkMetal": "blued", "Black": "polymer", "Wood": "ash", "DarkWood": "ash"}
    gun = donor("Shotgun_ShortStock", unit=U, mats=m, default_mat="blued")
    erase(gun, 0.45, 1.0)
    bevel(gun, 0.0012)
    front = u2y(gun, 0.45)
    top = at(gun, "ccu").z
    zc = top - 0.03
    parts = [gun]
    for sx in (-1, 1):
        parts.append(cyl(0.0125, 0.25, "cbc", (sx * 0.0125, front, zc + 0.002), material="blued", sides=12, chamfer=0.1))
        parts.append(box((0.006, 0.014, 0.022), "ccc", (sx * 0.012, front - 0.07, top - 0.002), "steel", 0.15))
    parts.append(box((0.016, 0.25, 0.008), "cbc", (0, front, zc + 0.0125), "blued", 0.1))
    parts.append(box((0.044, 0.05, 0.012), "ccd", (0, front + 0.045, zc - 0.012), "ash", 0.2))
    parts.append(box((0.05, 0.014, 0.04), "ccc", (0, front + 0.012, zc), "steel", 0.2))
    parts.append(cyl(0.004, 0.056, "ccc", (0, front + 0.012, zc), axis="X", material="brass", sides=8))
    parts.append(box((0.01, 0.034, 0.008), "ccd", (0, front - 0.04, top - 0.004), "steel", 0.2))
    parts.append(box((0.004, 0.006, 0.006), "ccu", (0, front + 0.248, zc + 0.0185), "red", 0.0))
    return join(parts, "sawed_off"), 0.502


# --- Hunting rifle: a walnut bolt-action with a straight-comb stock and a scope --------------------
#
# Stock, action and barrel: Quaternius SniperRifle_6, its original scope off. Scope: Quaternius's
# Scope_1 on two rings of ours. Ours: the brass bolt knob, the muzzle crown and barrel band, the
# recoil pad, the sling stud.

def hunting_rifle():
    m = {"Green": "walnut", "Black": "polymer", "DarkMetal": "blued", "Grey": "steel", "Glass": "lens",
         "Metal": "steel", "LightMetal": "steel", "Wood": "walnut", "DarkWood": "walnut"}
    gun = donor("SniperRifle_6", unit=U, mats=m, default_mat="blued")
    erase(gun, 0.2, 0.75, 0.74, 1.0)
    bevel(gun, 0.0015)
    zc = v2z(gun, 0.72)
    rb = u2y(gun, 0.34)
    parts = [gun]
    sc = donor("Scope_1", unit=U * 0.95, default_mat="polymer")
    place(sc, "ccd", (0, rb + 0.10, zc + 0.028))
    parts.append(sc)
    lens_r = (at(sc, "ccu").z - at(sc, "ccd").z) * 0.42
    parts.append(cyl(lens_r * 1.05, 0.04, "cbc", (0, at(sc, "cfc").y - 0.004, at(sc, "cfc").z), material="graphite", sides=12))
    for dy in (0.05, 0.15):
        parts.append(box((0.016, 0.014, 0.03), "cbd", (0, rb + dy, zc + 0.012), "blued", 0.2))
    parts.append(cyl(0.01, 0.018, "lcc", (at(gun, "rcc").x + 0.026, rb + 0.06, zc - 0.01), axis="X", material="brass", sides=10))
    parts.append(cyl(0.004, 0.032, "lcc", (at(gun, "rcc").x - 0.0005, rb + 0.06, zc - 0.006), axis="X", material="steel", sides=6))
    muz = at(gun, "cfc")
    parts.append(cyl(0.0105, 0.014, "cfc", (0, muz.y + 0.002, zc), material="steel", sides=12))
    parts.append(cyl(0.0125, 0.02, "cbc", (0, u2y(gun, 0.52), zc), material="blued", sides=12))
    parts.append(rail(0.15, "cbd", (0, rb + 0.0, zc + 0.015), width=0.02))
    parts.append(box((0.04, 0.016, v2z(gun, 0.62) - v2z(gun, 0.02)), "cfd", (0, at(gun, "cbc").y + 0.006, v2z(gun, 0.02)), "rubber", 0.2))
    parts.append(cyl(0.005, 0.012, "ccu", (0, u2y(gun, 0.08), at(gun, "ccd").z + 0.05), axis="X", material="steel", sides=8))
    return join(parts, "hunting_rifle"), 1.04


# --- Machine gun: a belt-fed support gun with a vented heavy barrel, bipod and ammunition box ------
#
# Receiver and guard: Quaternius AssaultRifle_1's. Stock: its sibling AssaultRifle_5's, in olive.
# Bipod: Quaternius's, folded forward. Ours: the heavy barrel in a vented shroud, the feed tray,
# the ammunition box, the brass belt looping into the tray, the carry handle, the iron post.

def machine_gun():
    m = {"Metal": "gunmetal", "DarkMetal": "blued", "Black": "polymer", "Wood": "walnut", "DarkWood": "walnut",
         "Grey": "graphite"}
    recv = donor("AssaultRifle_1", keep=lambda p: p.u1 < 0.62 and not (p.u0 > 0.25 and p.v1 < 0.36 and p.mat in ("Grey", "Black", "Metal")),
                 unit=U, mats=m, default_mat="gunmetal")
    bevel(recv, 0.0012)
    front = u2y(recv, 0.6)
    zc = v2z(recv, 0.76)
    parts = [recv]
    parts.append(cyl(0.03, 0.30, "cbc", (0, front - 0.01, zc - 0.004), material="graphite", sides=12, chamfer=0.05))
    parts += _holes(front + 0.01, zc - 0.004, 0.03, 6, 0.045, (0.004, 0.012, 0.01))
    parts.append(cyl(0.013, 0.17, "cbc", (0, front + 0.28, zc - 0.004), material="steel", sides=10))
    parts.append(cyl(0.02, 0.05, "cbc", (0, front + 0.43, zc - 0.004), material="blued", sides=8, chamfer=0.05))
    parts.append(box((0.006, 0.012, 0.04), "ccd", (0, front + 0.3, zc + 0.025), "blued", 0.1))
    stock = donor("AssaultRifle_5", keep=lambda p: p.uc < 0.3, unit=U, default_mat="olive")
    back = at(recv, "cbu")
    place(stock, "cfu", (0, back.y + 0.004, back.z - 0.008))
    bevel(stock, 0.0012)
    parts.append(stock)
    parts.append(box((0.06, 0.09, 0.014), "ccd", (0, u2y(recv, 0.43), at(recv, "ccu").z - 0.004), "gunmetal", 0.2))
    parts.append(box((0.04, 0.09, 0.075), "rcu", (-0.026, u2y(recv, 0.45), v2z(recv, 0.3)), "olive", 0.15))
    for i in range(7):
        parts.append(cyl(0.005, 0.034, "ccc", (-0.026 + 0.003 * math.sin(i * 0.9), u2y(recv, 0.45), v2z(recv, 0.3) + 0.01 + i * 0.012),
                         axis="X", material="brass", sides=6))
    parts.append(box((0.01, 0.1, 0.03), "ccd", (0, u2y(recv, 0.5), at(recv, "ccu").z + 0.006), "blued", 0.2))
    for sx in (-1, 1):
        leg = box((0.008, 0.008, 0.15), "ccu", (sx * 0.045, front + 0.2, zc - 0.03), "blued", 0.1)
        rotate(leg, sx * 25, "Y", about=Vector((sx * 0.02, front + 0.2, zc - 0.03)))
        parts.append(leg)
    parts.append(box((0.05, 0.016, 0.016), "ccc", (0, front + 0.2, zc - 0.03), "blued", 0.2))
    return join(parts, "machine_gun"), 0.78


# --- Grenade launcher: a revolving six-shot launcher with a drum, a fat barrel and a stock --------
#
# Frame, trigger, guard and grip: Quaternius Revolver_2, scaled up by half. Stock: Quaternius's
# Stock accessory, in tan. Foregrip: Quaternius's Grip. Ours: the drum with its chamber ring,
# the wide short barrel and muzzle collar, the ladder sight.

def grenade_launcher():
    m = {"Metal": "gunmetal", "LightMetal": "blued", "Grey": "rubber", "DarkWood": "tan", "Wood": "tan", "DarkMetal": "blued"}
    frame = donor("Revolver_2", keep=lambda p: not (p.u0 > 0.62), unit=U * 1.55, mats=m, default_mat="gunmetal")
    bevel(frame, 0.002)
    front = u2y(frame, 0.62)
    zc = v2z(frame, 0.77)
    drum_r = 0.058
    parts = [frame]
    drum = cyl(drum_r, 0.1, "ccc", (0, u2y(frame, 0.45), zc), material="steel", sides=12, chamfer=0.06)
    parts.append(drum)
    for a in range(0, 360, 60):
        x = math.cos(math.radians(a)) * drum_r * 0.62
        z = math.sin(math.radians(a)) * drum_r * 0.62
        parts.append(cyl(0.0125, 0.012, "cfc", (x, at(drum, "ccc").y + 0.05, zc + z), material="polymer", sides=8))
    parts.append(cyl(drum_r * 1.05, 0.012, "ccc", (0, at(drum, "cbc").y + 0.02, zc), material="gunmetal", sides=12))
    parts.append(cyl(0.032, 0.17, "cbc", (0, front - 0.02, zc - 0.004), material="blued", sides=12))
    parts.append(cyl(0.039, 0.024, "cfc", (0, front + 0.15, zc - 0.004), material="graphite", sides=12))
    parts.append(box((0.01, 0.03, 0.05), "ccd", (0, front + 0.01, zc + 0.03), "blued", 0.1))
    parts.append(box((0.01, 0.01, 0.034), "ccd", (0, front + 0.01, zc + 0.078), "steel", 0.0))
    stock = donor("Stock", unit=U * 0.95, default_mat="tan")
    back = at(frame, "cbu")
    place(stock, "cfu", (0, back.y + 0.12, back.z - 0.015))
    parts.append(stock)
    gr = donor("Grip", unit=U * 1.2, default_mat="rubber")
    place(gr, "ccu", (0, front + 0.06, zc - 0.036))
    parts.append(gr)
    return join(parts, "grenade_launcher"), 0.60


# --- Rocket launcher: a shoulder-fired tube with a warhead showing at the front -----------------
#
# Grips and sight: Quaternius Grip (twice) and Scope_2. Ours: the thin launch tube, the flared
# blast cone, the pointed warhead on its stem, the walnut heat guard, the sight's bracket, the
# trigger housing, the shoulder pad.

def rocket_launcher():
    R = 0.034
    L = 0.70
    parts = [cyl(R, L, "cbc", (0, 0, 0), material="olive", sides=14, chamfer=0.04)]
    parts.append(cyl(R * 1.9, 0.1, "cbc", (0, -0.03, 0), material="graphite", sides=14, radius2=R * 1.0))
    parts.append(cyl(R * 1.12, 0.03, "cbc", (0, 0.1, 0), material="steel", sides=14))
    parts.append(cyl(R * 1.12, 0.03, "cbc", (0, L - 0.03, 0), material="steel", sides=14))
    parts.append(cyl(R * 0.55, 0.05, "cbc", (0, L, 0), material="blued", sides=10))
    parts.append(cyl(R * 1.4, 0.10, "cbc", (0, L + 0.04, 0), material="tan", sides=14, chamfer=0.1))
    parts.append(cyl(R * 1.4, 0.12, "cbc", (0, L + 0.13, 0), material="red", sides=14, radius2=R * 0.15, chamfer=0.0))
    parts.append(cyl(R * 1.42, 0.008, "cbc", (0, L + 0.07, 0), material="signal", sides=14))
    parts.append(cyl(R * 1.18, 0.2, "cbc", (0, 0.26, 0), material="walnut", sides=14, chamfer=0.06))
    for i in range(4):
        parts.append(cyl(R * 1.2, 0.008, "cbc", (0, 0.285 + i * 0.045, 0), material="blued", sides=14))
    hs = box((0.03, 0.08, 0.034), "ccu", (0, 0.46, -R + 0.004), "polymer", 0.25)
    parts.append(hs)
    pg = donor("Grip", unit=U * 1.0, default_mat="rubber")
    place(pg, "ccu", (0, 0.46, at(hs, "ccd").z + 0.004))
    parts.append(pg)
    fg = donor("Grip", unit=U * 0.85, default_mat="rubber")
    rotate(fg, -8, "X")
    place(fg, "ccu", (0, 0.3, -R + 0.004))
    parts.append(fg)
    sc = donor("Scope_2", unit=U * 0.62, default_mat="polymer")
    place(sc, "lcc", (-R - 0.012, 0.44, R * 0.5))
    parts.append(sc)
    parts.append(box((0.016, 0.03, 0.03), "lcc", (-R + 0.004, 0.44, R * 0.4), "blued", 0.2))
    parts.append(box((0.04, 0.02, 0.07), "ccc", (0, -0.01, -0.004), "rubber", 0.2))
    return join(parts, "rocket_launcher"), 0.788


# --- Flamethrower: a fuel-tank wand with a pilot light and a hose ------------------------------
#
# Grips: Quaternius Grip, twice. Ours: the long wand and the finned barrel shroud, the fuel tank
# slung under it with its bands and valve, the nozzle, the pilot flame, the hose.

def flamethrower():
    wz = 0.0
    parts = [cyl(0.014, 0.58, "cbc", (0, 0, wz), material="steel", sides=12)]
    parts.append(cyl(0.024, 0.34, "cbc", (0, 0.08, wz), material="graphite", sides=12, chamfer=0.06))
    for i in range(6):
        parts.append(cyl(0.028, 0.008, "cbc", (0, 0.1 + i * 0.054, wz), material="blued", sides=12))
    parts.append(cyl(0.021, 0.07, "cbc", (0, 0.58, wz), material="blued", sides=12, radius2=0.03))
    parts.append(cyl(0.007, 0.07, "cbc", (0, 0.62, wz - 0.034), material="steel", sides=8))
    parts.append(cyl(0.007, 0.04, "cbc", (0, 0.695, wz - 0.034), material="signal", sides=8, radius2=0.002, chamfer=0))
    parts.append(cyl(0.05, 0.34, "cbc", (0, 0.02, wz - 0.095), material="red", sides=14, chamfer=0.12))
    for y in (0.07, 0.29):
        parts.append(cyl(0.0515, 0.022, "cbc", (0, y, wz - 0.095), material="steel", sides=14))
    parts.append(cyl(0.015, 0.03, "ccd", (0, 0.2, wz - 0.045), axis="Z", material="brass", sides=8))
    parts.append(cyl(0.02, 0.01, "ccu", (0, 0.2, wz - 0.002), axis="Z", material="stainless", sides=10))
    parts.append(box((0.008, 0.02, 0.02), "ccd", (0, 0.2, wz - 0.045), "polymer", 0.2))
    pg = donor("Grip", unit=U * 1.0, default_mat="rubber")
    place(pg, "ccu", (0, 0.18, wz - 0.018))
    parts.append(pg)
    parts.append(box((0.012, 0.05, 0.02), "ccu", (0, 0.22, wz - 0.016), "polymer", 0.2))
    fg = donor("Grip", unit=U * 0.8, default_mat="rubber")
    place(fg, "ccu", (0, 0.4, wz - 0.022))
    parts.append(fg)
    for i in range(5):
        parts.append(cyl(0.008, 0.03, "ccc", (0, 0.04 + i * 0.022, wz - 0.052 + 0.02 * math.sin(i * 0.8)), material="rubber", sides=6))
    parts.append(box((0.012, 0.02, 0.028), "ccd", (0, 0.5, wz + 0.014), "blued", 0.1))
    return join(parts, "flamethrower"), 0.588


RECIPES = {
    "service_pistol": service_pistol,
    "silenced_pistol": silenced_pistol,
    "uzi": uzi,
    "tactical_smg": tactical_smg,
    "pump_shotgun": pump_shotgun,
    "sawed_off": sawed_off,
    "hunting_rifle": hunting_rifle,
    "machine_gun": machine_gun,
    "grenade_launcher": grenade_launcher,
    "rocket_launcher": rocket_launcher,
    "flamethrower": flamethrower,
}
