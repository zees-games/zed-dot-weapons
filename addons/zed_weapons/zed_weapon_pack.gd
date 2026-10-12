class_name ZedWeaponPack
extends RefCounted

## The second pack: fourteen weapons as dot-weapon documents, their art as zee-dot-weapons
## art entries, and [method install], which hands both to zee.
##
## [b]A pack on top of a pack, not beside it.[/b] zee-dot-weapons already has the half that
## draws (rig, view model, world model, effects, sounds, netcode, rollback), and a second
## copy of all that for fourteen more weapons would be two rigs a game has to choose between.
## So this is only content: documents a server validates, filenames a client loads, and a
## sound class per weapon. `ZeeWeaponPack.add_source` puts them in every catalogue zee builds,
## which is every rig's default, so a game that calls [method install] carries both packs on
## one rig with nothing else changed.
##
## [b]What a throwable does is the game's.[/b] dot-weapon spawns nothing; it describes a
## projectile and hands it over. The molotov, the pipe bomb and the bile jar are thrown the
## way zee's frag is, and say what they are by their tags ([ZedWeaponIds]).

# No CHANNEL: a table of documents. zee logs a refused id itself.

const SOURCE := &"zed"

const TICK_RATE := 64

const HITSCAN := "res://addons/dot_weapon/behaviour/dot_weapon_hitscan.gd"
const PROJECTILE := "res://addons/dot_weapon/behaviour/dot_weapon_projectile.gd"
const THROWN := "res://addons/dot_weapon/behaviour/dot_weapon_thrown.gd"

const WEAPONS_DIR := "res://assets/weapon-pack/"
const FOOD_DIR := "res://assets/food-kit/"


static func rpm_ticks(rpm: float) -> int:
	return maxi(1, int(round(60.0 / rpm * float(TICK_RATE))))


static func sec_ticks(seconds: float) -> int:
	return maxi(0, int(round(seconds * float(TICK_RATE))))


# --- Installing ---------------------------------------------------------------

## Adds this pack's weapons, art and sounds to zee-dot-weapons. Safe to call twice.
##
## [b]Before the first rig is set up.[/b] A rig builds its catalogue once, in `setup()`, so a
## rig built before this ran carries zee's weapons only, for as long as it lives.
static func install() -> void:
	# [b]A static method, never a lambda.[/b] zee keeps these in a static variable, which the
	# engine clears after it has freed the scripts at exit; a lambda held there outlives the
	# script it was written in and the process aborts on the way out (`double free or
	# corruption`, exit 134, after every check has passed). Found by dot-server-deploy's
	# zombiezone_client; `tools/exit_check.gd` and the suite's "exiting" section hold it.
	ZeeWeaponPack.add_source(SOURCE, Callable(ZedWeaponPack, &"weapons"))
	ZeeWeaponArtTable.add_source(SOURCE, Callable(ZedWeaponPack, &"art"))

	for id: StringName in SOUNDS:
		ZeeWeaponSound.set_class(id, SOUNDS[id])


## Takes this pack out again: a game unloading in a shell that loads the next.
static func uninstall() -> void:
	ZeeWeaponPack.remove_source(SOURCE)
	ZeeWeaponArtTable.remove_source(SOURCE)


static func installed() -> bool:
	return ZeeWeaponPack.source_names().has(String(SOURCE))


## Which of zee's baked reports each weapon sounds like.
const SOUNDS := {
	ZedWeaponIds.SERVICE_PISTOL: &"light",
	ZedWeaponIds.SILENCED_PISTOL: &"light",
	ZedWeaponIds.UZI: &"light",
	ZedWeaponIds.TACTICAL_SMG: &"light",
	ZedWeaponIds.PUMP_SHOTGUN: &"shotgun",
	ZedWeaponIds.SAWED_OFF: &"shotgun",
	ZedWeaponIds.HUNTING_RIFLE: &"sniper",
	ZedWeaponIds.MACHINE_GUN: &"heavy",
	ZedWeaponIds.GRENADE_LAUNCHER: &"launcher",
	ZedWeaponIds.ROCKET_LAUNCHER: &"launcher",
	ZedWeaponIds.FLAMETHROWER: &"minigun",
}


