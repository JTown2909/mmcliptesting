# JP 1.0 credits warp: how it works, and a faster payload

> **Timing correction (read first).** Results below that say "VI" were measured with the emulator's frame
> callback, which fires once per **game frame** (20 fps in gameplay = 3 real VIs), not once per VI.
> Multiply those numbers by 3 for real 60 Hz VIs (more during scene loads). `tools/run_ace.py` now reads
> the game's own VI counter (0x80097B58). Re-measured with real VIs:
>
> | case (ACE at the same moment) | ACE -> scene change |
> |---|---|
> | night state 6, current names, looking down 8 game frames after the ACE | 237 VI (3.95 s) |
> | night state 6, new names `87SはぁヲBス` / `83Iどバb7え`, no look-down | **69 VI (1.15 s)**, saves 168 VI = **2.8 s** |
> | daytime state 6 (17:38), current names, look down within 62 game frames of the ACE | 399 VI (6.65 s) |
>
> Daytime look-down window: looking down any time up to ~186 VI (**~3.1 s**) after the ACE costs nothing;
> after that, each game frame late costs a game frame.

All addresses JP 1.0, verified on the runner's BizHawk savestates (QuickSave1-7) and by
emulating from QuickSave6 in mupen64plus (`tools/m64sim.py`).

## Execution chain
1. **SRM.** Link picks up a pot (`Obj_Tsubo`, instance 0x80419F10); the pot is destroyed while held,
   and `Obj_Moon_Stone` is later allocated over it (instance 0x80419E90). The stale reference leaves
   the Moon Stone's **draw** pointer (`+0x13C`, 0x80419FCC) = **0x80400A64**, an address inside
   Link's own Player struct (Link = 0x803FFFA0, so +0xAC4).
2. **Draw = code in Link.** The Moon Stone sits above Link (y = -44 vs Link y = -480), so it is only
   drawn when the camera looks up (C-Up then look up). Executing Player+0xAC4:
   ```
   80400A64  lb   s6, 0x5AC0(v1)
   80400A68  nop ; nop ; nop
   80400A74  j    (yaw << 16 | parallelYaw) -> 0x0814_2CA3 = j 0x8050B28C
   80400A78  00000800 (sll at, zero, 0 - harmless delay slot)
   ```
   `Player.yaw` (+0xAD4) = **0x0814** is the "0814 angle"; `Player.parallelYaw` (+0xAD6) = **0x2CA3**
   (set during the explosion step) supplies the low half of the jump target.
   Target = 0x80000000 | ((yaw & 0x3FF) << 18) | (parallelYaw << 2).
3. **Created file name** survives at 0x8050B28C (stale file-select data in a free heap block):
   `j 0x801EF48C ; xori a2, a0, 0xAA66` (a0 = Moon Stone actor, so a2 = 0x804134F6).
4. **Playing file name** (gSaveContext.save.saveInfo.playerData.playerName, 0x801EF48C; gSaveContext = 0x801EF460):
   `j 0x800ECD3C ; sb a2, 0x050D(a2)` writes 0xF6 to 0x80413A03 =
   `ovl_En_Test4` code + 0xF33 (`ori t4, zero, 0xFFF1` -> 0xFFF6), then jumps into
   `CutsceneCmd_SetTime` past its frame check, which is a leaf function, so it returns cleanly
   to Actor_Draw. Time = hour/minute bytes at a2+6 / a2+7.
5. Day 3, no ocarina, nextBellTime = 00:00: when En_Test4 sees the bell crossed it fades to the
   cutscene index it loads, now 0xFFF6 (ending).

## Why the original has to look down
Bytes at 0x804134FC/FD = (140, 234) -> 23:54. Every frame the Moon Stone is drawn, the time is reset to
23:54, so the runner must look down and let the clock run to midnight (~55 VI after looking down).

## Bell math -> instant trigger
En_Test4 fires when `(s16)(time - 0) * (s16)(prevBellTime - 0) <= 0`. prevBellTime is an evening
value (negative as s16), so **any time 00:00-05:59** fires on the very next update. 06:00+ would
instead hit the moon-crash transition, so stay below 06:00.

