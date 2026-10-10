@tool
extends EditorPlugin

## Editor entry point for zed-dot-weapons. Registers nothing: the pack is documents and a
## table of filenames, and its weapons are carried by zee-dot-weapons' rig. A game calls
## [method ZedWeaponPack.install] when it loads; there is no autoload to do it for it.


func _enter_tree() -> void:
	pass


func _exit_tree() -> void:
	pass