# --- The documents ---------------------------------------------------------------

static func weapons(types: Dictionary = {}) -> Array[DotWeaponDef]:
	var t := types if not types.is_empty() else ZeeWeaponDamage.table()

	return [
		service_pistol(t), silenced_pistol(t), uzi(t),
		tactical_smg(t), pump_shotgun(t), sawed_off(t), hunting_rifle(t),
		machine_gun(t), grenade_launcher(t), rocket_launcher(t), flamethrower(t),
		molotov(t), pipe_bomb(t), bile_jar(t),
	]


static func table(types: Dictionary = {}) -> Dictionary:
	var out: Dictionary = {}

	for def in weapons(types):
		out[def.id] = def

	return out


# --- Sidearms ----------------------------------------------------------------------

## The plain one: what a survivor is handed when there is nothing else.
static func service_pistol(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.SERVICE_PISTOL, "Service Pistol", ZeeWeaponIds.SLOT_SIDEARM,
		DotWeaponDef.Fire.SEMI, rpm_ticks(400.0))
	def.tags = [ZeeWeaponIds.TAG_SIDEARM]
	def.ammo_type = ZeeWeaponIds.AMMO_LIGHT
	def.magazine = 15
	def.reserve = 90
	def.reserve_max = 180
	def.reload_ticks = sec_ticks(1.5)
	def.deploy_ticks = sec_ticks(0.25)
	def.holster_ticks = sec_ticks(0.18)

	var b := _ballistics(t, 28.0)
	b.spread = 0.6
	b.spread_moving = 1.6
	b.bloom = 0.5
	b.bloom_max = 3.0
	b.recoil_pitch = 0.8
	b.max_range = 120.0
	def.tuning = b
	return def


## Quieter and a little weaker: a shot that does not wake the room.
static func silenced_pistol(t: Dictionary = {}) -> DotWeaponDef:
	var def := service_pistol(t)
	def.id = ZedWeaponIds.SILENCED_PISTOL
	def.display_name = "Silenced Pistol"
	def.tags = [ZeeWeaponIds.TAG_SIDEARM, ZeeWeaponIds.TAG_SILENCED]
	def.magazine = 12
	(def.tuning as DotWeaponBallistics).damage = 24.0
	return def


## Automatic in one hand: a sidearm that empties itself.
static func uzi(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.UZI, "Uzi", ZeeWeaponIds.SLOT_SIDEARM,
		DotWeaponDef.Fire.AUTO, rpm_ticks(900.0))
	def.tags = [ZeeWeaponIds.TAG_SIDEARM, ZeeWeaponIds.TAG_AUTOMATIC]
	def.ammo_type = ZeeWeaponIds.AMMO_LIGHT
	def.magazine = 32
	def.reserve = 128
	def.reserve_max = 256
	def.reload_ticks = sec_ticks(1.8)
	def.deploy_ticks = sec_ticks(0.25)
	def.holster_ticks = sec_ticks(0.18)

	var b := _ballistics(t, 14.0)
	b.spread = 2.0
	b.spread_moving = 2.8
	b.bloom = 0.2
	b.bloom_max = 3.5
	b.recoil_pitch = 0.35
	b.recoil_yaw = 0.25
	b.max_range = 80.0
	def.tuning = b
	return def


# --- Primaries ---------------------------------------------------------------------

static func tactical_smg(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.TACTICAL_SMG, "Tactical SMG", ZeeWeaponIds.SLOT_PRIMARY,
		DotWeaponDef.Fire.AUTO, rpm_ticks(850.0))
	def.tags = [ZeeWeaponIds.TAG_PRIMARY, ZeeWeaponIds.TAG_AUTOMATIC, ZeeWeaponIds.TAG_SILENCED]
	def.ammo_type = ZeeWeaponIds.AMMO_LIGHT
	def.magazine = 50
	def.reserve = 200
	def.reserve_max = 400
	def.reload_ticks = sec_ticks(2.2)
	def.deploy_ticks = sec_ticks(0.32)
	def.holster_ticks = sec_ticks(0.22)

	var b := _ballistics(t, 19.0)
	b.spread = 1.2
	b.spread_moving = 2.2
	b.bloom = 0.12
	b.bloom_max = 2.5
	b.recoil_pitch = 0.3
	b.recoil_yaw = 0.18
	b.max_range = 110.0
	def.tuning = b
	return def


