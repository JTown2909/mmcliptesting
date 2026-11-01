# Chest-minigame counter clip: setups for the console method (emulator-verified)

All setups start on room entry (Deku, x=-70, z=209.75, facing 0000) and end with the usual finish:
hold Z, hold Up for `4 + walk` frames, then A (with Up). Every setup below was replayed in the
emulator with the console inputs described here and clips; `videos/` has real game footage of each.

## Inputs

* **Tap d** – shield turn: target/untarget and let the camera settle, then shield, hold notch d,
  release shield (Link turns without moving), re-shield within ~2 frames. Same facing as a 1-frame flick.
* **HSpin d** – shield spin: camera settled, hold shield, hold notch d, release shield, press A
  **one frame after** the release (A on the release frame does not spin; 2 frames later gives a
  different result), keep holding d and re-shield within 15 frames of A.
  Only U / UL / L / UR / R are used: DL/DR sit exactly on the brake threshold and D always brakes.
* **ESS Lx/Rx n**, **Backflip**, **SidehopL/R**, **ScootFwd**, **SpinInPlace xn** – as in imbued's setup.

## S1 — 1 ESS tap, 4 in-place spins, 1 shield spin, walk 48 (`videos/game_counter_1ess.mp4`)

| step | x | z | facing |
|---|---|---|---|
| Tap UL + SpinInPlace x1 | -70.000000 | 209.750000 | 1E20 |
| ScootFwd | -65.953979 | 214.180359 | 1E20 |
| Tap L + SpinInPlace x1 | -65.953979 | 214.180359 | 5C47 |
| Backflip | -140.322784 | 276.065277 | 5C47 |
| SidehopR | -86.113518 | 341.210022 | 5C47 |
| Tap DL + ESS Lx1 | -86.113518 | 341.210022 | C34F |
| HSpinU | -235.600510 | 353.169128 | C342 |
| Tap L + SpinInPlace x2 | -235.600510 | 353.169128 | FF82 |

Then hold Z + Up for 52 frames and press A.

## S2 — 7 ESS taps, 2 in-place spins, 1 shield spin, walk 47 (`videos/game_counter_S2_7ess.mp4`)

| step | x | z | facing |
|---|---|---|---|
| Tap DL + SpinInPlace x2 | -70.000000 | 209.750000 | 5C40 |
| Backflip | -144.368805 | 271.634918 | 5C40 |
| Tap D + ESS Lx2 | -144.368805 | 271.634918 | EA57 |
| HSpinU | -220.343445 | 400.929138 | EA5C |
| ESS Rx1 | -220.343445 | 400.929138 | E354 |
| Backflip | -157.776459 | 327.136108 | E354 |
| Tap DR + ESS Lx2 | -157.776459 | 327.136108 | 916A |
| SidehopL | -234.919724 | 362.223816 | 916A |
| Tap DL + ESS Lx2 | -234.919724 | 362.223816 | FF76 |

Then hold Z + Up for 51 frames and press A.

## S3 — 11 ESS taps, no in-place spins, 1 shield spin, walk 48 (`videos/game_counter_S3_11ess_nosip.mp4`)

| step | x | z | facing |
|---|---|---|---|
| Tap DL | -70.000000 | 209.750000 | 6000 |
| ScootFwd | -65.760803 | 205.504211 | 6000 |
| Tap L + ESS Rx1 | -65.760803 | 205.504211 | 9900 |
| ScootFwd | -69.218491 | 200.600861 | 9900 |
| Tap DR + ESS Rx2 | -69.218491 | 200.600861 | 2AF8 |
| SidehopR | -111.028343 | 274.317078 | 2AF8 |
| Tap DR + ESS Rx4 | -111.028343 | 274.317078 | AEDA |
| HSpinUL | -234.823029 | 353.273163 | E352 |
| ESS Lx4 | -234.823029 | 353.273163 | FF72 |

Then hold Z + Up for 52 frames and press A.

## S4 — 9 ESS taps, 2 in-place spins, no shield spins, walk 64 (`videos/game_counter_S4_9ess_nospin.mp4`) — **confirmed on console**

