## Art half of ZedWeaponPack, split out for file size; ZedWeaponPack extends this and is the public name.
extends RefCounted

const WEAPONS_DIR := "res://assets/weapon-pack/"
## The guns: our own kitbashes (art-src/guns/), one silhouette each. WEAPONS_DIR keeps the ammunition and throwables.
const KIT_DIR := "res://assets/kitbash/"
const FOOD_DIR := "res://assets/food-kit/"
## The high-detail models: baked textures embedded in each file (art-src/hq/build_hq.py).
const HQ_DIR := "res://assets/hq/"

# Kenney's Weapon Pack is modelled at real size and stands on its base (a pistol is 0.3 m, every gun lies along Z,
# origin at the middle of its bottom face), so the pose scale is zee's times REAL_SCALE and the model is lifted by half its height.

## How much larger than zee's blaster pose a real-sized gun is drawn.
const REAL_SCALE := 1.45
## Hip shift for the long-gun poses (view metres): REAL_SCALE made a 1 m gun land low and right with its grip out of frame.
const LONG_GUN_HIP := Vector3(-0.09, 0.08, 0.0)

## Which way the Weapon Pack's barrels point: +Z, the opposite of zee's blasters (-Z).
## Settled by a side render with a marker on +Z (docs/history.md); the rack cannot tell, as
## zee's blasters passed it reversed for years.
const GUN_FORWARD := Vector3.BACK


static func art_entries() -> Array[ZeeWeaponArt]:
	return [
		_own_magazine(_gun_art(ZedWeaponIds.SERVICE_PISTOL, "", ZeeWeaponArtTable.POSE_PISTOL, PISTOL_HEIGHT, HQ_DIR + "service_pistol.glb"), "service_pistol"),
		_boxed(_fed(_gun_art(ZedWeaponIds.SILENCED_PISTOL, "silenced_pistol", ZeeWeaponArtTable.POSE_PISTOL, 0.156), MAG_BOX, Vector3(0.0, 0.03, -0.150))),
		_boxed(_fed(_gun_art(ZedWeaponIds.UZI, "uzi", ZeeWeaponArtTable.POSE_PISTOL, 0.207), MAG_BOX, Vector3(0.0, 0.03, -0.04))),
		_own_magazine(_gun_art(ZedWeaponIds.TACTICAL_SMG, "", ZeeWeaponArtTable.POSE_RIFLE, SMG_HEIGHT, HQ_DIR + "tactical_smg.glb"), "tactical_smg"),
		_rounds(_hand_fed(_fed(_pulled(_gun_art(ZedWeaponIds.PUMP_SHOTGUN, "", ZeeWeaponArtTable.POSE_RIFLE, PUMP_HEIGHT, HQ_DIR + "pump_shotgun.glb"), 0.15), ROUND_SHELL, Vector3(0.0, 0.07, -0.07), true),
			Vector3(0.0, -0.10, 0.02), 1.6, Vector3.ZERO, &"RELOAD_KEYS_TUBE"), 3),
		_hand_fed(_fed(_gun_art(ZedWeaponIds.SAWED_OFF, "sawed_off", ZeeWeaponArtTable.POSE_RIFLE, 0.141), ROUND_SHELL, Vector3(0.0, 0.05, 0.0), true),
			Vector3(0.0, 0.10, -0.04), 1.6, Vector3.ZERO, &"RELOAD_KEYS_BREAK"),
		_rounds(_hand_fed(_fed(_low_fore(_scoped(_pulled(_gun_art(ZedWeaponIds.HUNTING_RIFLE, "", ZeeWeaponArtTable.POSE_RIFLE, DMR_HEIGHT, HQ_DIR + "hunting_rifle.glb"), 0.2))), ROUND_RIFLE, Vector3(0.0, 0.14, -0.08), true),
			Vector3(0.03, 0.12, 0.0), 0.35, Vector3(90.0, 0.0, 0.0), &"RELOAD_KEYS_BOLT"), 2),
		_own_magazine(_gun_art(ZedWeaponIds.AK_RIFLE, "", ZeeWeaponArtTable.POSE_RIFLE, AK_HEIGHT, HQ_DIR + "ak_rifle.glb"), "ak_rifle"),
		_hip(_own_magazine(_gun_art(ZedWeaponIds.ASSAULT_CARBINE, "", ZeeWeaponArtTable.POSE_RIFLE, CARBINE_HEIGHT, HQ_DIR + "m4_carbine.glb"), "m4_carbine"), 1.1, Vector3.ZERO),
		_box_fed(_heavy(_pulled(_gun_art(ZedWeaponIds.MACHINE_GUN, "machine_gun", ZeeWeaponArtTable.POSE_HEAVY, 0.197), 0.12), 1.9)),
		_hand_fed(_fed(_heavy(_gun_art(ZedWeaponIds.GRENADE_LAUNCHER, "grenade_launcher", ZeeWeaponArtTable.POSE_HEAVY, 0.271), 1.6), ROUND_GRENADE, Vector3(0.0, 0.20, -0.10), true),
			Vector3(0.0, 0.14, -0.06), 2.2, Vector3.ZERO, &"RELOAD_KEYS_BREAK"),
		_tamed(_hand_fed(_fed(_heavy(_gun_art(ZedWeaponIds.ROCKET_LAUNCHER, "rocket_launcher", ZeeWeaponArtTable.POSE_HEAVY, 0.193), 2.0), ROUND_ROCKET, Vector3(-0.046, 0.21, 0.30), true),
			Vector3(0.0, 0.0, -0.06), 1.5, Vector3(0.0, 180.0, 0.0), &"RELOAD_KEYS_MUZZLE"), ROCKET_TIP),
		_heavy(_gun_art(ZedWeaponIds.FLAMETHROWER, "flamethrower", ZeeWeaponArtTable.POSE_HEAVY, 0.151), 1.7),
		_thrown_art(ZedWeaponIds.MOLOTOV, FOOD_DIR + "wine-red.scn", 0.7),
		_thrown_art(ZedWeaponIds.PIPE_BOMB, WEAPONS_DIR + "grenadeVintage.glb", 0.9),
		_thrown_art(ZedWeaponIds.BILE_JAR, FOOD_DIR + "honey.scn", 0.6),
	]


