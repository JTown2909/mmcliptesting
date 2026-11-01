# Majora's Mask JP 1.0 credits-warp research: guide for AI agents

Goal: make the any% credits warp (filename ACE) faster in **real time** for runners.
Read `docs/credits_warp.md` first: it has the full mechanism, every result so far, and what was ruled out.
This file explains how to work in the repo: setup, where the data is, and how to test ideas.

## What is not in the repo (ask the user)
- The ROM: *Zelda no Densetsu - Mujura no Kamen (Japan)*, JP 1.0, `.z64`, MD5 `15d1a2217cad61c39cfecbffa0703e25`.
- BizHawk 2.11 savestates (Mupen64Plus core) from the runner. Two batches exist:
  - **Batch 1, night (~21:00-23:00):** QuickSave1 = before entering the observatory, 2 = just inside,
    3 = after the heap manip, 4 = after getting SRM (holding the stale pot), 5 = after the explosion hit,
    6 = at angle 0814 just before C-Up, 7 = file select after typing the 2nd name.
  - **Batch 2, day 3 afternoon:** QuickSave2-6 for the same steps; 6 is at 17:38. In this batch,
    state 5 is just before turning from 2CA3 to 2E1C.
  - States, ROMs, RAM dumps and videos are gitignored. Never commit them.
- Decomp for reference: https://github.com/zeldaret/mm (the **US** build). JP 1.0 differs; see below.

## Environment setup (Linux container)
```bash
tools/setup_env.sh          # apt packages, builds tools/scriptinput/scriptinput.so, starts Xvfb :99
export DISPLAY=:99 SDL_AUDIODRIVER=dummy
```
- `m64sim.py` uses the **rice** video plugin, because glide64mk2 renders black screenshots under Xvfb.
- If emulator runs print nothing, Xvfb has probably died. `pgrep -a Xvfb`; clear `/tmp/.X99-lock`
  and `/tmp/.X11-unix/X99` **only after killing** the old server, then restart it.
- Pipe output through `grep --line-buffered`, or write to a file. Plain `grep | head` buffers output,
  and a `timeout` kill then loses all of it, which looks like a hang.

## Tools (all in `tools/`)
| tool | use |
|---|---|
| `bizstate.py` | Read/patch BizHawk `.State` files. RDRAM is at Core.bin offset 0x1C0, stored as little-endian 32-bit words. `.m64p(path)` writes a gzip m64p state that mupen64plus can load. `.save(path)` writes a patched `.State` back for the runner to try in BizHawk. |
| `m64sim.py` | Headless mupen64plus driver: load a state, set controller input every game frame, read/write RAM, take screenshots. |
| `run_ace.py` | Ready-made scenario: load a state, press C-Up, look up, and report the ACE frame, En_Test4 bell state and scene-change frame. Can override the names, time and drop angle, and when to look down. |
| `heapscan.py` | Walk the actor heap in a big-endian RDRAM dump; labels actors and their code overlays. |
| `find_time_payloads.py` | Enumerate typeable `xori`/`sb` name pairs and the clock time each one sets. |
| `actor_names.py` | Actor ID -> name table (from the decomp). |
| `mm_ace_watch.lua` | BizHawk Lua heap viewer + Link angle watches, for the runner. |
| `m64run.py`, `kzs.py` | Old: RDRAM dump at a frame from boot; kz-lite state decoder. |

Getting a RAM dump from a BizHawk state:
```python
from bizstate import BizState; import struct
st = BizState("QuickSave6.State"); raw = bytes(st.core[0x1C0:0x1C0 + 0x800000])
w = struct.unpack("<%dI" % (len(raw) // 4), raw); be = struct.pack(">%dI" % len(w), *w)  # N64 byte order
```

