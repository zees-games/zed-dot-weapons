# History

Bug stories worth keeping, because each could come back. The rules they left are in [CLAUDE.md](../CLAUDE.md).

## 2026-10-10: the axis, proven, and zee's hold turned round

zee-dot-weapons found that day that every one of its blasters had been drawn stock-first for as long as the pack existed: its meshes are symmetric along their length, so the rack's muzzle pip sat at whichever end the table named, and the rack agreed with a wrong table. This pack's `GUN_FORWARD` (+Z) had been settled by the same rack, so it was suspect too. A side render in headless Blender with a red marker on the model's +Z end (and a control render of one of zee's blasters, which put the marker on its stock) settled it: the marker sits on the muzzle of the pistol, the uzi, the shotgun, the hunting rifle, the machine gun and the rocket launcher. +Z was right: the rack puts its pip at whichever end the table names, and here the person reading it had read the right end as the muzzle. zee's reader had not.

The same day zee moved its hip hold to a canted, turned pose (`ZeeWeaponArtTable.pose_rotation`), a lower aim place and per-pose reload keys. This pack still wrote its old `view_rotation` (-2, -4, 0) and derived only the offset from zee, so its guns sat at the new place uncanted, showing their top and left side. zee's rotation is in the model's own space for a model pointing -Z; `orientation()` turns a +Z model round 180 degrees about Y first, and conjugating by that turn flips the sign of a pitch and a roll and keeps a yaw. Written straight across, the cant tipped the left side up and the underside toward the eye. `hold_rotation` makes the conversion, and the suite compares the held muzzle and top against zee's.

The aim place had the same gap: zed's guns stand on their base and are lifted by half their height, and the lift was applied to the hip offset only, so at the sight the gun sat half its height too high. Both lifts now go through the hold's basis.

The molotov's bottle was at 0.45 scale, thinner than the glove zee closes round it (a glove is never smaller than 0.6 of its grip size), so the hand hid the whole bottle but the neck. It is 0.7 now.
