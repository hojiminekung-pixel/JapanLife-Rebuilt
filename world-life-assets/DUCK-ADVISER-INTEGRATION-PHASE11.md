# Phase 11 — Duck adviser integration findings

## Exact tutorial target recovered

The native function `CTutorialGetNPC::Render()` is at ARM/Thumb address `0x235644`.

Its logic is now confirmed:

1. Calls `CMapDataManager::GetCharList()`.
2. Walks the live character list.
3. Reads the character instance pointer at the list node's `+0x8`.
4. Checks the character's active flag at `CCharInstance + 0x58`.
5. Reads `CCharInstance + 0x34`.
6. Compares it with the literal **997 (0x3E5)**.
7. Only that matching live character receives the tutorial arrow/marker.

This means the adviser is a **real in-world character**, not merely a tutorial portrait.

## Important distinction

The native tutorial code does NOT itself choose the NPC texture. It only finds the already-spawned character by its internal NPC/object type and draws the tutorial marker over it.

Therefore the correct replacement point is earlier:

`SNpcInfo -> CCharInstance::CreateNewNPC -> character/NPC texture selection -> live CCharInstance -> CTutorialGetNPC::Render`

The portrait path (`CUIAvatar::SetNPCID`) is separate and must be handled separately for dialogs/windows that show a portrait.

## Resource investigation

`data_npc.smf` contains 32 table records. Existing named NPC records include tourists, citizens, NINJA, SAMURAI, SUMO, MONK, MAIKO and quest animals. The literal 997 does not occur in this file, so 997 is not simply an NPC-table ID.

The value 997 does occur in other game-data resources (building/shop/quest data), confirming that it is used as a general game identifier elsewhere. We therefore must not invent a new NPC ID by reusing 997.

## Safe next implementation

1. Recover the native `SNpcInfo` construction/loader contract.
2. Identify which existing runtime NPC is assigned type 997 in the starting map.
3. Trace that NPC's texture/model lookup.
4. Create a duck adviser variant at the same texture/model layer.
5. Keep type 997 and tutorial logic unchanged if possible.
6. Add portrait mapping separately where needed.
7. Only then convert the duck artwork into the game's `packed*.smf` texture format.
8. Build a separate test APK; keep the verified World Life 0.1 APK untouched.

## Outfit rule

The mayor duck uses the blue Japanese happi outfit from the approved character sheet. Future tutorial chapters use distinct outfit variants. Crown duck remains reserved for the player; no-crown duck remains reserved for staff.

## Current status

**Do not patch the APK yet.** The exact tutorial hook is recovered, but the runtime texture/model lookup must be identified first. This prevents the common failure mode where a new PNG exists in the APK but the native engine never references it.
