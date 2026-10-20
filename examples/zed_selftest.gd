extends Node

## zed-dot-weapons' suite: the pack installs into zee-dot-weapons, every weapon validates,
## has art that loads and a report of its own, and does what it is for when fired.
##
## [codeblock]
## godot --headless --path . res://examples/zed_selftest.tscn
## [/codeblock]
##
## [b]What it cannot see is how a weapon looks in the hand[/b], and two of this pack's first
## three bugs were exactly that (every gun pointing backwards, a bottle drawn as its own
## base). `tools/screenshot.sh --rack` and `tools/screenshot.sh <id>` are the other half.

# No CHANNEL: a suite's verdict is its output.

## Every check this suite makes; a script error aborts a section part-way, and only the
## total can see the checks that never ran.
const CHECKS := 51

const ZEE_COUNT := 27

var _sections_entered: int = 0
var _sections_finished: int = 0
var _checks: int = 0
var _failures: int = 0


func _ready() -> void:
	print("zed-dot-weapons self-test")
	print("=========================")

	_ids()
	_install()
	_documents()
	_workshop()
	_art()
	_sights()
	_firing()
	_throwing()
	_attachments()
	_uninstall()
	_exiting()

	print("")
	print("%d sections entered, %d finished, %d checks, %d failed" % [
		_sections_entered, _sections_finished, _checks, _failures
	])

	if _checks != CHECKS:
		print("!! %d checks ran, %d expected. A section aborted part-way." % [_checks, CHECKS])

	var passed := _failures == 0 and _sections_entered == _sections_finished and _checks == CHECKS
	print("RESULT: %s" % ("PASS" if passed else "FAIL"))
	get_tree().quit(0 if passed else 1)


func _ids() -> void:
	_begin("ids")
	var all := ZedWeaponIds.all()
	_check("sixteen weapons are named", all.size() == 16)

	var clash: Array[String] = []

	for id in all:
		if ZeeWeaponIds.all().has(id):
			clash.append(String(id))

	# zee's ids win a clash, so an id here that zee has would silently never exist.
	_check("none of them is an id zee-dot-weapons has: %s" % ", ".join(clash), clash.is_empty())
	_end()


func _install() -> void:
	_begin("installing into zee-dot-weapons")
	ZedWeaponPack.install()
	ZedWeaponPack.install()
	var table := ZeeWeaponPack.table()
	var missing: Array[String] = []

	for id in ZedWeaponIds.all():
		if not table.has(id):
			missing.append(String(id))

	_check("every weapon is in zee's catalogue: missing %s" % ", ".join(missing), missing.is_empty())
	_check("beside all of zee's, once each, installed twice", table.size() == ZEE_COUNT + ZedWeaponIds.all().size())
	_check("zee's catalogue validates with them in it", ZeeWeaponPack.catalogue().validate().ok)
	_check("and a rig's default catalogue carries them", _rig_catalogue_has(ZedWeaponIds.HUNTING_RIFLE))
	_end()


