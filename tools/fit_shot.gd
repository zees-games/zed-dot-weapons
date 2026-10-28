extends Node3D

## One frame of a carbine with attachments fitted, through the view model or the world model.
## godot --path . res://tools/fit_shot.tscn -- --fit red_dot,suppressor [--aim] [--world] --out f.png

const SETTLE_FRAMES := 40


func _ready() -> void:
	ZedWeaponPack.install()
	var args := OS.get_cmdline_user_args()
	var ids := PackedStringArray()
	var out := "fit_shot.png"
	var world := args.has("--world")
	for i in args.size():
		if args[i] == "--fit" and i + 1 < args.size():
			ids = args[i + 1].split(",", false)
		elif args[i] == "--out" and i + 1 < args.size():
			out = args[i + 1]

	var fitting := DotWeaponFitting.make(ZedWeaponIds.ASSAULT_CARBINE)
	var catalogue := ZedWeaponPack.attachments()
	for id in ids:
		fitting.fit(catalogue.get_attachment(StringName(id)).mount, StringName(id))

	var art := ZeeWeaponArtTable.get_art(ZedWeaponIds.ASSAULT_CARBINE)
	var camera := $Camera as Camera3D
	if world:
		var model := ZeeWorldModel.new()
		add_child(model)
		model.equip(art)
		model.set_fitting(fitting)
		model.global_position = Vector3(0.0, 0.0, 0.0)
		camera.look_at_from_position(Vector3(0.9, 0.35, 0.9), Vector3(0.0, 0.15, 0.0))
	else:
		var view := ZeeViewModel.new()
		camera.add_child(view)
		view.equip(art)
		view.set_fitting(fitting)
		view.aim(args.has("--aim"))
		for i in 90:
			view.advance(1.0 / 60.0)
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	var image := get_viewport().get_texture().get_image()
	print("saved ", out, " ", image.save_png(out))
	get_tree().quit()