## Eight shells, one at a time: the answer to a crowd in a doorway.
static func pump_shotgun(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.PUMP_SHOTGUN, "Pump Shotgun", ZeeWeaponIds.SLOT_PRIMARY,
		DotWeaponDef.Fire.SEMI, rpm_ticks(70.0))
	def.tags = [ZeeWeaponIds.TAG_PRIMARY]
	def.ammo_type = ZeeWeaponIds.AMMO_SHELL
	def.magazine = 8
	def.reserve = 56
	def.reserve_max = 112
	def.reload_ticks = sec_ticks(3.4)
	def.deploy_ticks = sec_ticks(0.4)
	def.holster_ticks = sec_ticks(0.28)

	var b := _ballistics(t, 14.0)
	b.pellets = 10
	b.fixed_pattern = true
	b.spread = 4.6
	b.spread_moving = 0.6
	b.recoil_pitch = 2.6
	b.max_range = 24.0
	def.tuning = b
	return def


## Two barrels, both at once if you are quick: the most damage in the pack inside three
## metres and almost none at fifteen.
static func sawed_off(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.SAWED_OFF, "Sawed-Off", ZeeWeaponIds.SLOT_PRIMARY,
		DotWeaponDef.Fire.SEMI, rpm_ticks(240.0))
	def.tags = [ZeeWeaponIds.TAG_PRIMARY]
	def.ammo_type = ZeeWeaponIds.AMMO_SHELL
	def.magazine = 2
	def.reserve = 40
	def.reserve_max = 80
	def.reload_ticks = sec_ticks(2.0)
	def.deploy_ticks = sec_ticks(0.3)
	def.holster_ticks = sec_ticks(0.2)

	var b := _ballistics(t, 12.0)
	b.pellets = 14
	b.fixed_pattern = true
	b.spread = 7.5
	b.spread_moving = 1.0
	b.recoil_pitch = 3.6
	b.max_range = 15.0
	def.tuning = b
	return def


## Bolt action, scoped, and a primary: a sniper that leaves the heavy slot free.
static func hunting_rifle(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.HUNTING_RIFLE, "Hunting Rifle", ZeeWeaponIds.SLOT_PRIMARY,
		DotWeaponDef.Fire.SEMI, rpm_ticks(60.0))
	def.tags = [ZeeWeaponIds.TAG_PRIMARY, ZeeWeaponIds.TAG_SCOPED]
	def.ammo_type = ZeeWeaponIds.AMMO_HEAVY
	def.magazine = 5
	def.reserve = 40
	def.reserve_max = 80
	def.reload_ticks = sec_ticks(2.8)
	def.deploy_ticks = sec_ticks(0.5)
	def.holster_ticks = sec_ticks(0.35)

	var b := _ballistics(t, 90.0)
	b.spread = 0.0
	b.spread_moving = 6.0
	b.spread_airborne = 12.0
	b.spread_crouched = 0.0
	b.recoil_pitch = 3.2
	b.max_range = 600.0
	def.tuning = b
	return def


# --- Heavies ------------------------------------------------------------------------