| step | x | z | facing |
|---|---|---|---|
| Tap UR + ESS Rx1 | -70.000000 | 209.750000 | D8F8 |
| ScootFwd | -74.908661 | 213.200165 | D8F8 |
| ESS Lx4 | -74.908661 | 213.200165 | F518 |
| ScootFwd | -76.492569 | 218.987213 | F518 |
| Tap DL + SpinInPlace x2 | -76.492569 | 218.987213 | 515E |
| Backflip | -164.620789 | 258.907227 | 515E |
| ESS Lx3 | -164.620789 | 258.907227 | 6676 |
| SidehopL | -233.275345 | 209.219086 | 6676 |
| Tap DR + ESS Rx1 | -233.275345 | 209.219086 | FF71 |

Then hold Z + Up for 68 frames and press A.

`verified_console_setups.txt` lists all 301 emulator-verified setups for this method
(columns: ESS taps, in-place spins, tap turns, walk, rough time estimate, shield spins).

## Superseded
Setups A–D in the previous version used a scripted spin (A + stick from standstill) that differs
from the console shield spin; they do not work with the console method.

## No ESS, no diagonals (exhaustive to 6 moves)
Turns limited to cardinal shield turns + spins in place (≤4 per turn); moves = sidehops, scoot,
backflip, shield spins U/L/R, back-wall pin. Nothing exists with ≤4 moves; with 6 moves 575 setups
pass the exact check, 14 of the top 61 clip in the emulator. Best (6 moves, 7 spins in place,
3 shield spins, walk 44, `videos/game_counter_S5_noess_nodiag.mp4`):

Tap L + SpinInPlace x1 | SidehopR | Tap L + SpinInPlace x1 | HSpinL | Tap L + SpinInPlace x2 | ScootFwd |
Tap L + SpinInPlace x2 | Backflip | HSpinU | Tap L + SpinInPlace x1 | HSpinL | Tap U → hold Z+Up 48 frames, A.

Without ESS the facing can only be adjusted in 0x1E0 steps (spin in place), so these are much slower
than S4. A cardinal-only SE corner pin was tested and is not reliable (Link stops against the east
wall instead of sliding to the corner for some facings).

## Guano scoots, at most one ESS step, no diagonals (exhaustive to 4 moves)
Moves: sidehops, scoot, backflip, shield spins U/L/R, guano shield-scoot chains of 1–6 (L/R, chain
reset before each), back-wall pin; turns: cardinal shield turns, spins in place ≤4, at most one ESS
step. 33 setups pass the exact check, 8 clip in the emulator (guano scoots depend on the exact
facing/camera relation, which the per-16-unit table does not capture, hence the low hit rate).
Best (`videos/game_counter_S6_guano_1ess.mp4`, walk 49 → hold Z+Up 53 frames, A):

| step | x | z | facing |
|---|---|---|---|
| Tap R + SpinInPlace x1 | -70.000000 | 209.750000 | BE20 |
| SidehopL | -73.661171 | 294.419006 | BE20 |
| SpinInPlace x2 | -73.661171 | 294.419006 | BA60 |
| GuanoR2 | -96.324730 | 275.486877 | BA60 |
| Tap L + SpinInPlace x1 | -96.324730 | 275.486877 | F890 |
| GuanoR5 | -159.187225 | 309.521637 | F890 |
| GuanoR6 | -237.029129 | 344.297516 | F890 |
| Tap U + ESS Lx1 | -237.029129 | 344.297516 | FFA7 |

13 guano scoots + 4 spins in place: not faster than S4.

## Everything except diagonals (unlimited ESS, guano scoots, shield spins, spins in place) — exhaustive to 4 moves
6897 setups pass the exact check; the 204 fastest/shortest were replayed in the emulator (71 clip), and
the 60 fastest near-misses were re-searched from the emulator's exact state after 2–3 moves (5 more clip).
Ranked by estimated time and step count (each guano scoot and each spin in place = 1 step), imbued's
setup (9 steps, walk 59) is still first. The best new no-diagonal setup that clips:
Tap R + ESS Rx6 | SidehopL | SpinInPlace x2 | SidehopL | GuanoL1 | SpinInPlace x2 | ScootFwd | Tap L + ESS Lx7
(12 steps, walk 55). All verified setups: `verified_nodiag_setups.txt`.
