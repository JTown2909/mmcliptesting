# JP 1.0 credits warp: how it works, and a faster payload

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
