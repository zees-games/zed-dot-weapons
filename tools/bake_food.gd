extends SceneTree

## Bakes the Food Kit models this pack uses into scenes that carry their own texture.
##   godot --headless --path . --script tools/bake_food.gd
##
## [b]Why they cannot be used as imported.[/b] The Food Kit's GLBs name an external
## `Textures/colormap.png`, and the import records it as `res://assets/food-kit/Textures/…`.
## A game delivered as a dot-cloud pack is mounted under `res://dot_cloud/<id>/<version>/`,
## where that absolute path does not exist, so the bottle loads white. (The Weapon Pack's
## models use plain material colours and have no such path.) An ImageTexture made from the
## pixels belongs to the scene it is saved in, so the baked scene has no dependency at all.

const MODELS := ["wine-red", "honey"]


func _initialize() -> void:
	for name in MODELS:
		var source := "res://assets/food-kit/%s.glb" % name
		var root: Node = (load(source) as PackedScene).instantiate()
		_embed(root, root)
		var packed := PackedScene.new()
		var _packed_ok := packed.pack(root)
		var out := "res://assets/food-kit/%s.scn" % name
		var saved := ResourceSaver.save(packed, out, ResourceSaver.FLAG_COMPRESS)
		print("%s -> %s: %s" % [source, out, error_string(saved)])
		root.free()

	quit()


func _embed(node: Node, owner_node: Node) -> void:
	if node != owner_node:
		node.owner = owner_node

	if node is MeshInstance3D and (node as MeshInstance3D).mesh != null:
		var mesh: Mesh = (node as MeshInstance3D).mesh.duplicate()

		for i in mesh.get_surface_count():
			var material := mesh.surface_get_material(i) as StandardMaterial3D

			if material != null and material.albedo_texture != null:
				var copy := material.duplicate() as StandardMaterial3D
				copy.albedo_texture = ImageTexture.create_from_image(material.albedo_texture.get_image())
				mesh.surface_set_material(i, copy)

		(node as MeshInstance3D).mesh = mesh

	for child in node.get_children():
		_embed(child, owner_node)