Example: test a name pair from a state:
```bash
python3 tools/run_ace.py ROM.z64 QuickSave6.State --name1 0807BD233886AC66 --name2 0803B34FA0C6070D --frames 300
```
`run_ace.py` prints both "frame" (emulator callback = one **game frame**, 20 fps in gameplay) and "VI"
(real 60 Hz, from the game's VI counter at 0x80097B58). **Compare using VI.** "scene change" is when the
credits scene load starts. Compare candidates against the same state and the same input (the default
input fires the ACE at game frame 73).
- Pitfall: the m64p frame callback is NOT per VI. Old numbers labelled "VI" in docs/credits_warp.md are
  game frames (see the correction box at the top of that file).

## JP 1.0 facts (verified on the runner's states)
- gSaveContext = 0x801EF460 (time +0x0C, isNight +0x10, day +0x18, playerName +0x2C = 0x801EF48C).
  Fields past `Save` are offset differently from the US decomp. JP `nextCutsceneIndex` is written with
  `sh t4, 0x42D6(t2)`, i.e. gSaveContext+0x42D6. The skyboxTime candidate is 0x801F373E.
- Heap (actor arena) nodes are **0x30 bytes** in JP (0x10 in US). Head 0x803FFF70; Link = 0x803FFFA0.
- Player offsets matched the US decomp where checked: yaw +0xAD4, parallelYaw +0xAD6, heldActor +0x34C,
  stateFlags1 +0xA6C, shape.rot.y +0xBE, world.rot.y +0x32.
- Route heap layout (same in both batches): ovl_En_Test4 code 0x80412AD0, En_Test4 instance 0x80414540,
  Obj_Moon_Stone instance 0x80419E90 (draw ptr at +0x13C = 0x80419FCC).
- Name charset (byte -> character) is in `find_time_payloads.py` (`JP`): 0x00-0x09 digits, hiragana,
  small/voiced hiragana, katakana (+ヴ), A-Z = 0xAB-0xC4, a-z = 0xC5-0xDE. A byte is only typeable if
  it is <= 0xDE. This mapping reproduces the runner's current names exactly.
- Day 3 bells: daytime 17:30/36/42/48/54, then 00:00. The warp only fires when a bell rings **while
  nextBellTime == 0**. Crossing 18:00 runs the night transition first, which returns early.

## Verified results (details in docs/credits_warp.md)
- Afternoon ACE (the real route; WR finishes the setup around 16:00): current names `87Sはぁヲヴス` /
  `83Iどバb5え` are optimal for the `sb` + `CutsceneCmd_SetTime` payload type. The runner has about 3.1 s
  (~186 VI) after the ACE to look down at no cost.
- Night ACE: `87SはぁヲBス` / `83Iどバb7え` set 00:01; the scene change starts 69 VI (1.15 s) after the ACE, 2.8 s sooner than the current names (runner confirmed it works in BizHawk).
- ACE in the 17:54-18:00 window with the night names: crashes (runner confirmed).
- Pot drop angle: 0x0A50-0x0A74 in steps of 4 all work in emulation (it must be a multiple of 4).

## How to look for improvements
1. Form a hypothesis from the decomp (US source, then confirm JP addresses in RAM or with capstone).
2. Check it on the runner's state with `run_ace.py` or a custom `m64sim` script. Read RAM rather than
   relying on screenshots; take screenshots only to confirm a scene.
3. If "alive" stops printing, the game hung. Treat that as a crash.
4. For anything promising, write a patched `.State` with `bizstate.py` (`TEST_*.State`) and ask the runner
   to try it in BizHawk. Emulator behaviour can differ from real hardware: mupen64plus accepted an
   unaligned jump that hardware would reject.
5. Record every result, good or bad, in `docs/credits_warp.md`.

## Open directions
- **Angle setups:** faster ways to reach a valid pot drop angle (any of 10), and 0814 / 2CA3
  (wall snap + ESS turns). The runner's setup videos show the current method.
- **Heap setup:** which steps of the heap manip are actually needed to put Obj_Moon_Stone at 0x80419E90
  (compare QuickSave2 -> 3 -> 4 heaps with `heapscan.py`).
- **Name typing cost:** map the JP keyboard layout (`ovl_file_choose/z_file_nameset_JPN.c`) to choose,
  among equivalent payloads, the one that is fastest to type.
- **A different payload type** for an afternoon ACE (one that avoids the night card + midnight wait).
  Not yet worked out.
