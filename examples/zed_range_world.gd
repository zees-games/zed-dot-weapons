extends Node

## The range's static world for zed_range.gd, which extends this: floor, walls, target props,
## the stand-in character and the contact sheet's roof.

## Where the target props come from.
const TARGETS := "res://assets/blaster-kit/"


## `--dummy`: a character standing in the line of fire, so a capture shows a shot landing on a
## body (ZeeShotFx's red burst) rather than on the far wall.
func _add_dummy() -> void:
	var body := CharacterBody3D.new()
	body.name = "Dummy"
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.35
	capsule.height = 1.8
	shape.shape = capsule
	body.add_child(shape)
	var mesh := MeshInstance3D.new()
	var look := CapsuleMesh.new()
	look.radius = 0.35
	look.height = 1.8
	mesh.mesh = look
	mesh.material_override = _material(Color(0.55, 0.62, 0.72))
	body.add_child(mesh)
	$World.add_child(body)
	var eye := _controller.eye_transform()
	var ahead := -eye.basis.z
	ahead.y = 0.0
	body.global_position = eye.origin + ahead.normalized() * 6.0 + Vector3(0.0, -0.75, 0.0)


## A floor, a back wall and the kit's own targets, built in code.
##
## In code because this example is meant to be read top to bottom, and a scene file is
## the one part of a Godot project that cannot be. A real level is a scene an artist
## made; this is a page you can check.
func _build_world() -> void:
	var world := $World

	_add_box(world, Vector3(70.0, 1.0, 70.0), Vector3(0.0, -0.5, 0.0), Color(0.22, 0.24, 0.27))

	# A back wall to catch the pellets, so a shotgun's pattern is visible as a pattern.
	_add_box(world, Vector3(40.0, 8.0, 1.0), Vector3(0.0, 4.0, -18.0), Color(0.3, 0.32, 0.36))
	_add_box(world, Vector3(1.0, 8.0, 36.0), Vector3(-20.0, 4.0, 0.0), Color(0.28, 0.3, 0.34))
	_add_box(world, Vector3(1.0, 8.0, 36.0), Vector3(20.0, 4.0, 0.0), Color(0.28, 0.3, 0.34))

	# Something to jump on, so the airborne spread penalty can be felt.
	for i in range(4):
		_add_box(
			world,
			Vector3(3.0, 0.5 + float(i) * 0.5, 3.0),
			Vector3(-11.0, (0.5 + float(i) * 0.5) * 0.5, 2.0 - float(i) * 3.5),
			Color(0.35, 0.3, 0.26)
		)

	_add_targets(world)


## The kit's targets and crates, at the ranges the weapons are tuned for.
##
## Placed by distance on purpose: the shotgun stops at 26 m and the sniper reaches a
## kilometre, so a range with everything at one distance tells you nothing about either.
func _add_targets(world: Node3D) -> void:
	var rows := [
		{"z": -4.0, "model": "target-large.glb", "count": 3, "spacing": 4.0, "y": 1.4},
		{"z": -10.0, "model": "target-small.glb", "count": 5, "spacing": 3.0, "y": 1.5},
		{"z": -16.0, "model": "target-detail.glb", "count": 7, "spacing": 2.4, "y": 1.6},
	]

	for row: Dictionary in rows:
		var count := int(row["count"])
		var spacing := float(row["spacing"])

		for i in range(count):
			var model := ZeeModelCache.instantiate(TARGETS + str(row["model"]))
			if model == null:
				continue

			# [b]Turned a quarter and lifted off the floor.[/b] The target discs are
			# modelled in the YZ plane — five centimetres thick along X — so dropped in
			# untouched they face sideways and read as saucers lying on the ground. They
			# are also 34 cm across, which is a dinner plate at thirty metres, so they
			# are scaled up to something a sniper can be aimed at.
			model.rotation = Vector3(0.0, PI * 0.5, 0.0)
			model.scale = Vector3.ONE * 3.0
			model.position = Vector3(
				(float(i) - float(count - 1) * 0.5) * spacing,
				float(row["y"]),
				float(row["z"])
			)

			# A body behind the mesh, so a shot at one actually stops there and leaves a
			# mark. A target you can shoot through is a target that teaches nothing.
			var body := StaticBody3D.new()
			var shape := CollisionShape3D.new()
			var box := BoxShape3D.new()
			box.size = Vector3(0.2, 1.0, 1.0)
			shape.shape = box
			body.add_child(shape)
			body.position = model.position
			body.rotation = model.rotation
			world.add_child(body)

			world.add_child(model)

	# Crates for cover, and because a physics prop is the quickest way to see that a
	# launcher's splash is doing something.
	for i in range(6):
		var crate := ZeeModelCache.instantiate(TARGETS + "crate-medium.glb")
		if crate == null:
			continue
		crate.position = Vector3(
			-6.0 + float(i) * 2.4, 0.0, 6.0 - float(i % 3) * 2.0
		)
		world.add_child(crate)


func _add_box(parent: Node3D, size: Vector3, at: Vector3, colour: Color) -> void:
	var body := StaticBody3D.new()
	var mesh := MeshInstance3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	var block := BoxMesh.new()

	box.size = size
	block.size = size
	mesh.mesh = block
	mesh.material_override = _material(colour)

	shape.shape = box
	body.add_child(shape)
	body.add_child(mesh)
	body.position = at
	parent.add_child(body)


func _material(colour: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = colour
	material.roughness = 0.9
	return material


## A slab over the player on the sun's side, so the player stands in its shadow.
func _sheet_roof() -> Node3D:
	var sun := get_node_or_null("Sun") as DirectionalLight3D
	var toward := sun.global_transform.basis.z.normalized() if sun != null else Vector3.UP
	var body := StaticBody3D.new()
	var mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(5.0, 0.2, 5.0)
	mesh.mesh = box
	mesh.material_override = _material(Color(0.3, 0.3, 0.32))
	body.add_child(mesh)
	$World.add_child(body)
	body.global_position = _camera.global_position + toward * 3.0
	return body
