class_name ZedDefExport
extends RefCounted

## Writes the pack's weapons as Workshop files: one [DotWeaponDef] `.tres` per weapon and the
## `provides.json` that lists them. The same form as zee-dot-weapons' [ZeeDefExport], whose
## category table and document builder this reuses so the two packs cannot describe a slot
## differently.
##
## [b]The code table stays the source of truth.[/b] The files are generated from
## [method ZedWeaponPack.weapons], never hand-edited; the suite loads each back and compares
## it with the code row. Run it with `tools/export-defs.sh`.

const TITLE := "Zed Weapons"


static func own_weapons() -> Array[DotWeaponDef]:
	return ZedWeaponPack.weapons(ZeeWeaponDamage.table())


## The `provides.json` document for [param defs].
static func provides(defs: Array[DotWeaponDef]) -> Dictionary:
	var doc := ZeeDefExport.provides(defs)
	doc["title"] = TITLE
	return doc


## Writes everything under [param root]. The value of the result is the number of definitions.
static func export_to(root: String) -> DotResult:
	var dir := root.path_join("weapons")
	var made := DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(dir))
	if made != OK:
		return DotResult.fail(DotError.CODE_IO, "Cannot create %s (error %d)." % [dir, made])

	var defs := own_weapons()

	for def in defs:
		var path := dir.path_join("%s.tres" % String(def.id))
		var saved := ResourceSaver.save(def, path)
		if saved != OK:
			return DotResult.fail(DotError.CODE_IO, "Cannot save %s (error %d)." % [path, saved])

	var json_path := root.path_join("provides.json")
	var f := FileAccess.open(json_path, FileAccess.WRITE)
	if f == null:
		return DotResult.fail(DotError.CODE_IO, "Cannot write %s." % json_path)

	f.store_string(JSON.stringify(provides(defs), "\t", false) + "\n")
	f.close()
	return DotResult.success(defs.size())