func _documents() -> void:
	_begin("the documents")
	var tiers := 0
	var slots_ok := true

	for def in ZedWeaponPack.weapons():
		for tier in [ZeeWeaponIds.TAG_SIDEARM, ZeeWeaponIds.TAG_PRIMARY, ZeeWeaponIds.TAG_HEAVY, ZeeWeaponIds.TAG_THROWN]:
			if def.tags.has(tier):
				tiers += 1
				break

		var wanted := {ZeeWeaponIds.TAG_SIDEARM: ZeeWeaponIds.SLOT_SIDEARM, ZeeWeaponIds.TAG_THROWN: ZeeWeaponIds.SLOT_THROWN}
		for tag: StringName in wanted:
			if def.tags.has(tag) and def.slot != int(wanted[tag]):
				slots_ok = false

	# A game sorts weapons by tier tag (game-zombie-zone's ZzWeapons does), so a weapon with
	# none is a weapon no box or map can ever hand out.
	_check("every weapon has a tier tag", tiers == ZedWeaponIds.all().size())
	_check("and sits in the slot its tier says", slots_ok)

	var t := ZedWeaponPack.table()
	_check("the molotov says it is one", (t[ZedWeaponIds.MOLOTOV] as DotWeaponDef).tags.has(ZedWeaponIds.TAG_MOLOTOV))
	_check("the pipe bomb, the bile jar and the flamethrower too",
		(t[ZedWeaponIds.PIPE_BOMB] as DotWeaponDef).tags.has(ZedWeaponIds.TAG_PIPE_BOMB)
		and (t[ZedWeaponIds.BILE_JAR] as DotWeaponDef).tags.has(ZedWeaponIds.TAG_BILE)
		and (t[ZedWeaponIds.FLAMETHROWER] as DotWeaponDef).tags.has(ZedWeaponIds.TAG_INCENDIARY))

	var classes := 0
	for id in ZedWeaponPack.SOUNDS:
		if ZeeWeaponSound.class_for(id, DotWeaponOutcome.KIND_SHOT) == ZedWeaponPack.SOUNDS[id] and ZeeWeaponSound.RECIPES.has(ZedWeaponPack.SOUNDS[id]):
			classes += 1
	_check("every gun sounds like a class zee can bake", classes == ZedWeaponPack.SOUNDS.size())

	# Written in 64 Hz ticks like zee's, and saying so: dot-weapon scales a row to the
	# arsenal's rate only when the row names its own, so an unstamped row fires twice as
	# fast on a 128 Hz server.
	var stamped := 0
	for def in ZedWeaponPack.weapons():
		if def.authored_tick_rate == ZedWeaponPack.TICK_RATE:
			stamped += 1
	_check("every row says it was written at %d Hz" % ZedWeaponPack.TICK_RATE, stamped == ZedWeaponIds.all().size())
	_end()


func _workshop() -> void:
	_begin("the Workshop files agree with the code table")

	var doc: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://provides.json"))
	_check("provides.json parses to a dictionary", doc is Dictionary)
	if not (doc is Dictionary):
		_end()
		return

	var provides := doc as Dictionary
	var code := ZedDefExport.own_weapons()
	var entries: Array = provides.get("entries", [])
	_check("schema 1, kind weapon", int(provides.get("schema", 0)) == 1 and provides.get("kinds", []) == ["weapon"])
	_check("one entry per code weapon", entries.size() == code.size() and code.size() == ZedWeaponIds.all().size())
	_check("provides.json is what the exporter writes now (run tools/export-defs.sh)",
		JSON.stringify(provides) == JSON.stringify(JSON.parse_string(JSON.stringify(ZedDefExport.provides(code)))))

	var by_id := {}
	for def in code:
		by_id[def.id] = def

	var bad: Array[String] = []
	var clash: Array[String] = []
	for e: Dictionary in entries:
		var id := StringName(e["id"])
		var def: DotWeaponDef = by_id.get(id, null)
		var loaded := load("res://" + String(e["def"])) as DotWeaponDef
		if def == null or loaded == null or loaded.id != id or loaded.slot != def.slot \
				or e.get("category", "") != ZeeDefExport.category_for(def.slot) \
				or not (e.get("meta", {}) as Dictionary).has("asset_root"):
			bad.append(String(id))
		if ZeeWeaponIds.all().has(id):
			clash.append(String(id))

	_check("every provided id is a ZedWeaponPack weapon whose file loads: %s" % ", ".join(bad), bad.is_empty())
	_check("no provided id is one zee provides: %s" % ", ".join(clash), clash.is_empty())

	var zee_doc: Variant = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path("res://").path_join("../zee-dot-weapons/provides.json")))
	if zee_doc is Dictionary:
		var zee_ids := {}
		for e: Dictionary in (zee_doc as Dictionary).get("entries", []):
			zee_ids[e["id"]] = true
		var shared := 0
		for e: Dictionary in entries:
			if zee_ids.has(e["id"]):
				shared += 1
		_check("none collides with zee's provides.json", shared == 0)
	else:
		_check("zee's provides.json is not beside this checkout (skipped)", true)

	var index := DotContentIndex.new()
	index.set_session(DotContentIndex.SESSION_SOLO)
	var added := index.add_pack({
		"content_id": "gamemann/zed-dot-weapons", "version": "1.0.0", "prefix": "res://",
		"session": "solo", "source": "subscription", "provides": provides,
	})
	_check("the index takes the pack", added.ok)
	var cat := DotWeaponCatalogue.new().follow_content(index)
	var listed := 0
	for def in code:
		if cat.has(def.id) and cat.listing(def.id) != null:
			listed += 1
	_check("a catalogue following the index lists every zed weapon", cat.size() == code.size() and listed == code.size())
	_check("and validates", cat.validate().ok)
	_check("a delivered weapon instantiates its behaviour", cat.instantiate(ZedWeaponIds.UZI).ok and cat.instantiate(ZedWeaponIds.MOLOTOV).ok)
	cat.unfollow_content()

	_end()


