"""Per facing bin, measure in the emulator:
  turns: facing after a tap turn in each of 8 notches (target/untarget/settle, tap, settle) and ESS sanity;
  moves: per-frame (speed, movement angle) for each move, and the facing afterwards.
Output: one JSON line per bin."""
import sys, json, struct; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
part, nparts = int(sys.argv[1]), int(sys.argv[2])
bins = range(part, 4096, nparts) if len(sys.argv) < 4 else [int(v, 16) >> 4 for v in sys.argv[3].split(",")]
N8 = dict(U=(0, 127), UL=(-90, 90), L=(-128, 0), DL=(-90, -90), D=(0, -128), DR=(90, -90), R=(127, 0), UR=(90, 90))
def spin(d, turn_first):
    sx, sy = N8[d]
    s = [(21, 0, 0, 0)] + ([(1, 0, sx, sy)] if turn_first else []) + [(1, A, sx, sy), (20, R, sx, sy)]
    return s
MOVES = {"SidehopL": lambda: hold_sidehop(True), "SidehopR": lambda: hold_sidehop(False),
         "ScootFwd": shield_scoot_forward, "Backflip": hold_backflip}
SPINS = [("U", False), ("L", False), ("R", False), ("UL", False), ("UR", False),
         ("L", True), ("R", True), ("D", True), ("UL", True), ("UR", True), ("DL", True), ("DR", True)]
g = G(ROM); g.load(ENTRY); g.run([(4, 0, 0, 0)])
for base_ in (LINK + 0x24, LINK + 0x108):  # move to the middle of the open floor so no move touches a wall
    g.write(base_, struct.pack(">f", -180.0)); g.write(base_ + 8, struct.pack(">f", 470.0))
g.run([(10, 0, 0, 0)])
base = f"/dev/shm/_gm_base{part}.m64"; g.save(base)
S = f"/dev/shm/_gm_s{part}.m64"
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
def rec(seq):
    fr = []
    for n, b, x, y in seq:
        for _ in range(n):
            x0, z0 = g.f32(LINK + 0x24), g.f32(LINK + 0x2C)
            g.frame(b, x, y)
            x1, z1 = g.f32(LINK + 0x24), g.f32(LINK + 0x2C)
            sp = g.read(LINK + 0x70, 4).hex(); ang = g.u16(LINK + 0x32)
            if x1 != x0 or z1 != z0: fr.append((sp, ang, x1 - x0, z1 - z0))
    g.set_input(0, 0, 0)
    return fr
out = open(SP + f"/moves_{part}.jsonl", "a")
import glob
done = set()
for f in glob.glob(SP + "/moves_*.jsonl"):
    for line in open(f):
        try: done.add(json.loads(line)["a"] >> 4)
        except Exception: pass
for b in bins:
    if b in done: continue
    a = b * 16
    g.load(base)
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, a)
    g.run([(6, Z, 0, 0)]); camt = g.cam()
    g.target_untarget_snap(); snap = g.cam()
    g.save(S)
    r = dict(a=a, camt=camt, snap=snap, turn={}, move={})
    for d, (sx, sy) in N8.items():
        g.load(S); g.run([(1, 0, 0, 0), (1, 0, sx, sy), (12, 0, 0, 0)])
        r["turn"][d] = [g.u16(LINK + 0xBE), g.cam()]
    for name, f in MOVES.items():
        g.load(S); fr = rec(f())
        r["move"][name] = [fr, g.u16(LINK + 0xBE)]
    for d, tf in SPINS:
        g.load(S); fr = rec(spin(d, tf)); g.run([(12, 0, 0, 0)])
        r["move"][f"Spin{d}{'t' if tf else ''}"] = [fr, g.u16(LINK + 0xBE)]
    out.write(json.dumps(r) + "\n"); out.flush()