## A hundred-round box and a long reload: what you carry when the horde is the plan.
static func machine_gun(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.MACHINE_GUN, "Machine Gun", ZeeWeaponIds.SLOT_HEAVY,
		DotWeaponDef.Fire.AUTO, rpm_ticks(750.0))
	def.tags = [ZeeWeaponIds.TAG_HEAVY, ZeeWeaponIds.TAG_AUTOMATIC, ZeeWeaponIds.TAG_PRIMARY]
	def.ammo_type = ZeeWeaponIds.AMMO_BELT
	def.magazine = 100
	def.reserve = 200
	def.reserve_max = 400
	def.reload_ticks = sec_ticks(5.0)
	def.deploy_ticks = sec_ticks(0.9)
	def.holster_ticks = sec_ticks(0.6)

	var b := _ballistics(t, 22.0)
	b.spread = 1.8
	b.spread_moving = 4.0
	b.spread_airborne = 6.0
	b.bloom = 0.06
	b.bloom_max = 2.2
	b.recoil_pitch = 0.4
	b.recoil_yaw = 0.2
	b.max_range = 160.0
	def.tuning = b
	return def


## One shell, lobbed, and it goes off on whatever it meets.
static func grenade_launcher(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.GRENADE_LAUNCHER, "Grenade Launcher", ZeeWeaponIds.SLOT_HEAVY,
		DotWeaponDef.Fire.SEMI, rpm_ticks(60.0))
	def.behaviour_path = PROJECTILE
	def.tags = [ZeeWeaponIds.TAG_HEAVY, ZeeWeaponIds.TAG_EXPLOSIVE]
	def.ammo_type = ZeeWeaponIds.AMMO_ORDNANCE
	def.magazine = 1
	def.reserve = 15
	def.reserve_max = 30
	def.reload_ticks = sec_ticks(2.4)
	def.deploy_ticks = sec_ticks(0.5)
	def.holster_ticks = sec_ticks(0.34)

	var b := _explosive(t, 30.0, 32.0, 0.9, 5.0, 130.0)
	b.recoil_pitch = 2.8
	def.tuning = b
	return def


## Straight and slow to reload: one big hole in whatever is in front of you.
static func rocket_launcher(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.ROCKET_LAUNCHER, "Rocket Launcher", ZeeWeaponIds.SLOT_HEAVY,
		DotWeaponDef.Fire.SEMI, rpm_ticks(40.0))
	def.behaviour_path = PROJECTILE
	def.tags = [ZeeWeaponIds.TAG_HEAVY, ZeeWeaponIds.TAG_EXPLOSIVE]
	def.ammo_type = ZeeWeaponIds.AMMO_ORDNANCE
	def.magazine = 1
	def.reserve = 6
	def.reserve_max = 12
	def.reload_ticks = sec_ticks(3.5)
	def.deploy_ticks = sec_ticks(0.8)
	def.holster_ticks = sec_ticks(0.5)

	var b := _explosive(t, 60.0, 36.0, 0.0, 6.5, 240.0)
	b.recoil_pitch = 4.0
	def.tuning = b
	return def


## Short, wide and burning: everything it touches is alight, which in a game with fire is
## most of the damage.
static func flamethrower(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.FLAMETHROWER, "Flamethrower", ZeeWeaponIds.SLOT_HEAVY,
		DotWeaponDef.Fire.AUTO, rpm_ticks(600.0))
	def.tags = [ZeeWeaponIds.TAG_HEAVY, ZeeWeaponIds.TAG_AUTOMATIC, ZedWeaponIds.TAG_INCENDIARY]
	def.ammo_type = ZedWeaponIds.AMMO_FUEL
	# A tank, not a magazine: it runs dry and that is that.
	def.magazine = 0
	def.reserve = 300
	def.reserve_max = 300
	def.auto_reload = false
	def.reload_ticks = 0
	def.deploy_ticks = sec_ticks(0.8)
	def.holster_ticks = sec_ticks(0.5)

	var b := _ballistics(t, 5.0)
	b.pellets = 4
	b.spread = 7.0
	b.spread_moving = 1.0
	b.recoil_pitch = 0.05
	b.max_range = 9.0
	def.tuning = b
	return def


# --- Thrown ------------------------------------------------------------------------
#
# Thrown the way zee's frag is (dot-weapon's thrown behaviour, charged for distance), and
# told apart by their tags. None of them has a fuse except the pipe bomb's, which is the
# game's: it lands, beeps and draws the horde, then goes off.

