class_name ZedWeaponPack
extends "zed_weapon_pack_art.gd"

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
	ZeeAttachmentArt.add_source(SOURCE, Callable(ZedWeaponPack, &"attachment_art"))

	for id: StringName in SOUNDS:
		ZeeWeaponSound.set_class(id, SOUNDS[id])


## Takes this pack out again: a game unloading in a shell that loads the next.
static func uninstall() -> void:
	ZeeWeaponPack.remove_source(SOURCE)
	ZeeWeaponArtTable.remove_source(SOURCE)
	ZeeAttachmentArt.remove_source(SOURCE)


static func installed() -> bool:
	return ZeeWeaponPack.source_names().has(String(SOURCE))


## Which of zee's baked reports each weapon sounds like.
const SOUNDS := {
	ZedWeaponIds.SERVICE_PISTOL: &"light",
	ZedWeaponIds.SILENCED_PISTOL: ZeeWeaponSound.SUPPRESSED,
	ZedWeaponIds.UZI: &"smg",
	ZedWeaponIds.TACTICAL_SMG: ZeeWeaponSound.SUPPRESSED,
	ZedWeaponIds.PUMP_SHOTGUN: &"shotgun",
	ZedWeaponIds.SAWED_OFF: &"shotgun",
	ZedWeaponIds.HUNTING_RIFLE: &"sniper",
	ZedWeaponIds.ASSAULT_CARBINE: &"rifle",
	ZedWeaponIds.AK_RIFLE: &"rifle",
	ZedWeaponIds.MACHINE_GUN: &"heavy",
	ZedWeaponIds.GRENADE_LAUNCHER: &"launcher",
	ZedWeaponIds.ROCKET_LAUNCHER: &"launcher",
	ZedWeaponIds.FLAMETHROWER: &"minigun",
}


# --- The documents ---------------------------------------------------------------

## [param profiled] false skips the cfg profiles (the Workshop export writes the builders' own numbers).
static func weapons(types: Dictionary = {}, profiled: bool = true) -> Array[DotWeaponDef]:
	var t := types if not types.is_empty() else ZeeWeaponDamage.table()

	var out: Array[DotWeaponDef] = [
		service_pistol(t), silenced_pistol(t), uzi(t),
		tactical_smg(t), pump_shotgun(t), sawed_off(t), hunting_rifle(t), assault_carbine(t), ak_rifle(t),
		machine_gun(t), grenade_launcher(t), rocket_launcher(t), flamethrower(t),
		molotov(t), pipe_bomb(t), bile_jar(t),
	]

	for def in out:
		def.weight = float(WEIGHTS.get(def.id, def.weight))

	if profiled:
		errors = DotWeaponProfiles.tune(out, profile_set())

	return out


## Carry weight in kg per weapon; a profile's `weight` key overrides it.
const WEIGHTS := {
	&"service_pistol": 1.0, &"silenced_pistol": 1.0, &"uzi": 1.0, &"tactical_smg": 2.8, &"sawed_off": 4.0,
	&"hunting_rifle": 5.0, &"assault_carbine": 4.0, &"machine_gun": 6.0, &"grenade_launcher": 6.0,
	&"rocket_launcher": 6.0, &"flamethrower": 6.0, &"molotov": 0.4, &"pipe_bomb": 0.4, &"bile_jar": 0.4,
}
## The config addon name profiles are read under (`cfg/addons/zed_weapons/weapon`); see [DotWeaponProfiles].
const ADDON := "zed_weapons"
## The game id for the game tier (`cfg/game/<game>/weapon`); empty skips it.
static var game: String = ""
## A mounted pack's `cfg` root (`DotCloudMounter.cfg_root_of`), the weakest root.
static var pack_cfg_root: String = ""
## Roots under [member pack_cfg_root]; empty means [method DotProfileSet.default_roots]. Tests set it.
static var base_roots: PackedStringArray = PackedStringArray()
## Profiles that failed to load in the last [method weapons]; their weapons keep the builder's numbers.
static var errors: PackedStringArray = PackedStringArray()


## The weapon profile set; call [method DotProfileSet.clear_cache] when done.
static func profile_set(layer: Variant = null) -> DotProfileSet:
	return DotWeaponProfiles.overlay_set(ADDON, game, pack_cfg_root, base_roots, layer)