func _art() -> void:
	_begin("the art")
	var ids := {}

	for art in ZedWeaponPack.art():
		ids[art.id] = art.validate().ok

	var all_valid := ids.values().all(func(ok: bool) -> bool: return ok)
	_check("an entry for every weapon, and each one valid", ids.size() == ZedWeaponIds.all().size() and all_valid)
	var models := ZedWeaponPack.validate_models()
	_check("every model is on disk: %s" % ("" if models.ok else models.error.message), models.ok)
	_check("zee's art table validates with this pack's in it", ZeeWeaponArtTable.validate().ok)

	# A mounted pack has no `res://assets/…`, so a model that names a file by that path loads
	# without it (tools/bake_food.gd says why the Food Kit's had to be baked).
	var leaning: Array[String] = []
	for art in ZedWeaponPack.art():
		for dep in ResourceLoader.get_dependencies(art.model_path):
			leaning.append("%s -> %s" % [art.id, dep])
	_check("no model leans on another file: %s" % ", ".join(leaning), leaning.is_empty())

	var muzzle := ZeeModelCache.muzzle_distance(ZedWeaponPack.WEAPONS_DIR + "sniperSand.glb", ZedWeaponPack.GUN_FORWARD)
	# Half the rifle's 1.04 m: the model is centred along its length, so the far end is there.
	_check("the hunting rifle's muzzle is measured half its length out (%.2f m)" % muzzle, absf(muzzle - 0.52) < 0.03)

	# [b]zee's hold, turned for a gun pointing the other way.[/b] zee's cant and turn are written
	# for a blaster pointing -Z; these point +Z, so the same numbers written straight across
	# tip the gun's left side up. The hold must be exactly zee's hold with the model turned
	# round first: in the view, the muzzle goes where a zee rifle's goes and so does the top.
	var rifle := ZeeWeaponArtTable.get_art(ZedWeaponIds.HUNTING_RIFLE)
	var zee_turn := Basis.from_euler(ZeeWeaponArtTable.pose_rotation(ZeeWeaponArtTable.POSE_RIFLE) * (PI / 180.0))
	var held := rifle.view_transform().basis.orthonormalized()
	var muzzle_dir := held * ZedWeaponPack.GUN_FORWARD
	_check("a gun is held on zee's hold: muzzle where zee's points, %s" % muzzle_dir,
		muzzle_dir.is_equal_approx(zee_turn * Vector3.FORWARD))
	_check("and canted the same way, top toward the crosshair (%s)" % (held * Vector3.UP),
		(held * Vector3.UP).is_equal_approx(zee_turn * Vector3.UP) and (held * Vector3.UP).x < 0.0)

	# [b]Every heavy gun reloads with something carried into it in sight[/b]: a box and belt,
	# or a round pushed in from where the hand can be seen. A 9 cm round inside a fist, or a
	# launcher reload keyed by a name zee does not have, reads as the gun tilting.
	var unfed: Array[String] = []
	for id in [ZedWeaponIds.MACHINE_GUN, ZedWeaponIds.GRENADE_LAUNCHER, ZedWeaponIds.ROCKET_LAUNCHER]:
		var art := ZeeWeaponArtTable.get_art(id)
		var boxed := art != null and art.magazine_part != &""
		var fed := art != null and art.magazine_loose and art.load_from != Vector3.ZERO and not art.reload_keys.is_empty()
		if not boxed and not fed:
			unfed.append(String(id))
	_check("every heavy gun reloads with something carried in, in sight: %s" % ", ".join(unfed), unfed.is_empty())
	_end()