## New payloads (only the last-but-one character of each name changes)
| a2 | time set | created file (1st) | playing file (2nd) |
|---|---|---|---|
| current 804134F6 | 23:54 (must look down) | 87Sはぁヲヴス | 83Iどバb5え |
| **804132F6** | 00:01 | 87Sはぁヲ**B**ス | 83Iどバb**7**え |
| 804133F6 | 00:13 | 87Sはぁヲ**C**ス | 83Iどバb**6**え |
| 804124F6 | 00:04 | 87SはぁヲPス | 83Iどバbしえ |
| 80412CF6 | 01:05 | 87SはぁヲHス | 83Iどバbええ |

The time bytes for all four come from static overlay code (En_Test4 / Obj_Tokeidai) at fixed
addresses in this heap layout. `tools/find_time_payloads.py` lists every option.

## Emulated results from QuickSave6 (VI = 60 Hz frames)
| payload | ACE fires | scene change starts | notes |
|---|---|---|---|
| current, look down **8 VI** after the ACE (faster than a human can) | 73 | 152 | |
| 804132F6 (B / 7), keep looking up | 73 | **96** | no look-down needed |
| 804133F6 (C / 6), keep looking up | 73 | **96** | |

That saves at least 56 VI (~0.93 s), more in practice because the look-down input is gone entirely.
Both runs reach the same ending scene (Tatl/Tael "あっ！気がついた" text box) and keep running.

## Daytime ACE (setup done before 18:00) - tested on the second batch of savestates
Heap layout is identical (Moon Stone 0x80419E90, En_Test4 code 0x80412AD0, same draw pointer 0x80400A64).
Pot drop angle 0x0A64 is the low half of that draw pointer (high half 0x8040).

Bell logic on day 3 in daytime: nextBellTime is 17:30/17:36/.../17:54, and only becomes 00:00 after
the 17:54 bell. The warp only fires when a bell rings **while nextBellTime == 00:00**. Any jump past
18:00 first runs the night transition (title card), which returns early and skips the bell check.

Emulated from daytime QuickSave6 (17:38), ACE at VI 73:
| payload / situation | result |
|---|---|
| current names (23:54), look down at VI 81 | night flip VI 136, nextBell -> 00:00, midnight VI 184, **scene change VI 206** |
| new names (00:01), ACE before 17:54 | 17:36 bell rings with nextBell != 0 -> nextBell = 00:10 -> **never warps** |
| new names, clock moved so ACE lands 17:54-18:00 | scene change VI 159, then **emulator hangs** (game stops producing frames) - likely title card still up during the scene change; needs a BizHawk check |
| new names, ACE at night after the title card (first batch, 21-23h) | scene change VI 96, credits play normally |

Among typeable `xori`/`sb` variants, 23:54 is already the latest pre-midnight time, so for a daytime ACE
the current names are optimal within this payload shape.

### BizHawk confirmation (runner)
- TEST_A (night state 6 + new names): credits, no look-down needed. **Works.**
- TEST_B (daytime state 6, clock 17:49, new names): **crashes** (red crash line). The 17:54-18:00 window is not usable.

## Pot drop angle tolerance
Link's yaw while holding the pot is written into the low half of the stale draw pointer (0x8040_yyyy).
Emulated from TEST_A with the draw pointer forced to each value:

| drop angle | result |
|---|---|
| 0x0A40, 0x0A4C | crash |
| **0x0A50, 0A54, 0A58, 0A5C, 0A60, 0A64, 0A68, 0A6C, 0A70, 0A74** | ACE + credits |
| 0x0A78 | crash (starts after the jump) |

Every working angle lands in the run of zero words (nops) in Link's data at Player+0xAB0..0xAD4 that
leads into the yaw/parallelYaw jump. The angle must be a multiple of 4: an unaligned value (0x0A62)
happened to work in mupen64plus, but real hardware raises an address error, so don't rely on it.
These Player fields were zero in every savestate checked, but they are live game data.

## Route constraint: ACE in the afternoon (WR finishes setup ~16:00)
- With the `sb` + `CutsceneCmd_SetTime` payload, every reachable a2 (low byte F6, within +-0x8000 of the
  patch byte, any register/opcode) was checked: **23:54 (the current names) is the only time >= 23:49**.
  For a daytime ACE the current names are optimal; improving further needs a different payload type.
- Jumping straight into En_Test4's own warp block is not viable: it loads play/this/player from its own
  stack frame (0x54/0x50/0x4C(sp)), which doesn't exist when entered from a draw call.
- **Look-down window** (daytime QuickSave6, ACE at VI 73): looking down at VI 81, 120 or 135 all give the
  scene change at VI 206. At VI 145 -> 217 and VI 160 -> 232. The clock doesn't move during the night
  card anyway, so there is ~60 VI (~1 s) after the ACE to look down at no cost.

