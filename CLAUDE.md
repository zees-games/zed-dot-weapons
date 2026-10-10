# zed-dot-weapons

A second weapons pack, on top of zee-dot-weapons. Read `../../CLAUDE.md` and `../zee-dot-weapons/CLAUDE.md` first: everything about how a weapon is drawn, held, heard, replicated and rolled back is zee's, and this repository only adds content to it. Its `origin` is `git@github.com:gamemann/zed-dot-weapons.git`, on Christian's account like zee. Built 2026-10-10 for game-zombie-zone, which asked for "a separate addon pack, so the server can carry two weapon packs".

## The one idea: content, through zee's seam

A second copy of zee's rig, view model and effects for fourteen more weapons would be two rigs a game has to choose between. So this pack is documents (`ZedWeaponPack.weapons`), art entries (`ZedWeaponPack.art`, `ZeeWeaponArt` objects) and a sound class per gun, and `ZedWeaponPack.install()` hands all three to zee through `ZeeWeaponPack.add_source`, `ZeeWeaponArtTable.add_source` and `ZeeWeaponSound.set_class` (added to zee for this, 2026-10-10). After that every catalogue zee builds, which is every rig's default, carries both packs. **zee's ids win a clash**, so no id here may be one zee has (`service_pistol`, not `pistol`); the suite checks.

**Install before the first rig is set up.** A rig builds its catalogue once, in `setup()`; one built before `install()` carries zee's weapons for as long as it lives.

## What a throwable does is the game's

dot-weapon spawns nothing; a thrown weapon's use is a `DotWeaponSpawn` handed to the game. The molotov, pipe bomb and bile jar say what they are with tags (`ZedWeaponIds.TAG_MOLOTOV`, `TAG_PIPE_BOMB`, `TAG_BILE`) and the flamethrower with `TAG_INCENDIARY`, so a game that has fire, a lure and bile can do the right thing with a pack it has never heard of. game-zombie-zone's `ZzGame._throw` is the reference.

**A thrown weapon's fuse must outlast the longest hold.** dot-weapon's thrown behaviour reads a fuse used up by the cook as "it went off in the hand" and throws nothing. A bottle has no fuse, and the first molotov, written with `fuse_ticks` 0, never left the hand; it is ten seconds now and no game reads it. The suite's "throwing" section fails with the zero put back.

## Three things the renders found, that no check can

- **Every gun pointed backwards.** Kenney's Weapon Pack lies along Z with each model centred along its length, so the measured muzzle is the same distance out at either end and the suite's muzzle check passes both ways. The rack (`tools/screenshot.sh --rack`) put the red muzzle pips on the shotguns' wooden stocks and the rifle's scope end. The models point +Z, like zee's blasters (`GUN_FORWARD`).
- **The models stand on their base**, origin at the middle of the bottom face, unlike zee's centred blasters, so each gun is lowered by half its measured height in both views (scaled with the model, zee's third trap). Real size, too: the pistol is 0.3 m and the rifle 1.04 m against zee's toy blasters, so the pose scale is zee's times `REAL_SCALE` (1.45).
- **A bottle turned the way zee turns a grenade is drawn as its own base**, a dark hexagon behind the hand. zee maps a grenade's +Y onto the view's forward, which for something round is invisible. The throwables here are said to face forward already, so they are held standing up.

## Every model stands alone, because a game is delivered as a pack

A game that vendors this art is mounted under `res://dot_cloud/<id>/<version>/`, where a model that names another file by `res://assets/…` loads without it. The Weapon Pack's models use plain material colours and name nothing. The Food Kit's name an external `Textures/colormap.png`, so the bottle and the jar are baked by `tools/bake_food.gd` into `.scn` files that carry the texture inside them (an `ImageTexture` made from the pixels), and the art names those. The suite's "no model leans on another file" asks `ResourceLoader.get_dependencies` of every model; pointed at the raw `.glb` it fails.

## Validating

```bash
godot --headless --path . --import
find . -name '*.gd' -not -path './.godot/*' -not -path './addons/dot_*' -not -path './addons/zee_weapons/*' | while read f; do
    godot --headless --path . --check-only --script "res://${f#./}"
done
timeout 120 godot --headless --path . res://examples/zed_selftest.tscn   # 7 sections, 25 checks
tools/screenshot.sh --rack                                                # and look at it
tools/screenshot.sh molotov
```

`tools/measure.gd` prints every vendored model's bounds (`godot --headless --path . --script tools/measure.gd`), which is where the heights in `ZedWeaponPack.art()` came from.
