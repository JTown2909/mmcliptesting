# Chest-minigame counter clip: new setups (emulator-verified)

All setups start on room entry (Deku, x=-70, z=209.75, facing 0000, camera 0000) and end with
the usual finish: hold Z, hold Up for `4 + walk` frames, then press A (with Up) to spin.
Every setup here was replayed frame-by-frame in the emulator (JP 1.0) and clips.

Notation (same procedures as imbued's `test-cmg-solution.lua`):
* **ESS Lx/Rx n** – tap Z (camera behind Link), release, then n ESS turns left/right.
* **Tap d** – tap Z, release, wait for the camera to settle, then tilt the stick to notch d for
  exactly **one frame** (U, UL, L, DL, D, DR, R, UR, camera-relative). Holding it 2 frames moves
  Link 3.75 units. imbued's "cardinal turn down" is `Tap D`.
* **Backflip / SidehopL / SidehopR / ScootFwd** – exactly as in imbued's setup (targeted, held).
* **Spin d** – Deku spin held toward notch d: from standstill (camera settled), press A and the
  stick direction together (same frame, or stick ≤1 frame after A), keep holding the stick, then
  shield. **Spin dt** – tap the direction 1 frame first, then A + direction on the next frame.
  Shield timing (0–8 frames late), hold length and the wait before the spin do not matter.
* **SpinInPlace xn** – imbued's in-place spin, n times.

## Best by estimated time

### A — 5 ESS taps, walk 29 (vs imbued: 18 ESS taps, walk 59)
| step | x | z | facing | camera |
|---|---|---|---|---|
| Tap DL, ESS Lx3 | -70.000000 | 209.750000 | 7518 | 6008 |
| Backflip | -95.540558 | 303.066040 | 7518 | 751D |
| Tap D, ESS Lx1 | -95.540558 | 303.066040 | FC25 | F51E |
| Spin U | -108.656738 | 452.456146 | FC90 | FCA0 |
| Tap U | -108.656738 | 452.456146 | FCA0 | FCB0 |
| Spin UR | -239.612808 | 518.367615 | C6CB | C6C3 |
| Tap L | -239.612808 | 518.367615 | 06C3 | 06C1 |
| ScootFwd | -238.622543 | 524.285217 | 06C3 | 06C1 |
| ESS Rx1 | -238.622543 | 524.285217 | FFBB | 06C1 |
| hold Z+Up 33 frames, A | → clip | | | |

### B — 2 tap turns, 13 ESS taps, walk 37
Tap L + ESS Lx4 | Backflip | ESS Lx1 | Spin Rt | Tap D | Spin Lt | ESS Lx6 | ScootFwd | ESS Rx2
(end -237.691605, 452.251312, facing FFAA; hold Z+Up 41 frames, A)

See `verified_setups.txt` for all 87 verified setups with ESS/tap/spin counts.
Time estimates use guessed per-input costs (ESS group 0.6 s + 0.25 s/tap, tap turn 1.2 s,
in-place spin 1.3 s, spin/sidehop/scoot/backflip ~0.6–1.3 s, walk at 20 fps) and are only for ranking.

### C — 2 ESS taps, walk 30
Tap D | Backflip | Tap UR | Spin Dt | Tap UR + ESS Lx1 | ScootFwd | Tap D + SpinInPlace x1 | Spin R | Tap UL + ESS Lx1

### D — 1 ESS tap, walk 48
Tap UL + SpinInPlace x1 | ScootFwd | Tap L + SpinInPlace x1 | Backflip | SidehopR | Tap DL + ESS Lx1 | Spin U | Tap L + SpinInPlace x2

## Videos (`videos/`)
Top-down replays from the emulator (exact per-frame position, facing and camera over the room's
wall geometry, current step labelled): `counter_setupA.mp4`, `counter_setupB.mp4`,
`counter_setupC_2ess.mp4`, `counter_setupD_1ess.mp4`, and `counter_imbued.mp4` for comparison.
Frame counts in these videos include the scripted camera-settle waits from imbued's lua
procedures, so they are not a measure of human execution time.

## Shield-method caveat (needs checking on console)
In the emulator, holding R as Deku does not turn Link; after R is released with the stick held,
Link turns 2 frames later and starts walking on the 3rd. A spin started by "prehold direction with
shield, release shield + A" does **not** land on the same position as the scripted spin (A + stick
from standstill, camera settled): the result changes with the number of frames between the R
release and A (tested 1–4 frames, all different, none equal to the scripted spin). Tap turns done
via shield give the same facing as the 1-frame flick as long as the stick is released before Link
starts walking.