## Angle mechanics (measured in emulation, game frames = 20 fps)
Angles are u16 (0x10000 = 360°). Measured on the runner's daytime QuickSave4 (holding pot), QuickSave5
(2CA3) and night QuickSave5 (2E1C after the explosion) with `tools/input_probe.py`.

**Standing (normal camera) turns**
- Target = camera input yaw + stick direction. Link's shape steps toward it by **0x708 per game frame**
  and snaps exactly onto it once within 0x708. `Player.yaw` (+0xAD4) jumps to the target on the first frame.
- A **1-frame** light-stick tap does nothing; a **2-frame** tap turns exactly one 0x708 step.
- Cardinal ESS directions are exact: in QuickSave4 the camera input yaw is 0x2AAB (60°), and ESS
  up/right/left/down target 2AAB / EAAB / 6AAB / AAAB. In QuickSave5 the camera is 0x2CAB.
- Standing turns do **not** change parallelYaw (+0xAD6).
- Ruled out: from 2AAB/2AAC, no combination of cardinal snaps (c × 0x4000) and 0x708 steps reaches any
  valid drop angle (0A50-0A74). The runner's method for A64 must involve something else; ask them.

**First-person turns (C-Up)**
- An isolated tap from rest turns -(x - 8) × 16 per frame for stick x = 9..26 (x = 10 -> -0x20,
  15 -> -0x70, 20 -> -0xC0), capped at **300 (0x12C)** for x >= 27. Stick right = yaw decreases.
- Holding the stick **accelerates** the turn (after ~20 frames: -460, -660, -960 per frame), and the turn
  keeps its momentum after the stick is eased (x = 9 kept turning 300/frame). Only isolated taps from
  rest are predictable.
- First-person turns do not change parallelYaw. **First person is unavailable while holding the pot.**
- Multiples of 16, plus 300 (≡ 12 mod 16), can produce any multiple of 4, so first person can never
  change an angle's value mod 4.

**Why the explosion is probably in the 0814 setup**
2CA3 ≡ 3 (mod 4) but 0814 ≡ 0 (mod 4). Standing turns snap to (camera yaw + stick angle); in
QuickSave5 the camera is 0x2CAB ≡ 3, so cardinal snaps stay ≡ 3, first person preserves the class, and
Z-targeting into empty space left the camera at 2CAB. The bomb knockback sets yaw = 2E1C (≡ 0) **without
touching parallelYaw (2CA3)**, which moves Link into the right class for 0814. (Inferred from the
arithmetic; the runner should confirm.) An attempt to plan 2E1C -> 0814 frame-exactly in first person
overshot because of the turn acceleration.

### ESS rotation (runner's method) - confirmed
Rotating the stick through the ESS range keeps the target ahead of Link, so he turns exactly 0x708 per
game frame without snapping. Emulated with the stick steered 45° ahead of Link each frame:
- Pot drop: from 2AAC (daytime QuickSave4), **41 steps clockwise -> 0A64** (2AAC - 41 × 0x708 mod 0x10000).
- 0814: from 2E1C (night QuickSave5), **31 steps counterclockwise -> 0814**, parallelYaw stays 2CA3.
- A search over one optional snap to an ESS cardinal (camera 2AAB at the drop, 2CEB at 0814) plus
  n steps either way finds nothing shorter. The 0x708 grid from 2AAC only reaches A64 among the 10
  valid drop angles. One step per game frame is the maximum turn rate, so both turns are already
  optimal from these starting angles. Shorter turns would need a different starting angle (another
  wall snap with a suitable value mod 8).
- 0814 ≡ 4 (mod 8) and every step is ≡ 0 (mod 8), so the base angle must be ≡ 4 (mod 8). 2CA3 and the
  camera (2CEB) are ≡ 3, while the explosion's 2E1C is ≡ 4. That's why the explosion is in the setup.

## Full setup traced from the runner's movie (`.bk2`, daytime, from QuickSave2 to credits)
Replayed with `tools/bk2replay.py --offset -1` (BizHawk logs one input row per VI; offset -1 stays in sync:
same pot address, same A64 / 2CA3 / 2E1C / 0814 and the ACE all reproduce). `--heaplog` records every
actor-heap allocation/free. Frames = game frames (20 fps); VI = 60 Hz from the movie start.