## A gun: lies along +Z, stands on its base, [param height] metres tall (measured).
## On zee's hold, with its rotations handed over as [method hold_rotation]: the 180-degree turn
## flips a pitch and a roll, and written straight across the cant showed the gun's underside.
static func _gun_art(id: StringName, model: String, pose: StringName, height: float, path: String = "") -> ZeeWeaponArt:
	var art := ZeeWeaponArt.make(id, path if path != "" else KIT_DIR + model + ".glb")
	art.model_forward = GUN_FORWARD
	art.pose = pose
	art.view_scale = ZeeWeaponArtTable.pose_scale(pose) * REAL_SCALE
	art.world_scale = REAL_SCALE
	art.weight = ZeeWeaponArtTable.pose_weight(pose)
	art.view_rotation = hold_rotation(ZeeWeaponArtTable.pose_rotation(pose))
	art.aim_rotation = hold_rotation(Vector3.ZERO)
	# zee's blasters' aim place (ZeeWeaponArtTable._blaster): ZeeWeaponArt's default sits higher.
	art.view_offset = ZeeWeaponArtTable.pose_offset(pose)
	art.aim_offset = Vector3(0.0, -0.135, -0.46)
	# Lifted by half its height along the model's own up through the hold's basis (it carries
	# the cant), else the aim place sits half the height too high.
	var lift := Vector3(0.0, -height * 0.5, 0.0)
	art.view_offset += art.view_transform().basis * lift
	if pose == ZeeWeaponArtTable.POSE_RIFLE or pose == ZeeWeaponArtTable.POSE_HEAVY:
		art.view_offset += LONG_GUN_HIP
	art.aim_offset += art.aim_transform().basis * lift
	art.world_offset = Vector3(0.0, -height * 0.5 * art.world_scale, float(OS.get_environment("ZW_Z_" + String(id)) if OS.get_environment("ZW_Z_" + String(id)) != "" else "0"))
	return art


## zee's hold rotation (pitch, yaw, roll in degrees, written for a model pointing -Z) for a
## model pointing +Z: pitch and roll change sign, yaw does not.
static func hold_rotation(zee_rotation: Vector3) -> Vector3:
	return Vector3(-zee_rotation.x, zee_rotation.y, -zee_rotation.z)


static func _scoped(art: ZeeWeaponArt) -> ZeeWeaponArt:
	art.aim_scoped = true
	art.aim_zoom = 0.4
	art.aim_time = 0.2
	art.weight = 1.5
	return art


## What a reload carries in, from the Weapon Pack's own ammunition models: a box magazine for
## the pistols and the uzis, and a loose round (a shell, a cartridge, a grenade, a rocket) for
## everything fed by hand.
const MAG_BOX := WEAPONS_DIR + "ammo_uzi.glb"
const ROUND_SHELL := WEAPONS_DIR + "ammo_shotgun.glb"
const ROUND_RIFLE := WEAPONS_DIR + "ammo_sniper.glb"
const ROUND_BELT := WEAPONS_DIR + "ammo_machinegun.glb"
const ROUND_GRENADE := WEAPONS_DIR + "ammo_machinegunLauncher.glb"
const ROUND_ROCKET := WEAPONS_DIR + "ammo_rocketModern.glb"