static func molotov(t: Dictionary = {}) -> DotWeaponDef:
	return _thrown(t, ZedWeaponIds.MOLOTOV, "Molotov", ZedWeaponIds.AMMO_MOLOTOV, ZedWeaponIds.TAG_MOLOTOV)


static func pipe_bomb(t: Dictionary = {}) -> DotWeaponDef:
	var def := _thrown(t, ZedWeaponIds.PIPE_BOMB, "Pipe Bomb", ZedWeaponIds.AMMO_PIPE_BOMB, ZedWeaponIds.TAG_PIPE_BOMB)
	def.tags.append(ZeeWeaponIds.TAG_EXPLOSIVE)
	var b := def.tuning as DotWeaponBallistics
	b.splash_radius = 6.0
	b.splash_damage = 300.0
	return def


static func bile_jar(t: Dictionary = {}) -> DotWeaponDef:
	return _thrown(t, ZedWeaponIds.BILE_JAR, "Bile Jar", ZedWeaponIds.AMMO_BILE, ZedWeaponIds.TAG_BILE)


# --- Builders ------------------------------------------------------------------------

static func _gun(id: StringName, name: String, slot: int, fire: DotWeaponDef.Fire, interval: int) -> DotWeaponDef:
	var def := DotWeaponDef.new()
	def.authored_tick_rate = TICK_RATE
	def.id = id
	def.display_name = name
	def.behaviour_path = HITSCAN
	def.slot = slot
	def.fire_mode = fire
	def.use_interval_ticks = interval
	def.cost_per_use = 1
	# zee's bash, which every one of its guns has; ZeeWeaponBash reads these through the rig.
	def.params = {
		&"bash_damage": 42.0,
		&"bash_reach": 1.9,
		&"bash_cooldown_ticks": sec_ticks(0.8),
	}
	return def


static func _ballistics(t: Dictionary, damage: float, type: StringName = ZeeWeaponIds.DAMAGE_DART) -> DotWeaponBallistics:
	var b := DotWeaponBallistics.new()
	b.damage = damage
	b.damage_type = ZeeWeaponDamage.from(t if not t.is_empty() else ZeeWeaponDamage.table(), type)
	return b


## A shell that flies at [param speed] under [param gravity] and goes off on contact.
static func _explosive(t: Dictionary, direct: float, speed: float, gravity: float, radius: float, splash: float) -> DotWeaponBallistics:
	var b := _ballistics(t, direct, ZeeWeaponIds.DAMAGE_BLAST)
	b.splash_type = ZeeWeaponDamage.from(t if not t.is_empty() else ZeeWeaponDamage.table(), ZeeWeaponIds.DAMAGE_BLAST)
	b.speed = speed
	b.min_speed = speed
	b.min_charge_damage = 1.0
	b.gravity_scale = gravity
	b.radius = 0.15
	b.life_ticks = sec_ticks(6.0)
	b.splash_radius = radius
	b.splash_damage = splash
	b.splash_hurts_owner = true
	b.spread = 0.0
	b.spread_moving = 0.0
	b.spread_airborne = 0.0
	b.max_range = 300.0
	return b


