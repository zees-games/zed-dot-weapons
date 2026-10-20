# zed-dot-weapons

A second weapons pack, on top of zee-dot-weapons. Read `../../CLAUDE.md` and `../zee-dot-weapons/CLAUDE.md` first: everything about how a weapon is drawn, held, heard, replicated and rolled back is zee's, and this repository only adds content to it. Its `origin` is `git@github.com:zees-games/zed-dot-weapons.git`, in Christian's `zees-games` organisation like zee. Built 2026-10-10 for game-zombie-zone, which asked for "a separate addon pack, so the server can carry two weapon packs".

## The one idea: content, through zee's seam

A second copy of zee's rig, view model and effects for fifteen more weapons would be two rigs a game has to choose between. So this pack is documents (`ZedWeaponPack.weapons`), art entries (`ZedWeaponPack.art`, `ZeeWeaponArt` objects) and a sound class per gun, and `ZedWeaponPack.install()` hands all three to zee through `ZeeWeaponPack.add_source`, `ZeeWeaponArtTable.add_source` and `ZeeWeaponSound.set_class` (added to zee for this, 2026-10-10). After that every catalogue zee builds, which is every rig's default, carries both packs. **zee's ids win a clash**, so no id here may be one zee has (`service_pistol`, not `pistol`); the suite checks.

**Install before the first rig is set up.** A rig builds its catalogue once, in `setup()`; one built before `install()` carries zee's weapons for as long as it lives.

**The sources are static methods, not lambdas.** zee keeps them in a static variable that the engine clears after it has freed the scripts at exit, and the first version's lambdas outlived their script: every process that installed the pack aborted on the way out (`double free or corruption`, exit 134) with every check passed. dot-server-deploy's zombiezone_client found it by its exit code; the suite's "exiting" section runs `tools/exit_check.gd` as a second process and fails with a lambda put back.

## The Workshop form

