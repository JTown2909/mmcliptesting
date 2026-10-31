# Laundry Pool / Counter clip research – status

All numbers are for JP 1.0, Deku Link, read from mupen64plus running the kz-lite
ROM with the user's kz states (see `emu/`).

## Laundry Pool clip

* Corner: north alley wall `z = 435` (x ≥ -1431, faces -z) meets the diagonal wall
  `(-1431,435) → (-1653,341)` (faces (0.39,-0.92)).  Behind the vertex is the
  wall `x = -1431` (z ≥ 435) that faces **-x**.
* MM's wall code does two passes (walls facing z, then walls facing x) and pushes Link
  even when he is up to his wall radius (14) *behind* a plane.  If one movement step
  lands Link (before collision) inside a tiny triangle at the vertex, the back wall
  `x = -1431` pushes him 14 units to x = -1445 – behind both front walls.
* Landing target (pre-collision position on the clip frame), measured by teleport:
  `x ∈ [-1431.00, -1431.00 + 0.12·(z − 434.05)]`, `z ∈ [434.05, 435.0]`
  (≈ 0.1 × 1 unit).  The spin's 2nd/3rd frame (step ≈ 13–15) is what reaches it.
* Reproduced the video's clip exactly: spin frame state
  `x=C4B313CE y=C117662B z=43D1BA1E`, shape 9754, movement yaw 0x474 → next frame
  `x=-1445.0 z=434.24` (matches `C4B4A000 … 43D91F59` in the video).
  Movement yaw window at that position: 0x470–0x480; position window ≈ 0.1 unit.
* Setup replay from room entry matches the video bit-for-bit up to C4B538B4
  (ESS right to 706E, Z, wait, left 10 frames, right 15 frames).  The stop at
  C4B3A704 was not reproduced (Link keeps decelerating to C4B38660 instead).

## Counter clip (Treasure Chest Shop)

* Corner: pillar front `z = 840` (x ≤ -240, faces -z) meets the counter's left
  diagonal `(-240,840) → (-175,811)`.  Behind: pillar east face `x = -240` (faces +x).
* Landing target by teleport: `x = -240.00` (window < 0.01), `z ∈ [839.1, 839.6]`.
  Room is axis aligned and the camera starts at yaw 0, so straight +z runs keep x exact.

## Searches run (no new clip found yet)

* Hold one notch from entry (± Z reset), A on frames 1–70: 0 real clips.
* 130 deterministic anchors (ESS turns to notches + Z resets, depth 3) × 8 notches,
  A on every distinct frame within 40 units of the corner at speed ≥ 5
  (763 spin attempts): 0 clips.
