extends SceneTree

## Prints every vendored model's bounds: size, and where its origin sits in it.
##   godot --headless --path . --script tools/measure.gd

func _initialize() -> void:
	for dir in ["res://assets/weapon-pack/", "res://assets/food-kit/"]:
		for file in DirAccess.get_files_at(dir):
			if not file.ends_with(".glb"):
				continue
			var scene: PackedScene = load(dir + file)
			var node := scene.instantiate()
			var box := _bounds(node, Transform3D.IDENTITY)
			print("%-28s size %s  min %s  max %s" % [file, box.size.snapped(Vector3.ONE * 0.001), box.position.snapped(Vector3.ONE * 0.001), box.end.snapped(Vector3.ONE * 0.001)])
			node.free()
	quit()


func _bounds(node: Node, parent: Transform3D) -> AABB:
	var xf := parent
	if node is Node3D:
		xf = parent * (node as Node3D).transform
	var box := AABB()
	var started := false
	if node is MeshInstance3D and (node as MeshInstance3D).mesh != null:
		box = xf * (node as MeshInstance3D).mesh.get_aabb()
		started = true
	for child in node.get_children():
		var inner := _bounds(child, xf)
		if inner.size != Vector3.ZERO:
			box = inner if not started else box.merge(inner)
			started = true
	return box