### Heap manip: what each part does
| frame (VI) | event | effect |
|---|---|---|
| 174-212 (507-621) | pots broken, items spawn and despawn | frees space around 0x80416A00-0x80416F00. **Runner tested: not needed**, the setup works without it |
| 256-420 (753-1245) | two trips into the torch room and back | rooms load/unload; the heap reshuffles. **Runner confirmed: needed** |
| **443 (1314)** | **explosion 1**: its effect actor En_Clear_Tag (0x2E90 bytes) sits at 0x80416E90-0x80419D50 | while it exists, re-entering the pot room (frame 501) spawns the **target pot at node 0x80419EE0** (data 0x80419F10) instead of lower |
| 513 (1524) | explosion 1 effect ends | that space is freed |
| **777 (2316)** | **explosion 2**: En_Clear_Tag at 0x80414870 | the free block below the pot now starts exactly at **0x80417730** |
| 796-808 (2373-2409) | carry the pot into the torch room | the new room loads 2 × En_Water_Effect, En_Light and 4 × Obj_Syokudai into 0x80417730+, leaving exactly **0x80 bytes free** in front of the pot; the old room unloads, so the **held pot is freed (SRM)** |
| 854 (2547) | back in the pot room | **Obj_Moon_Stone spawns at node 0x80419E60** (the 0x80 gap + the freed pot), i.e. exactly 0x80 before the pot. The stale held pot writes Link's yaw to pot+0xBE = Moon Stone draw pointer + 2 |

Requirement for any alternative manip: **Moon Stone instance = held-pot instance - 0x80** (with the Moon
Stone code still loaded at 0x8040xxxx). Then recompute the names from the Moon Stone address
(`find_time_payloads.py` takes a0 and the patch address as arguments).

### Where the setup time goes: ESS rotations are done in bursts
| turn | steps (0x708 each) | time in the movie | back-to-back minimum |
|---|---|---|---|
| pot drop 2AAC -> 0A64 (clockwise) | 41 | frames 996-1211 = **10.7 s** (bursts of ~10 steps, ~20-frame pauses) | 2.05 s |
| 2CA3: fence angle D563 -> 2CA3 (clockwise), then Z sets parallelYaw | 24 | frames 1294-1404 = **5.5 s** | 1.2 s |
| 0814: 2E1C -> 0814 (counterclockwise) | 31 | frames 1625-1725 = **5.0 s** | 1.55 s |

That's 21.2 s of turning versus 4.8 s if every frame were a step. Link turns one step per frame as long
as the stick direction stays more than one step (~9.9°) ahead and less than 180° ahead of him. So the
stick can be swept faster than Link turns; the only real constraints are never letting it fall within
~10° of Link (that causes a snap) and stopping on the right step. A realistic approach is a fast sweep for
most of the turn, then slower single steps for the last few.

Other waits seen: about 3.5 s between the bomb and the explosion hit (frames 1501-1571), and 2.7 s
between the hit and starting the 0814 turn (frames 1571-1625).

## Heap simulator (`tools/heapsim.py`) - validated against the movie
Exact model of the JP 1.0 actor heap:
- **Allocator (decomp `__osMalloc.c`):** first-fit `malloc` from the head; `mallocR` from the tail
  (carves the end of a block); a block is split only if size + 0x30 < block size; `free` merges with
  adjacent free neighbours.
- **Actor spawn:** actor code (overlay) via `malloc`, or `mallocR` for ALLOCTYPE_PERMANENT (En_Door,
  En_Holl, En_Bom), unless already loaded; then the instance via `malloc`. Code is freed when its last
  instance dies (never for permanent).
- **Sizes and alloc types** come from the game's actor overlay table (JP 1.0 RAM 0x801A9E60, 0x20 bytes per
  actor; found through Obj_Moon_Stone's overlayEntry pointer 0x801AEEC0) plus each actor's profile in the
  ROM: `tools/actorinfo_jp10.pkl`.
- **Room actor lists** read from the ROM (`tools/romfiles.py`, Yaz0 + dmadata at ROM 0x1C110): torch room =
  file 1295, pot room = file 1296. Rooms spawn their actors in list order.

Quirks found, each needed to match real RAM:
- Every room spawns its own **En_Test4**, which deletes itself on its first update (only one may exist).
  While it lives (0x160 bytes) it occupies a hole, so later actors in the same load go elsewhere.