static func _thrown(t: Dictionary, id: StringName, name: String, pool: StringName, tag: StringName) -> DotWeaponDef:
	var def := DotWeaponDef.new()
	def.authored_tick_rate = TICK_RATE
	def.id = id
	def.display_name = name
	def.behaviour_path = THROWN
	def.slot = ZeeWeaponIds.SLOT_THROWN
	def.fire_mode = DotWeaponDef.Fire.CHARGE
	def.use_interval_ticks = sec_ticks(1.0)
	def.tags = [ZeeWeaponIds.TAG_THROWN, tag]
	def.ammo_type = pool
	def.magazine = 0
	def.reserve = 1
	def.reserve_max = 1
	def.cost_per_use = 1
	def.auto_reload = false
	def.reload_ticks = 0
	# Held to throw further, up to a second.
	def.charge_ticks = sec_ticks(1.0)
	def.charge_requires_min = false
	def.deploy_ticks = sec_ticks(0.35)
	def.holster_ticks = sec_ticks(0.25)
	# [b]A fuse ten times the longest hold, and no game reads it.[/b] dot-weapon's thrown
	# behaviour treats a fuse used up by the cook as "it went off in the hand" and throws
	# nothing, so a fuse of zero (which is what a bottle has) is a molotov that never leaves
	# it. These go off when they land, which is the game's to decide from the tag.
	def.params = {
		&"fuse_ticks": sec_ticks(10.0),
		&"speed_scales_with_cook": true,
	}

	var b := _ballistics(t, 0.0, ZeeWeaponIds.DAMAGE_BLAST)
	b.radius = 0.12
	b.life_ticks = sec_ticks(12.0)
	b.max_range = 100.0
	b.speed = 18.0
	b.min_speed = 9.0
	b.gravity_scale = 1.0
	b.splash_hurts_owner = true
	def.tuning = b
	return def


# --- Art --------------------------------------------------------------------------
#
# [b]Kenney's Weapon Pack is modelled at real size and stands on its base[/b]: a pistol is
# 0.3 m long, the hunting rifle 1.04 m, every gun lies along Z with its origin at the middle
# of its bottom face. zee's blasters are toys about half again as big and centred, so the
# pose scale is zee's times [constant REAL_SCALE] and the model is lifted by half its height.

## How much larger than zee's blaster pose a real-sized gun is drawn.
const REAL_SCALE := 1.45

## Which way the Weapon Pack's barrels point: +Z, the opposite of zee's blasters (-Z).
## Settled by a side render in Blender with a marker on +Z (docs/history.md): the marker is
## on the muzzle of the pistol, uzi, shotgun, hunting rifle, machine gun and rocket launcher.
## The rack had said the same, but the rack cannot tell (zee's blasters passed it reversed
## for years), so the side render is the proof.
const GUN_FORWARD := Vector3.BACK


static func art() -> Array[ZeeWeaponArt]:
	return [
		_boxed(_fed(_gun_art(ZedWeaponIds.SERVICE_PISTOL, "pistol", ZeeWeaponArtTable.POSE_PISTOL, 0.23), MAG_BOX, Vector3(0.0, 0.03, -0.092))),
		_boxed(_fed(_gun_art(ZedWeaponIds.SILENCED_PISTOL, "pistolSilencer", ZeeWeaponArtTable.POSE_PISTOL, 0.23), MAG_BOX, Vector3(0.0, 0.03, -0.150))),
		_boxed(_fed(_gun_art(ZedWeaponIds.UZI, "uzi", ZeeWeaponArtTable.POSE_PISTOL, 0.333), MAG_BOX, Vector3(0.0, 0.03, -0.027))),
		_boxed(_fed(_gun_art(ZedWeaponIds.TACTICAL_SMG, "uziLongSilencer", ZeeWeaponArtTable.POSE_RIFLE, 0.333), MAG_BOX, Vector3(0.0, 0.03, -0.148))),
		_rounds(_hand_fed(_fed(_gun_art(ZedWeaponIds.PUMP_SHOTGUN, "shotgun", ZeeWeaponArtTable.POSE_RIFLE, 0.157), ROUND_SHELL, Vector3(0.0, 0.03, -0.03), true),
			Vector3(0.0, -0.10, 0.02), 1.6, Vector3.ZERO, &"RELOAD_KEYS_TUBE"), 3),
		_fed(_gun_art(ZedWeaponIds.SAWED_OFF, "shotgunShort", ZeeWeaponArtTable.POSE_RIFLE, 0.134), ROUND_SHELL, Vector3(0.0, 0.05, 0.0), true),
		_rounds(_hand_fed(_fed(_scoped(_gun_art(ZedWeaponIds.HUNTING_RIFLE, "sniperSand", ZeeWeaponArtTable.POSE_RIFLE, 0.283)), ROUND_RIFLE, Vector3(0.0, 0.10, -0.12), true),
			Vector3(0.03, 0.12, 0.0), 0.7, Vector3(90.0, 0.0, 0.0), &"RELOAD_KEYS_BOLT"), 2),
		_box_fed(_heavy(_gun_art(ZedWeaponIds.MACHINE_GUN, "machinegun", ZeeWeaponArtTable.POSE_HEAVY, 0.264), 1.9)),
		_hand_fed(_fed(_heavy(_gun_art(ZedWeaponIds.GRENADE_LAUNCHER, "machinegunLauncher", ZeeWeaponArtTable.POSE_HEAVY, 0.264), 1.6), ROUND_GRENADE, Vector3(0.0, 0.20, -0.10), true),
			Vector3(0.0, 0.14, -0.06), 2.2, Vector3.ZERO, &"RELOAD_KEYS_BREAK"),
		_hand_fed(_fed(_heavy(_gun_art(ZedWeaponIds.ROCKET_LAUNCHER, "rocketlauncherModern", ZeeWeaponArtTable.POSE_HEAVY, 0.337), 2.0), ROUND_ROCKET, Vector3(-0.046, 0.21, 0.30), true),
			Vector3(0.0, 0.0, 0.30), 2.0, Vector3(0.0, 180.0, 0.0), &"RELOAD_KEYS_MUZZLE"),
		_heavy(_gun_art(ZedWeaponIds.FLAMETHROWER, "flamethrower_long", ZeeWeaponArtTable.POSE_HEAVY, 0.207), 1.7),
		_thrown_art(ZedWeaponIds.MOLOTOV, FOOD_DIR + "wine-red.scn", 0.7),
		_thrown_art(ZedWeaponIds.PIPE_BOMB, WEAPONS_DIR + "grenadeVintage.glb", 0.9),
		_thrown_art(ZedWeaponIds.BILE_JAR, FOOD_DIR + "honey.scn", 0.6),
	]


