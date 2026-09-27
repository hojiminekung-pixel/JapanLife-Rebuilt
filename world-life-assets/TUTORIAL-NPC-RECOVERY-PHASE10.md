# World Life — Tutorial NPC Recovery (Phase 10)

## Confirmed native path

The original Master contains a dedicated tutorial manager and NPC path:

- `CTutorialManager::SetTutorial(int)` selects tutorial implementations by tutorial ID.
- Tutorial ID `0x46` (70) instantiates `CTutorialGetNPC`.
- `CTutorialGetNPC::Render()` scans the map character list and selects a character whose internal object/NPC type field at `CCharInstance + 0x34` equals `0x3E5` (997 decimal).
- `CCharInstance::CreateNewNPC(SNpcInfo const*)` stores the `SNpcInfo` pointer at `+0x78` and the special NPC/object type from `SNpcInfo + 0x0C` into `+0x34` and `+0x48`.
- `CCharInstanceManager::PopNPC(...)` creates the character from the supplied `SNpcInfo` pointer.
- `CUIAvatar::SetNPCID(unsigned)` separately maps an NPC-table entry to portrait/avatar fields. This is a different path from `CTutorialGetNPC::Render()`.

## Implication

The tutorial adviser should not be replaced by blindly swapping a UI PNG. The game has two relevant character paths:

1. Map/tutorial character path — live `CCharInstance` + `SNpcInfo`.
2. Portrait/avatar path — `CUIAvatar` + `CNpcTable`.

The exact replacement should preserve whichever path each tutorial uses.

## Safe implementation target

- Keep the original Master, font, mapdata, packed textures and save systems unchanged.
- Add a black-duck adviser as a new character/resource variant.
- Give adviser outfits distinct variant IDs for future chapters.
- Reserve the crown duck for the player role.
- Reserve the no-crown duck for staff.
- Do not modify `data_npc.smf` or tutorial binaries until the exact `SNpcInfo`/texture contract is recovered.

## Recovered tutorial IDs

| Tutorial ID | Native implementation |
|---:|---|
| 0x46 (70) | CTutorialGetNPC |
| 0xBE (190) | CTutorialCleanMascotCity |
| 0xC8 (200) | CTutorialAcceptMascotSale |
| 0xDC (220) | CTutorialInviteFriends |
| 0xE6 (230) | CTutorialAcceptMascotHelpTrain |
| 0xF0 (240) | CTutorialManageHotel |
| 0xFA (250) | CTutorialGetEnergy |
| 0x14 (20) | CTutorialConstructTrainStation |
| 0x0A (10) | CTutorialCollectEarning |
| 0x28 (40) | CTutorialMoveObj |

The mascot-related tutorial classes already exist natively, so the replacement can be integrated at the character/resource layer instead of rebuilding the tutorial UI.


## Additional texture finding

The `packed*.smf` family uses a `text1000` texture container rather than ordinary PNG files. Several large resources have decompressed payload sizes consistent with block-compressed GPU texture storage. The duck artwork should therefore be converted into the exact packed texture format only after the target atlas/slot and metadata are identified; raw PNG substitution is unsafe.
