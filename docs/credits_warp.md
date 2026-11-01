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