## zee's view model measures an iron sight on every unscoped gun and, aimed, holds its line
## through the screen's centre. These guns point +Z and stand on their base, so a line found
## on the wrong side or end of the model shows up here as a sight off the axis.
func _sights() -> void:
	_begin("sights")
	var view := ZeeViewModel.new()
	view.show_arms = false
	add_child(view)
	var sighted := 0
	var unsighted: Array[String] = []
	var worst := 0.0
	var worst_id := &""
	for art in ZedWeaponPack.art():
		if not art.aim_enabled or art.aim_scoped:
			continue
		view.equip(art)
		view.aim(true)
		for _i in range(30):
			view._process(0.02)
		var points := view.sight_points()
		if points.is_empty():
			unsighted.append(String(art.id))
			continue
		sighted += 1
		var rear: Vector3 = points.rear
		var front: Vector3 = points.front
		var off := maxf(Vector2(rear.x, rear.y).length(), Vector2(front.x, front.y).length())
		# The front sight is further out than the rear, or the gun is held backwards.
		if front.z >= rear.z:
			off += 1.0
		if off > worst:
			worst = off
			worst_id = art.id
	_check("every unscoped gun has a measured iron sight (%d; none for %s)" % [sighted, ", ".join(unsighted)], sighted == 12)
	_check("and its line runs through the screen's centre when aimed (worst %.4f m, %s)" % [worst, worst_id],
		worst < 0.002)
	view.queue_free()
	_end()


## Every gun, given alone to an arsenal on zee's catalogue, fires when its trigger is held.
func _firing() -> void:
	_begin("firing")
	var dead: Array[String] = []
	var spent: Array[String] = []

	for id in ZedWeaponIds.all():
		var def: DotWeaponDef = ZedWeaponPack.table()[id]

		if def.tags.has(ZeeWeaponIds.TAG_THROWN):
			continue

		var arsenal := _arsenal()
		var _given := arsenal.give(id)
		_run(arsenal, 0, 80, 0)
		var outcomes := _run(arsenal, 80, 160, DotWeaponCommand.BUTTON_ATTACK)
		var out := 0

		for o: DotWeaponOutcome in outcomes:
			out += o.shots.size() + o.spawns.size()

		if out == 0:
			dead.append(String(id))

		var pool := arsenal.ammo().count(def.ammo_type) + (arsenal.current().magazine if arsenal.current() != null else 0)

		if pool >= def.magazine + def.reserve:
			spent.append(String(id))

		remove_child(arsenal)
		arsenal.free()

	_check("every gun puts something into the world: dead %s" % ", ".join(dead), dead.is_empty())
	_check("and spends ammunition doing it: free %s" % ", ".join(spent), spent.is_empty())

	var launcher := _arsenal()
	var _l := launcher.give(ZedWeaponIds.ROCKET_LAUNCHER)
	_run(launcher, 0, 80, 0)
	var rocket: DotWeaponSpawn = null
	for o: DotWeaponOutcome in _run(launcher, 80, 120, DotWeaponCommand.BUTTON_ATTACK):
		if not o.spawns.is_empty():
			rocket = o.spawns[0]
	_check("a rocket flies straight", rocket != null and is_zero_approx(rocket.gravity_scale) and rocket.splash_damage > 200.0)
	remove_child(launcher)
	launcher.free()
	_end()


## The throwables leave the hand: a charge, a release, and a projectile with somewhere to go.
## A fuse used up by the cook is dot-weapon's "it went off in the hand", which throws nothing;
## a bottle's fuse of zero was exactly that on the first try.
func _throwing() -> void:
	_begin("throwing")

	for id in [ZedWeaponIds.MOLOTOV, ZedWeaponIds.PIPE_BOMB, ZedWeaponIds.BILE_JAR]:
		var arsenal := _arsenal()
		var _given := arsenal.give(id)
		_run(arsenal, 0, 60, 0)
		# Held, then let go, in one run: a release is an edge against the previous command.
		var thrown: DotWeaponSpawn = null

		for o: DotWeaponOutcome in _run(arsenal, 60, 110, DotWeaponCommand.BUTTON_ATTACK, 100):
			if not o.spawns.is_empty():
				thrown = o.spawns[0]

		_check("a %s is thrown, forward and with a fuse left" % String(id),
			thrown != null and thrown.velocity.length() > 5.0 and thrown.fuse_ticks > 0 and thrown.id == id)
		remove_child(arsenal)
		arsenal.free()

	_end()