## A gun: lies along +Z, stands on its base, [param height] metres tall (measured).
##
## [b]On zee's hold[/b]: zee's pose offset and its cant and turn
## ([method ZeeWeaponArtTable.pose_rotation]), zee's aim place, and (by leaving
## [member ZeeWeaponArt.reload_keys] empty) the pose's reload keys. zee's rotations are written
## for a model pointing -Z; these point +Z, and the 180-degree turn that [method
## ZeeWeaponArt.orientation] puts in front of them flips the sign of a pitch and a roll (a
## yaw is about the axis of the turn and keeps its sign), so they are handed over as
## [method hold_rotation]. Written straight across, the cant tipped the left side up and
## showed the camera the gun's underside.
static func _gun_art(id: StringName, model: String, pose: StringName, height: float) -> ZeeWeaponArt:
	var art := ZeeWeaponArt.make(id, WEAPONS_DIR + model + ".glb")
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
	# Lifted by half its height, so the middle of the gun is where zee's centred blasters'
	# is: along the model's own up through the hold's basis (which carries the scale and the
	# cant), since once the hold is canted the camera's down is no longer the gun's. The aim
	# place needs it too, or the gun at the sight sits half its height too high.
	var lift := Vector3(0.0, -height * 0.5, 0.0)
	art.view_offset += art.view_transform().basis * lift
	art.aim_offset += art.aim_transform().basis * lift
	art.world_offset = Vector3(0.0, -height * 0.5 * art.world_scale, 0.0)
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
## space (+Z forward, standing on its base), where zee's support hand takes it.
##
## [b]Without one, zee's reload is the gun rolling and nothing else[/b]: the support hand stays
## on the fore-end (zee sends it to the magazine well only when there is a magazine) and nothing
## leaves or enters the gun. The play test called that "no proper reload animations". A
## [param loose] round is drawn only while it is carried in (`ZeeWeaponArt.magazine_loose`, set
## by name so an older zee without it still loads the pack).
static func _fed(art: ZeeWeaponArt, path: String, offset: Vector3, loose: bool = false) -> ZeeWeaponArt:
	var _with := art.with_magazine(path, offset)
	if loose:
		art.set(&"magazine_loose", true)
	return art


