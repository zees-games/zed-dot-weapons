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

## Which way the Weapon Pack's barrels point: +Z, the same as zee's blasters. Found by the
## rack render, as zee's was, and the first guess (-Z) was wrong: the shotguns' wooden
## stocks and the hunting rifle's scope end sat at the red muzzle pips, and the rifle's
## barrel and the rocket's warhead at the other end.
const GUN_FORWARD := Vector3.BACK


static func art() -> Array[ZeeWeaponArt]:
	return [
		_gun_art(ZedWeaponIds.SERVICE_PISTOL, "pistol", ZeeWeaponArtTable.POSE_PISTOL, 0.23),
		_gun_art(ZedWeaponIds.SILENCED_PISTOL, "pistolSilencer", ZeeWeaponArtTable.POSE_PISTOL, 0.23),
		_gun_art(ZedWeaponIds.UZI, "uzi", ZeeWeaponArtTable.POSE_PISTOL, 0.333),
		_gun_art(ZedWeaponIds.TACTICAL_SMG, "uziLongSilencer", ZeeWeaponArtTable.POSE_RIFLE, 0.333),
		_gun_art(ZedWeaponIds.PUMP_SHOTGUN, "shotgun", ZeeWeaponArtTable.POSE_RIFLE, 0.157),
		_gun_art(ZedWeaponIds.SAWED_OFF, "shotgunShort", ZeeWeaponArtTable.POSE_RIFLE, 0.134),
		_scoped(_gun_art(ZedWeaponIds.HUNTING_RIFLE, "sniperSand", ZeeWeaponArtTable.POSE_RIFLE, 0.283)),
		_heavy(_gun_art(ZedWeaponIds.MACHINE_GUN, "machinegun", ZeeWeaponArtTable.POSE_HEAVY, 0.264), 1.9),
		_heavy(_gun_art(ZedWeaponIds.GRENADE_LAUNCHER, "machinegunLauncher", ZeeWeaponArtTable.POSE_HEAVY, 0.264), 1.6),
		_heavy(_gun_art(ZedWeaponIds.ROCKET_LAUNCHER, "rocketlauncherModern", ZeeWeaponArtTable.POSE_HEAVY, 0.337), 2.0),
		_heavy(_gun_art(ZedWeaponIds.FLAMETHROWER, "flamethrower_long", ZeeWeaponArtTable.POSE_HEAVY, 0.207), 1.7),
		_thrown_art(ZedWeaponIds.MOLOTOV, FOOD_DIR + "wine-red.scn", 0.45),
		_thrown_art(ZedWeaponIds.PIPE_BOMB, WEAPONS_DIR + "grenadeVintage.glb", 0.9),
		_thrown_art(ZedWeaponIds.BILE_JAR, FOOD_DIR + "honey.scn", 0.6),
	]


## A gun: lies along Z, stands on its base, [param height] metres tall (measured).
static func _gun_art(id: StringName, model: String, pose: StringName, height: float) -> ZeeWeaponArt:
	var art := ZeeWeaponArt.make(id, WEAPONS_DIR + model + ".glb")
	art.model_forward = GUN_FORWARD
	art.pose = pose
	art.view_scale = ZeeWeaponArtTable.pose_scale(pose) * REAL_SCALE
	art.world_scale = REAL_SCALE
	art.weight = ZeeWeaponArtTable.pose_weight(pose)
	# Lifted by half its height in both views, so the grip is where zee's centred blasters'
	# is, and scaled with the model (zee's third trap).
	art.view_offset = ZeeWeaponArtTable.pose_offset(pose) + Vector3(0.0, -height * 0.5 * art.view_scale, 0.0)
	art.world_offset = Vector3(0.0, -height * 0.5 * art.world_scale, 0.0)
	art.view_rotation = Vector3(-2.0, -4.0, 0.0)
	return art


static func _scoped(art: ZeeWeaponArt) -> ZeeWeaponArt:
	art.aim_scoped = true
	art.aim_zoom = 0.4
	art.aim_time = 0.2
	art.weight = 1.5
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