## The six attachments: dot-weapon's catalogue takes them, each fits the carbine on its own
## mount, they change the document the way their names say, and each model is on disk, stands
## alone, and the carbine's model has the socket it goes on.
func _attachments() -> void:
	_begin("attachments")
	var cat := ZedWeaponPack.attachments()
	var bad: Array[String] = []
	for att in ZedWeaponPack.attachment_defs():
		if not att.validate().ok:
			bad.append(String(att.id))
	_check("six attachments, each valid: %s" % ", ".join(bad), cat.ids().size() == 6 and bad.is_empty())

	var carbine := ZedWeaponPack.assault_carbine()
	var choices := cat.choices_for(carbine)
	_check("the carbine takes something on each of its five mounts (%s)" % str(choices.keys()), choices.size() == 5)

	var fitting := DotWeaponFitting.make(carbine.id)
	fitting.fit(DotWeaponAttachment.MOUNT_MAGAZINE, ZedWeaponIds.EXTENDED_MAG)
	fitting.fit(DotWeaponAttachment.MOUNT_MUZZLE, ZedWeaponIds.SUPPRESSOR)
	fitting.fit(DotWeaponAttachment.MOUNT_UNDERBARREL, ZedWeaponIds.FOREGRIP)
	var applied := cat.apply(carbine, fitting)
	var fitted: DotWeaponDef = applied.value if applied.ok else null
	_check("a full fitting applies (%s)" % ("" if applied.ok else applied.error.message), fitted != null)
	_check("an extended magazine holds ten more, and the catalogue's copy is untouched",
		fitted != null and fitted.magazine == 40 and carbine.magazine == 30)
	_check("a suppressor makes it silenced, a foregrip and a suppressor tame the kick",
		fitted != null and fitted.tags.has(ZeeWeaponIds.TAG_SILENCED)
		and absf(fitted.tuning.recoil_pitch - carbine.tuning.recoil_pitch * 0.72) < 0.001)

	var missing: Array[String] = []
	var leaning: Array[String] = []
	for id: StringName in ZedWeaponPack.ATTACHMENT_ART:
		var path: String = ZedWeaponPack.ATTACHMENT_ART[id].path
		if not ResourceLoader.exists(path):
			missing.append(path)
			continue
		for dep in ResourceLoader.get_dependencies(path):
			leaning.append("%s -> %s" % [id, dep])
	_check("every attachment has art, and every model is on disk: %s" % ", ".join(missing),
		ZedWeaponPack.ATTACHMENT_ART.size() == 6 and missing.is_empty())
	_check("and none leans on another file: %s" % ", ".join(leaning), leaning.is_empty())

	var gun := (load(ZeeWeaponArtTable.get_art(ZedWeaponIds.ASSAULT_CARBINE).model_path) as PackedScene).instantiate()
	var sockets: Array[String] = []
	for mount in carbine.mounts:
		if gun.find_child(String(ZedWeaponPack.socket_name(mount)), true, false) == null:
			sockets.append(String(mount))
	for id: StringName in ZedWeaponPack.ATTACHMENT_ART:
		for hide: StringName in ZedWeaponPack.ATTACHMENT_ART[id].hides:
			if gun.find_child(String(hide), true, false) == null:
				sockets.append("%s hides %s" % [id, hide])
	gun.free()
	_check("the carbine's model has a socket per mount and every node an attachment hides: missing %s" % ", ".join(sockets),
		sockets.is_empty())
	_end()


func _uninstall() -> void:
	_begin("uninstalling")
	ZedWeaponPack.uninstall()
	_check("its weapons leave zee's catalogue", not ZeeWeaponPack.table().has(ZedWeaponIds.UZI) and ZeeWeaponPack.table().size() == ZEE_COUNT)
	_check("and its art leaves zee's table", ZeeWeaponArtTable.get_art(ZedWeaponIds.UZI) == null)
	_check("and it says so", not ZedWeaponPack.installed())
	_end()


## A process that installs the pack and quits without uninstalling it exits cleanly. Run as a
## second process because the failure is the engine aborting AFTER every check has passed.
func _exiting() -> void:
	_begin("exiting")
	var output: Array = []
	var code := OS.execute(OS.get_executable_path(), [
		"--headless", "--path", ProjectSettings.globalize_path("res://"),
		"--script", "res://tools/exit_check.gd",
	], output, true)
	var said := "\n".join(output)
	_check("a process left with the pack installed exits cleanly (exit %d)" % code,
		code == 0 and said.contains("installed:"))
	_end()


# --- Helpers ---------------------------------------------------------------------

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
