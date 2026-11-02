extends Node

## Counters, check printing and builders shared by the zed-dot-weapons suite.

var _sections_entered: int = 0
var _sections_finished: int = 0
var _checks: int = 0
var _failures: int = 0


func _rig_catalogue_has(id: StringName) -> bool:
	var rig := ZeeWeaponRig.new()
	rig.role = ZeeWeaponRig.Role.SERVER
	rig.authority = true
	add_child(rig)
	var ok := rig.setup().ok and rig.arsenal.catalogue.has(id)
	remove_child(rig)
	rig.free()
	return ok


func _arsenal() -> DotWeaponArsenal:
	var arsenal := DotWeaponArsenal.new()
	arsenal.catalogue = ZeeWeaponPack.catalogue()
	arsenal.tick_rate = ZedWeaponPack.TICK_RATE
	arsenal.authority = true
	add_child(arsenal)
	var _ready_now := arsenal.setup()
	return arsenal


## Ticks [param from] to [param to] with [param buttons] held, until [param release_at] when
## given. The outcomes that used something.
func _run(arsenal: DotWeaponArsenal, from: int, to: int, buttons: int, release_at: int = -1) -> Array:
	var out: Array = []
	var previous: DotWeaponCommand = null

	for tick in range(from, to):
		var command := DotWeaponCommand.new()
		command.buttons = buttons if release_at < 0 or tick < release_at else 0
		var ctx := DotWeaponContext.make(1, tick, Vector3(0.0, 1.6, 0.0), Vector3.FORWARD)
		ctx.authority = true
		var o := arsenal.simulate_tick(command, ctx, previous)

		if o.used:
			out.append(o)

		previous = command

	return out


func _profile_file(root: String, rel: String, text: String) -> void:
	var path := root.path_join("addons/zed_weapons/weapon").path_join(rel)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(path.get_base_dir()))
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()


func _by_id(defs: Array[DotWeaponDef]) -> Dictionary:
	var out := {}
	for d in defs:
		out[String(d.id)] = d
	return out


func _begin(name: String) -> void:
	_sections_entered += 1
	print("")
	print("-- %s" % name)


func _end() -> void:
	_sections_finished += 1


func _check(label: String, passed: bool) -> void:
	_checks += 1

	if passed:
		print("   ok    %s" % label)
	else:
		_failures += 1
		print("   FAIL  %s" % label)