## Gives a gun something to reload with: [param path] at [param offset] in the model's own
## space, where zee's support hand takes it. Without one zee's reload is the gun rolling and
## nothing else. A [param loose] round is drawn only while carried (`magazine_loose`, set by name).
static func _fed(art: ZeeWeaponArt, path: String, offset: Vector3, loose: bool = false) -> ZeeWeaponArt:
	var _with := art.with_magazine(path, offset)
	if loose:
		art.set(&"magazine_loose", true)
	return art


## A machine gun fed from a box: zee's ammunition box and belt, built in code (`magazine_part`),
## on the gun's right side (-X: the model points +Z), dropped and swapped on a reload. Set by
## name; a 9 cm belt round inside a fist read as the gun tilting.
static func _box_fed(art: ZeeWeaponArt) -> ZeeWeaponArt:
	art.set(&"magazine_part", &"ammo_box")
	art.magazine_offset = Vector3(-0.075, 0.0, -0.02)
	art.set(&"magazine_scale", 0.85)
	return art


## A launcher fed a round by hand (zee's `ZeeWeaponArt.load_from`): pushed from [param from]
## (model space), drawn at [param scale], turned by [param rotation], with zee's [param keys]
## by name (`ZeeWeaponPose.RELOAD_KEYS_*`). An older zee without them keeps its old reload.
static func _hand_fed(art: ZeeWeaponArt, from: Vector3, scale: float, rotation: Vector3, keys: StringName) -> ZeeWeaponArt:
	art.set(&"load_from", from)
	art.set(&"magazine_scale", scale)
	art.magazine_rotation = rotation
	# The key tables may live on a base script of the pose, so walk up.
	var table: Variant = null
	var pose: Script = ZeeWeaponPose
	while pose != null and table == null:
		table = pose.get_script_constant_map().get(keys)
		pose = pose.get_base_script()
	if table is Array:
		art.reload_keys = table
	return art


## A stick magazine for the pistols and the uzis: zee's `box_magazine`, half again as big, its
## foot below the grip's. Not `ammo_uzi`, a 6.5 cm cartridge that vanished inside the grip and
## glove. An older zee without the part keeps the cartridge.
static func _boxed(art: ZeeWeaponArt) -> ZeeWeaponArt:
	var parts: Variant = load(ZEE_RELOAD_PARTS) if ResourceLoader.exists(ZEE_RELOAD_PARTS) else null
	if parts is Script and (parts as Script).get_script_constant_map().has("BOX_MAGAZINE"):
		art.magazine_path = ""
		art.set(&"magazine_part", &"box_magazine")
		art.magazine_offset += Vector3(0.0, -0.065, 0.0)
		# Half again as big: at real size the gloves round the grip hid all but its foot.
		art.set(&"magazine_scale", 1.5)
	# Lifted further than zee's pose keys: these are real-sized, and a grip 23-33 cm tall puts
	# its foot (the magazine well) under the bottom of the screen at zee's reload height.
	art.reload_keys = lifted(ZeeWeaponArtTable.reload_keys(art.pose), RELOAD_LIFT)
	return art


## A gun that has its own magazine model (the high-detail ones): lifted reload keys, as for
## [method _boxed], but nothing drawn in the grip, since the model has its own.
static func _raised(art: ZeeWeaponArt) -> ZeeWeaponArt:
	# The model's own magazine is the one at rest; the prop is drawn only while the support hand
	# carries it in (`magazine_loose`), else a yellow box sat at the grip in every frame.
	art.set(&"magazine_loose", true)
	art.reload_keys = lifted(ZeeWeaponArtTable.reload_keys(art.pose), RELOAD_LIFT)
	return art


## A high-detail gun reloaded with its own magazine: `assets/hq/<gun>_mag.glb` (split by
## `art-src/hq/split_magazine.py`) is carried in while the gun's own node is hidden from pull
## to seat (`hide_during_reload`, set by name). `ammo_uzi` was a 6.5 cm cartridge, not a magazine.
static func _own_magazine(art: ZeeWeaponArt, gun: String) -> ZeeWeaponArt:
	var socket := {"service_pistol": Vector3(0.0, 0.107, -0.0559), "tactical_smg": Vector3(0.0, 0.155, 0.016), "ak_rifle": Vector3(0.0, 0.175, -0.014), "m4_carbine": Vector3(0.0, 0.175, -0.041)}
	var _with := art.with_magazine(HQ_DIR + gun + "_mag.glb", socket.get(gun, Vector3.ZERO))
	art.set(&"hide_during_reload", &"magazine")
	# The pistol's well is under the support fist: carried at the palm the magazine was behind
	# the glove from the pull to the seat (50-56% of the reload). Set by name, as zee's older
	# versions lack the field.
	if gun == "service_pistol":
		art.set(&"magazine_carry", Vector3(0.0, 0.07, 0.05))
	return _raised(art)


