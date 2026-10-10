extends SceneTree

## Installs the pack and quits, and nothing else. Run in a process of its own by the suite's
## "exiting" section, which reads the exit code: a source zee holds that outlives its script
## at exit aborts the engine after everything else has passed.

func _initialize() -> void:
	ZedWeaponPack.install()
	print("installed: %d weapons" % ZeeWeaponPack.weapons().size())
	quit(0)