## Weapon [param id] with the upgrades [param ids] applied; value `{def, cost}`.
static func upgraded(id: StringName, ids: Array, types: Dictionary = {}) -> DotResult:
	var def: DotWeaponDef = table(types).get(id)
	if def == null:
		return DotResult.fail(DotError.CODE_INVALID, "no weapon %s" % id)
	var set := profile_set()
	var res := DotWeaponProfiles.upgraded(def, ids, set)
	set.clear_cache()
	return res


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


## The high-detail one: a 30-round carbine with a mount for every attachment
## ([method attachments]). Its model is baked (assets/hq/, art-src/hq/), not kitbashed.
static func assault_carbine(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.ASSAULT_CARBINE, "Assault Carbine", ZeeWeaponIds.SLOT_PRIMARY,
		DotWeaponDef.Fire.AUTO, rpm_ticks(750.0))
	def.tags = [ZeeWeaponIds.TAG_PRIMARY, ZeeWeaponIds.TAG_AUTOMATIC]
	def.ammo_type = ZeeWeaponIds.AMMO_HEAVY
	def.magazine = 30
	def.reserve = 120
	def.reserve_max = 240
	def.reload_ticks = sec_ticks(2.4)
	def.deploy_ticks = sec_ticks(0.4)
	def.holster_ticks = sec_ticks(0.25)
	def.mounts = [
		DotWeaponAttachment.MOUNT_OPTIC, DotWeaponAttachment.MOUNT_MUZZLE,
		DotWeaponAttachment.MOUNT_UNDERBARREL, DotWeaponAttachment.MOUNT_SIDE,
		DotWeaponAttachment.MOUNT_MAGAZINE,
	]

	var b := _ballistics(t, 26.0)
	b.spread = 0.7
	b.spread_moving = 2.0
	b.bloom = 0.14
	b.bloom_max = 2.8
	b.recoil_pitch = 0.45
	b.recoil_yaw = 0.2
	b.max_range = 180.0
	def.tuning = b
	return def


## The second high-detail rifle: a 30-round 7.62 mm with wood furniture, hitting harder and
## kicking more than the carbine, and slower. Same five mounts.
static func ak_rifle(t: Dictionary = {}) -> DotWeaponDef:
	var def := _gun(ZedWeaponIds.AK_RIFLE, "AK Rifle", ZeeWeaponIds.SLOT_PRIMARY,
		DotWeaponDef.Fire.AUTO, rpm_ticks(600.0))
	def.tags = [ZeeWeaponIds.TAG_PRIMARY, ZeeWeaponIds.TAG_AUTOMATIC]
	def.ammo_type = ZeeWeaponIds.AMMO_HEAVY
	def.magazine = 30
	def.reserve = 120
	def.reserve_max = 240
	def.reload_ticks = sec_ticks(2.6)
	def.deploy_ticks = sec_ticks(0.45)
	def.holster_ticks = sec_ticks(0.3)
	def.mounts = [
		DotWeaponAttachment.MOUNT_OPTIC, DotWeaponAttachment.MOUNT_MUZZLE,
		DotWeaponAttachment.MOUNT_UNDERBARREL, DotWeaponAttachment.MOUNT_SIDE,
		DotWeaponAttachment.MOUNT_MAGAZINE,
	]

	var b := _ballistics(t, 32.0)
	b.spread = 0.9
	b.spread_moving = 2.4
	b.bloom = 0.2
	b.bloom_max = 3.4
	b.recoil_pitch = 0.62
	b.recoil_yaw = 0.3
	b.max_range = 170.0
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


## Guns that really have a selector, the first entry being how they start.
const SELECTABLE := {
	ZedWeaponIds.UZI: ["auto", "semi"], ZedWeaponIds.TACTICAL_SMG: ["auto", "semi", "burst"],
	ZedWeaponIds.ASSAULT_CARBINE: ["auto", "semi", "burst"], ZedWeaponIds.AK_RIFLE: ["auto", "semi"],
}


# --- Builders ------------------------------------------------------------------------