## How much higher than zee's keys a box-fed gun is raised mid-reload, in metres.
const RELOAD_LIFT := Vector3(-0.015, 0.075, 0.0)


## [param keys] with [param lift] added in proportion to how far each key already is from rest,
## so the ends stay at rest and the curve keeps its shape (no new corner for the suite's "never
## jolts" check to find).
static func lifted(keys: Array, lift: Vector3) -> Array:
	var most := 0.0
	for key: Array in keys:
		most = maxf(most, (key[1] as Vector3).length())
	if most <= 0.0001:
		return keys
	var out: Array = []
	for key: Array in keys:
		var weight := (key[1] as Vector3).length() / most
		out.append([key[0], (key[1] as Vector3) + lift * weight, key[2]])
	return out


## zee's parts built in code, by path (the file has no `class_name`).
const ZEE_RELOAD_PARTS := "res://addons/zee_weapons/view/zee_reload_parts.gd"


## How many rounds a hand-fed gun takes, one push each (`ZeeWeaponArt.load_count`, by name).
## The pump gun and hunting rifle are fed like zee's pump guns and bolt gun (`RELOAD_KEYS_TUBE`,
## `_BOLT`): one carry showed the round in one frame, and the lifted rifle read as a tilt.
static func _rounds(art: ZeeWeaponArt, count: int) -> ZeeWeaponArt:
	art.set(&"load_count", count)
	return art


## How much of zee's muzzle-up reload tip the rocket launcher keeps. At zee's full tip the
## muzzle is at the top of the screen and the support hand, sent after it, is behind the sight
## ring with the sleeve's cut end hanging in mid-air below it (the arm only, no hand).
const ROCKET_TIP := 0.55


## [param art]'s reload keys with every offset and turn scaled by [param amount]: the same curve
## (rest at both ends stays rest) shallower, so no new corner for the "never jolts" check.
static func _tamed(art: ZeeWeaponArt, amount: float) -> ZeeWeaponArt:
	var out: Array = []
	for key: Array in art.reload_keys:
		out.append([key[0], (key[1] as Vector3) * amount, (key[2] as Vector3) * amount])
	art.reload_keys = out
	return art


## The support hand lower on a gun with a scope on it: zee measures the fore-end's height as a
## share of the bounds, and a scope makes them tall, so the glove sat over barrel and scope at the
## hip and covered both.
static func _low_fore(art: ZeeWeaponArt) -> ZeeWeaponArt:
	art.set(&"fore_up", 0.22)
	return art


## A gun drawn [param scale] times larger at the hip, moved by [param shift] (the view's metres).
## The carbine's hip pose, zee's rifle hold, left it a small shape far to the right with its
## stock off the screen.
static func _hip(art: ZeeWeaponArt, scale: float, shift: Vector3) -> ZeeWeaponArt:
	art.view_scale *= scale
	art.view_offset += shift
	return art


## A long gun drawn [param back] metres nearer the body in the third-person hold: the arm's reach
## ends short of the fore-end, so the support hand bunched against the firing hand at the stock.
static func _pulled(art: ZeeWeaponArt, back: float) -> ZeeWeaponArt:
	art.world_offset.z += back
	return art


static func _heavy(art: ZeeWeaponArt, weight: float) -> ZeeWeaponArt:
	art.weight = weight
	return art


## A throwable: stands upright on its base, as zee's grenades do. Zee turns its grenades' +Y
## onto the view's forward, which hides a round grenade and draws a bottle as its dark base,
## so the model is said to face forward already and is held standing.
static func _thrown_art(id: StringName, path: String, scale: float) -> ZeeWeaponArt:
	var art := ZeeWeaponArt.make(id, path)
	art.model_forward = Vector3.FORWARD
	art.pose = ZeeWeaponArtTable.POSE_THROWN
	art.view_offset = ZeeWeaponArtTable.pose_offset(ZeeWeaponArtTable.POSE_THROWN)
	art.view_scale = ZeeWeaponArtTable.pose_scale(ZeeWeaponArtTable.POSE_THROWN) * scale
	art.world_scale = scale
	art.weight = ZeeWeaponArtTable.pose_weight(ZeeWeaponArtTable.POSE_THROWN)
	art.view_rotation = Vector3(10.0, 0.0, -12.0)
	art.aim_enabled = false
	return art


## The assault carbine's height, measured on its model with the standard magazine in
## (art-src/hq/out/measure.json): the lift to its middle, as for the kitbashed guns.
const CARBINE_HEIGHT := 0.279
## The service pistol's, magazine in.
const PISTOL_HEIGHT := 0.145
## The tactical SMG's, magazine in.
const SMG_HEIGHT := 0.237
## The pump shotgun's.
const PUMP_HEIGHT := 0.159
## The AK rifle's, magazine in.
const AK_HEIGHT := 0.277
## The marksman rifle's, scope on.
const DMR_HEIGHT := 0.204