- Entering the pot room **through the door re-spawns the En_Door instance before the room's actors**.
  The door belongs to the pot room and is freed when it unloads.
- **Memory leak:** every pot-room load allocates 2 × 0xB0 bytes right after En_Kakasi that are never freed.
- The first pot-room re-entry also allocates 0x520 and 0x420 bytes from the top of the heap, never freed
  (source unknown; modelled as raw allocations).
- Bombs are owned by the room they're pulled in and are freed when it unloads, unless carried or exploded.
  An explosion spawns En_Clear_Tag (0x5FA0 code + 0x2E84 instance) until it ends.

**Validation:** `tools/route_check.py` replays the movie's events from the frame-255 heap and matches the
real heap **exactly at all 22 checkpoints** (three torch-room loads, four pot-room loads, unloads, 3
explosions, bombs), ending with the Moon Stone at node 0x80419E60.

**What the simulator says about the setup** (`tools/route_search.py`, starting from frame 255):
- Removing either torch-room trip -> fails (matches the runner's test).
- Removing any of the three explosions -> fails.
- Pulling 1 instead of 2 bombs in the pot room, or 0-2 instead of 3 bombs in the torch room -> fails.
- Destroying the second pot before carrying the first -> **not needed** (works either way).
- A search over first trip on/off, bombs per room (pot 1-4, torch 0-5), each explosion overlapping a room
  load or not, and which pot is carried found **only the movie's structure** working.
- **Unresolved:** the simulator predicts that skipping the early pot breaking (frames 172-212) changes the
  result. With the pots alive, their code is still loaded when the torch room first loads, so the torch
  room's pots don't allocate it again and everything shifts (target pot 0x80419F40, not 0x80419EE0). The
  runner reports the setup still works without the pot breaking. A movie of that variant is needed to settle it.

## New setup: parallelYaw 2CA1 (instead of 2CA3), then yaw 0814
**Why 2CA3 can't simply become 2CA1:** ESS steps are 0x708 (≡ 0 mod 8), so they never change an angle mod 8.
The fence snap D563 ≡ 3 (mod 8) like 2CA3, but 2CA1 ≡ 1. The fix is a camera snap: tap Z (the camera
re-centres behind Link), then ESS up, and Link snaps to a camera-favoured angle that is 2 lower.

**Routes from the fence snap (D563), verified in emulation** (from the movie, frame 1268, right after the fence Z;
`tools/ess_plan_test.py`). parallelYaw ends at exactly 2CA1 whether the wait after Z is 6, 15 or 30 frames:
| route | inputs | steps |
|---|---|---|
| **A** | ESS right ×12 (-> 8103) · tap Z · ESS up (-> 8101) · ESS right ×12 (-> 2CA1) · Z | 24 + Z + ESS up |
| **B** | ESS right ×25 (-> 259B) · tap Z · ESS up (-> 2599) · ESS left ×1 (-> 2CA1) · Z | 26 + Z + ESS up |
(The current route is ESS right ×24 -> 2CA3 · Z.) ESS up **without** a Z tap first doesn't work: the camera
doesn't follow Link during ESS turns, so Link snaps back toward the old camera direction (D567).

**Other wall-snap angles in the basement** (runner-measured: D563, 5554, 2AAC, D4D1, 1526, 54D1, 0000, D554,
5572; all of them also come out of the collision data with the exact game atan, `tools/mm_atan.py`): searched with
`tools/angle_search.py` (motion model from rylieb/mm-angle-finder). None beat the fence. The next best are
D554 (ESS right ×4 · Z+ESS up · ESS right ×8 · Z+ESS up · ESS right ×12) and D4D1. The rest need many camera snaps or C-up.

**0814 afterwards is unchanged.** The movie was replayed with Link's angles and parallelYaw set to 2CA1 just after
the fence Z (frame 1422). The runner's own bomb inputs still produce the knockback yaw **2E1C**, the recorded
31 counterclockwise ESS steps still reach **0814**, and parallelYaw stays **2CA1**. (With the old file names
the ACE then jumps to 0x8050B284 and hits the "ZELDA3" header bytes, as expected for the new setup's
different target.) No explosion-free alternative exists: after parallelYaw is set, only par-preserving
moves (ESS steps ≡ 0 mod 8, C-up ±0x3C0) are allowed, and a Z re-centre would overwrite parallelYaw, so
nothing but the knockback can move yaw from ≡ 1 to ≡ 4 (mod 8).