## A machine gun fed from a box: zee's ammunition box and belt, built in code (`magazine_part`),
## on the gun's right side (-X: the model points +Z, so its right is zee's left), dropped and
## swapped on a reload. Set by name, so an older zee without the fields still loads the pack.
##
## [b]A box, not a loose round.[/b] The belt round this gun carried in before was 9 cm, drawn at
## the hold's scale inside a fist: the reload read as the gun tilting.
static func _box_fed(art: ZeeWeaponArt) -> ZeeWeaponArt:
	art.set(&"magazine_part", &"ammo_box")
	art.magazine_offset = Vector3(-0.09, 0.02, -0.02)
	art.set(&"magazine_scale", 1.4)
	return art


## A launcher fed a round by hand in sight (zee's `ZeeWeaponArt.load_from`): the push starts at
## [param from] off the seat (model space), the round drawn at [param scale] and turned by
## [param rotation] (the rocket's nose to the muzzle), with zee's [param keys] by name
## (`ZeeWeaponPose.RELOAD_KEYS_BREAK`, `_MUZZLE`). An older zee without them keeps its old reload.
static func _hand_fed(art: ZeeWeaponArt, from: Vector3, scale: float, rotation: Vector3, keys: StringName) -> ZeeWeaponArt:
	art.set(&"load_from", from)
	art.set(&"magazine_scale", scale)
	art.magazine_rotation = rotation
	var pose: Script = ZeeWeaponPose
	var table: Variant = pose.get_script_constant_map().get(keys)
	if table is Array:
		art.reload_keys = table
	return art


## A stick magazine for the pistols and the uzis: zee's `box_magazine`, built in code, drawn half
## again as big, its foot below the grip's.
##
## [b]Not the Weapon Pack's `ammo_uzi`[/b], which is a 6.5 cm cartridge: inside the grip and the
## glove it was nothing on screen, and the reload sheet showed the gun lifting with nothing
## leaving it or going in. An older zee without the part keeps the cartridge.
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


## How many rounds a hand-fed gun takes, one push each (zee's `ZeeWeaponArt.load_count`, by name).
##
## [b]The pump gun and the hunting rifle are fed like zee's pump guns and bolt gun[/b]
## (`RELOAD_KEYS_TUBE`, `_BOLT`): carried once from below the screen, the one round showed in one
## frame of the reload sheet, and the rifle, long and lifted half out of frame, read as a tilt.
static func _rounds(art: ZeeWeaponArt, count: int) -> ZeeWeaponArt:
	art.set(&"load_count", count)
	return art


static func _heavy(art: ZeeWeaponArt, weight: float) -> ZeeWeaponArt:
	art.weight = weight
	return art


## A throwable: stands upright on its base, as zee's grenades do.
##
## [b]Held upright, not pointed away.[/b] zee turns its grenades' +Y onto the view's forward,
## which for a round grenade is invisible; a bottle turned that way is drawn as its own
## base, a dark hexagon behind the hand, and tilting the view rotation did not save it. So
## the model is said to face forward already (its +Y stays up) and it is held standing.
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


## Every art entry's models exist. Loads nothing; asks the resource loader.
static func validate_models() -> DotResult:
	var missing := PackedStringArray()

	for entry in art():
		if not ResourceLoader.exists(entry.model_path):
			missing.append("%s: %s" % [entry.id, entry.model_path])

	if missing.is_empty():
		return DotResult.success(null)

	return DotResult.fail(DotError.CODE_IO, "%d model(s) are missing: %s" % [missing.size(), ", ".join(missing)])


static func describe_lines(types: Dictionary = {}) -> PackedStringArray:
	var out := PackedStringArray()
	var built := weapons(types)
	out.append("zed-dot-weapons: %d weapons at %d Hz, %s" % [built.size(), TICK_RATE, "installed" if installed() else "not installed"])

	for def in built:
		out.append("  %-18s %-18s slot %d  %s" % [def.id, def.display_name, def.slot, ", ".join(def.tags)])

	return out