static func _gun(id: StringName, name: String, slot: int, fire: DotWeaponDef.Fire, interval: int) -> DotWeaponDef:
	var def := DotWeaponDef.new()
	def.authored_tick_rate = TICK_RATE
	def.id = id
	def.display_name = name
	def.behaviour_path = HITSCAN
	def.slot = slot
	def.fire_mode = fire
	if SELECTABLE.has(id):
		def.fire_modes = PackedStringArray(SELECTABLE[id])
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


# Attachments: the rules are dot-weapon's ([DotWeaponAttachments]); each multiplier names a field of the document or its tuning, so a typo fails `apply` instead of shipping a suppressor that is not quiet.



## The art entries; here, not in the base, because a Callable on this class cannot find a static function it inherits.
static func art() -> Array[ZeeWeaponArt]:
	return art_entries()


static func attachment_defs() -> Array[DotWeaponAttachment]:
	return [
		_attachment(ZedWeaponIds.RED_DOT, "Red Dot", DotWeaponAttachment.MOUNT_OPTIC,
			{}, {}, [], {&"aim_zoom": 0.8}),
		_attachment(ZedWeaponIds.SCOPE_4X, "4x Scope", DotWeaponAttachment.MOUNT_OPTIC,
			{"spread": 0.85}, {}, [ZeeWeaponIds.TAG_SCOPED], {&"aim_zoom": 0.4}),
		_attachment(ZedWeaponIds.SUPPRESSOR, "Suppressor", DotWeaponAttachment.MOUNT_MUZZLE,
			{"recoil_pitch": 0.9, "max_range": 0.9}, {}, [ZeeWeaponIds.TAG_SILENCED]),
		_attachment(ZedWeaponIds.FOREGRIP, "Foregrip", DotWeaponAttachment.MOUNT_UNDERBARREL,
			{"recoil_pitch": 0.8, "spread_moving": 0.9}),
		_attachment(ZedWeaponIds.LASER_SIGHT, "Laser Sight", DotWeaponAttachment.MOUNT_SIDE,
			{"spread": 0.8}),
		_attachment(ZedWeaponIds.EXTENDED_MAG, "Extended Magazine", DotWeaponAttachment.MOUNT_MAGAZINE,
			{"reload_ticks": 1.1}, {"magazine": 10}),
	]


## The six in one catalogue, ready for an arsenal's `attachments`.
static func attachments() -> DotWeaponAttachments:
	var out := DotWeaponAttachments.new()
	for att in attachment_defs():
		var _added := out.add(att)
	return out


## How each attachment is drawn ([ZeeAttachmentArt]): the model that goes on the gun's `socket_<mount>` with no offset (art-src/hq/hq_attachments.py), and the nodes it replaces.
const ATTACHMENT_ART := {
	ZedWeaponIds.RED_DOT: {"path": HQ_DIR + "red_dot.glb", "hides": [&"rear_sight"], "aim": &"glass"},
	ZedWeaponIds.SCOPE_4X: {"path": HQ_DIR + "scope_4x.glb", "hides": [&"rear_sight"], "aim": &"scoped", "zoom": 0.4},
	ZedWeaponIds.SUPPRESSOR: {"path": HQ_DIR + "suppressor.glb", "hides": []},
	ZedWeaponIds.FOREGRIP: {"path": HQ_DIR + "foregrip.glb", "hides": []},
	ZedWeaponIds.LASER_SIGHT: {"path": HQ_DIR + "laser.glb", "hides": []},
	ZedWeaponIds.EXTENDED_MAG: {"path": HQ_DIR + "ext_mag.glb", "hides": [&"magazine"]},
}


## The node an attachment on [param mount] is parented to, in the gun's model.
static func socket_name(mount: StringName) -> StringName:
	return ZeeAttachmentArt.socket_name(mount)


## Zee's hook ([ZeeAttachmentArt]): how [param id] is drawn, or empty.
static func attachment_art(id: StringName) -> Dictionary:
	return ATTACHMENT_ART.get(id, {})


static func _attachment(id: StringName, name: String, mount: StringName, scale: Dictionary = {},
		add: Dictionary = {}, tags: Array[StringName] = [], params: Dictionary = {}) -> DotWeaponAttachment:
	var att := DotWeaponAttachment.new()
	att.id = id
	att.display_name = name
	att.mount = mount
	att.scale = scale
	att.add = add
	att.tags_added = tags
	att.params_set = params
	return att


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
