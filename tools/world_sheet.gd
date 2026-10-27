extends Node3D

## Zee's third-person sheet with this pack installed first, so the zed ids resolve.
## tools/screenshot.sh --world service_pistol: screenshots/world_<id>.png

const ZEE_SHEET := "../zee-dot-weapons/tools/world_sheet.gd"


func _ready() -> void:
	ZedWeaponPack.install()
	var path := ProjectSettings.globalize_path("res://").path_join(ZEE_SHEET).simplify_path()
	var script: GDScript = GDScript.new()
	script.source_code = FileAccess.get_file_as_string(path)
	script.reload()
	set_script(script)
	call(&"_ready")