`weapons/*.tres` (one `DotWeaponDef` each) and `provides.json` (schema 1, kind `weapon`, `meta.asset_root` `.`) publish the pack so that subscribing to it lists its weapons in a `DotWeaponCatalogue` following the content index. They are **generated** from `ZedWeaponPack.weapons` by `tools/export-defs.sh` (`ZedDefExport`, which reuses zee's `ZeeDefExport` for categories and the document); the suite's "Workshop files" section fails when they are stale, when an id is not a `ZedWeaponPack` weapon, or when one collides with zee's. Change a builder, re-run the script, commit all of it.

## Ticks at 64 Hz, and every row says so

Every duration is in ticks at `ZedWeaponPack.TICK_RATE` (64), and both builders (`_gun`, `_thrown`) set `DotWeaponDef.authored_tick_rate` to it, so dot-weapon's arsenal scales each row to the rate a server runs at (zee's [design](../zee-dot-weapons/docs/design.md#durations-are-ticks)). A builder added without it fires at another speed off 64 Hz; the suite's "the documents" section counts the stamped rows.

## What a throwable does is the game's

dot-weapon spawns nothing; a thrown weapon's use is a `DotWeaponSpawn` handed to the game. The molotov, pipe bomb and bile jar say what they are with tags (`ZedWeaponIds.TAG_MOLOTOV`, `TAG_PIPE_BOMB`, `TAG_BILE`) and the flamethrower with `TAG_INCENDIARY`, so a game that has fire, a lure and bile can do the right thing with a pack it has never heard of. game-zombie-zone's `ZzGame._throw` is the reference.

**A thrown weapon's fuse must outlast the longest hold.** dot-weapon's thrown behaviour reads a fuse used up by the cook as "it went off in the hand" and throws nothing. A bottle has no fuse, and the first molotov, written with `fuse_ticks` 0, never left the hand; it is ten seconds now and no game reads it. The suite's "throwing" section fails with the zero put back.

## Three things the renders found, that no check can

- **Every gun pointed backwards.** Kenney's Weapon Pack lies along Z with each model centred along its length, so the measured muzzle is the same distance out at either end and the suite's muzzle check passes both ways. The rack (`tools/screenshot.sh --rack`) put the red muzzle pips on the shotguns' wooden stocks and the rifle's scope end. The models point **+Z**, the opposite of zee's blasters (`GUN_FORWARD`). The rack cannot prove an axis (zee's blasters passed it reversed for years); a Blender side render with a marker on +Z did: the marker is on the muzzle of the pistol, uzi, shotgun, hunting rifle, machine gun and rocket launcher. [history](docs/history.md)
- **zee's hold is written for -Z, so it is turned before it is used** (`ZedWeaponPack.hold_rotation`: pitch and roll change sign, yaw does not). Every gun takes zee's pose offset, cant, aim place and per-pose reload keys; zee's numbers written straight across tip the gun's left side up. The lift by half the height goes through the hold's basis, at the hip and at the aim. The suite's "held on zee's hold" checks fail with the signs undone. [history](docs/history.md)
- **Aimed, every unscoped gun looks down an iron sight zee measures on its mesh** (zee's `docs/view-model.md`, "Aiming down the sight"): the guns' +Z and their base origin need nothing from this pack, and the suite's "sights" section checks each line runs through the screen's centre. The hunting rifle stays scoped.
- **The models stand on their base**, origin at the middle of the bottom face, unlike zee's centred blasters, so each gun is lowered by half its measured height in both views (scaled with the model, zee's third trap). Real size, too: the pistol is 0.3 m and the rifle 1.04 m against zee's toy blasters, so the pose scale is zee's times `REAL_SCALE` (1.45).
- **A bottle turned the way zee turns a grenade is drawn as its own base**, a dark hexagon behind the hand. zee maps a grenade's +Y onto the view's forward, which for something round is invisible. The throwables here are said to face forward already, so they are held standing up.

- **Every gun has something to reload with** (`ZedWeaponPack._fed`): zee's `box_magazine` part for the pistols and uzis (`_boxed`: the Weapon Pack's `ammo_uzi` is a 6.5 cm cartridge that vanished inside the grip and glove; drawn 1.5x, and the reload keys `lifted` so the grip's foot is on screen), and a loose round for the hand-fed ones (shotgun shell, rifle cartridge, machine-gun round, grenade, rocket; `magazine_loose`). Without one zee's support hand never leaves the fore-end and the reload is the gun rolling and nothing else. Offsets are in model space (+Z forward, on its base) at the grip's foot or the loading port; check them on `--sheet` with `EXTRA="--reloads …"` (18 reload frames). **The heavy guns are not fed like that** (`_box_fed`, `_hand_fed`): the machine gun swaps zee's ammunition box and belt (`magazine_part`, built in code); the grenade launcher breaks and takes a grenade from above, the rocket launcher is tipped up and a rocket (turned 180, nose to the muzzle) pushed down the muzzle (`load_from`, `magazine_scale`, zee's `RELOAD_KEYS_BREAK` / `_MUZZLE` looked up by name, set by name so an older zee still loads). The rocket at the back of the tube never showed: the tube's rear end is below the screen. The suite's "carried in, in sight" check fails with a key name zee lacks. **The pump shotgun and the hunting rifle are fed like zee's pump guns and bolt gun** (`_rounds`, zee's `RELOAD_KEYS_TUBE` / `_BOLT`): three shells up through the port, two cartridges laid into the top (turned to lie along the receiver, drawn at 0.7: a cartridge at 2x filled the screen).

## The guns are kitbashed

The eleven real-world guns are `assets/kitbash/<id>.glb`, built by `art-src/guns/build.py` from `zed_guns.py` (zee's kit, `zed_kit.py`, plus `export_standing`: +Z forward, origin at the middle of the base, as `ZedWeaponPack` expects). `build.py` prints each gun's size and writes `art-src/guns/out/measure.json`; the heights in `art()` come from there, and the reload offsets are in model space, so a changed recipe means re-checking `--sheet` with `EXTRA="--reloads …"`. The Weapon Pack still supplies the ammunition and the pipe bomb (`WEAPONS_DIR`); the guns come from `KIT_DIR`. A vendoring game needs `tools/sync-art.sh` after a rebuild.

## The high-detail guns (`assets/hq/`, `art-src/hq/`)

The assault carbine (2026-10-20) is the first of a second tier: modelled from scratch in `art-src/hq/` (`hq_kit.py` the kit, `hq_m4.py` the gun, `hq_attachments.py` the six attachments, `build_hq.py` the driver), each part built twice, a low mesh that ships and a bevelled high one baked onto it (normal, AO into the albedo, ORM), one 2048 set per gun and 512-1024 per attachment. Budget: 5-12k triangles a gun, 1-2k an attachment; `build_hq.py` prints the triangles per part and writes `art-src/hq/out/measure.json`. Rebuild on staging02 (the GPU bakes; CPU works but is slow), never with `--quick` for a model that ships. The textures are procedural, so there is nothing to credit; keep it that way or credit the CC0 source in the README.

- **The model points +Z, origin at the bottom, x on the bore**, like the kitbashes, so `_gun_art` takes it with the path as its last argument. `CARBINE_HEIGHT` is measured with the standard magazine in.
- **The gun's parts are nodes**: `body`, `magazine`, `rear_sight`, so an attachment can hide what it replaces (`ATTACHMENT_ART[id].hides`: the scope hides the rear sight, the extended magazine the magazine).
- **Sockets are empties named `socket_<mount>`** (`socket_name()`), identity rotation; each attachment's origin is where it meets the gun, so it is parented to the socket with no offset. A socket that carried the export's 180-degree turn put the suppressor on backwards, and stale `matrix_world` put every socket on one point: `hq_kit.export_glb` updates the view layer and resets the empties' rotation.
- **`sight_rear` and `sight_front` mark the real sights**, and zee aims down them and builds no ring (zee's `IronSight.from_marks`).
- **The `.glb.import` files embed the textures as Basis Universal** (`gltf/embedded_image_handling=2`): the model stands alone in a delivered pack, and nothing is extracted next to it.
- `art-src/hq/render_hq.py` renders Cycles frames of the exported files with attachments on their sockets, as the game fits them; the frames of record are in `reports/models/2026-10-20/`.

**Attachments are data here, the rules are dot-weapon's** (`DotWeaponAttachment`, `DotWeaponAttachments`): `ZedWeaponPack.attachment_defs()` says what each one changes, `attachments()` is the catalogue an arsenal takes. **zee does not draw a fitted attachment yet**: `ATTACHMENT_ART` and the sockets are ready for it.

## Every model stands alone, because a game is delivered as a pack

A game that vendors this art is mounted under `res://dot_cloud/<id>/<version>/`, where a model that names another file by `res://assets/…` loads without it. The Weapon Pack's models use plain material colours and name nothing. The Food Kit's name an external `Textures/colormap.png`, so the bottle and the jar are baked by `tools/bake_food.gd` into `.scn` files that carry the texture inside them (an `ImageTexture` made from the pixels), and the art names those. The suite's "no model leans on another file" asks `ResourceLoader.get_dependencies` of every model; pointed at the raw `.glb` it fails.

## Validating

```bash
godot --headless --path . --import
find . -name '*.gd' -not -path './.godot/*' -not -path './addons/dot_*' -not -path './addons/zee_weapons/*' | while read f; do
    godot --headless --path . --check-only --script "res://${f#./}"
done
timeout 120 godot --headless --path . res://examples/zed_selftest.tscn   # 11 sections, 51 checks
tools/screenshot.sh --rack                                                # and look at it
tools/screenshot.sh molotov
tools/screenshot.sh --sheet service_pistol pump_shotgun hunting_rifle molotov   # zee's 18-frame contact sheet, per weapon
```

Review every change to a gun's hold on the contact sheet (`--sheet`, the same frames as zee's, so the two packs' sheets can be laid side by side). `examples/zed_range.gd` is zee's range with `ZedWeaponPack.install()` added; keep it a copy, so a sheet change in zee comes across by copying the file.

`tools/measure.gd` prints every vendored model's bounds (`godot --headless --path . --script tools/measure.gd`), which is where the heights in `ZedWeaponPack.art()` came from.
