class_name ZedWeaponIds
extends RefCounted

## Every id, tag and ammunition pool in this pack.
##
## [b]Named by role, never by model[/b], as zee-dot-weapons' are, and for its reason: the
## model file is Kenney's export name, and a game that swapped the art would find every rule
## pointing at the wrong file. [ZedWeaponPack] is the only file that names a model.
##
## [b]No id here may be one zee-dot-weapons has.[/b] zee's own ids win a clash (see
## `ZeeWeaponPack.add_source`), so a `pistol` here would silently never exist. That is why
## these read `service_pistol` and `pump_shotgun`; the suite checks there is no overlap.

# --- Tags a game reads ---------------------------------------------------------
#
# What a throwable DOES when it lands is the game's: this pack spawns a projectile and says
# what kind of thing it is. game-zombie-zone turns a `molotov` into a fire, a `pipe_bomb` into
# a beeping lure that goes off, and a `bile` into a jar the horde comes to.

const TAG_MOLOTOV := &"molotov"
const TAG_PIPE_BOMB := &"pipe_bomb"
const TAG_BILE := &"bile"
## Sets what it hits alight, where the game has fire.
const TAG_INCENDIARY := &"incendiary"

# --- Ammunition pools ------------------------------------------------------------
#
# The guns share zee's pools (light, heavy, shells, belt, ordnance), so a pile of ammo in a
# game tops up both packs' guns. Fuel and the three throwables are pools of their own: a
# molotov and a frag grenade are not the same thing to carry.

const AMMO_FUEL := &"fuel"
const AMMO_MOLOTOV := &"molotovs"
const AMMO_PIPE_BOMB := &"pipe_bombs"
const AMMO_BILE := &"bile_jars"

# --- Sidearms ------------------------------------------------------------------
const SERVICE_PISTOL := &"service_pistol"
const SILENCED_PISTOL := &"silenced_pistol"
const UZI := &"uzi"

# --- Primaries -----------------------------------------------------------------
const TACTICAL_SMG := &"tactical_smg"
const PUMP_SHOTGUN := &"pump_shotgun"
const SAWED_OFF := &"sawed_off"
const HUNTING_RIFLE := &"hunting_rifle"
## The high-detail rifle (assets/hq/): baked textures, and mounts for every attachment below.
const ASSAULT_CARBINE := &"assault_carbine"

# --- Heavies -------------------------------------------------------------------
const MACHINE_GUN := &"machine_gun"
const GRENADE_LAUNCHER := &"grenade_launcher"
const ROCKET_LAUNCHER := &"rocket_launcher"
const FLAMETHROWER := &"flamethrower"

# --- Thrown --------------------------------------------------------------------
const MOLOTOV := &"molotov"
const PIPE_BOMB := &"pipe_bomb"
const BILE_JAR := &"bile_jar"


## Every id, in catalogue order. Kept beside the constants for zee's reason: a const cannot
## be enumerated, and the suite asserts this list, the catalogue and the art agree.
static func all() -> Array[StringName]:
	return [
		SERVICE_PISTOL, SILENCED_PISTOL, UZI,
		TACTICAL_SMG, PUMP_SHOTGUN, SAWED_OFF, HUNTING_RIFLE, ASSAULT_CARBINE,
		MACHINE_GUN, GRENADE_LAUNCHER, ROCKET_LAUNCHER, FLAMETHROWER,
		MOLOTOV, PIPE_BOMB, BILE_JAR,
	]


# --- Attachments -----------------------------------------------------------------
#
# dot-weapon's attachment ids ([DotWeaponAttachment]), each on one of its mounts. Named by
# what they do, like the weapons.

const RED_DOT := &"red_dot"
const SCOPE_4X := &"scope_4x"
const SUPPRESSOR := &"suppressor"
const FOREGRIP := &"foregrip"
const LASER_SIGHT := &"laser_sight"
const EXTENDED_MAG := &"extended_mag"


static func all_attachments() -> Array[StringName]:
	return [RED_DOT, SCOPE_4X, SUPPRESSOR, FOREGRIP, LASER_SIGHT, EXTENDED_MAG]
