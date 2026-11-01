"""Export lookup tables for c/search.c from the emulator-measured move table (gen_moves.py)."""
import sys, os, glob, json, struct, numpy as np
from sim import *
from clipcheck import APPROACH, GRIDS
SP = "/tmp/claude-0/-home-user-mmcliptesting/a78033bb-8150-5832-a8b0-7d77af0af2f6/scratchpad"
OUT = sys.argv[1] if len(sys.argv) > 1 else SP + "/cs"
import os; os.makedirs(OUT, exist_ok=True)

MT = {}
for f in glob.glob(SP + "/moves_*.jsonl"):
    for line in open(f):
        r = json.loads(line); MT[r["a"] >> 4] = r
HSPIN = bool(os.environ.get("HSPIN"))
if HSPIN:
    for f in glob.glob(SP + "/hspin_*.jsonl"):
        for line in open(f):
            r = json.loads(line)
            mv = MT[r["a"] >> 4]["move"]
            for k in [k for k in mv if k.startswith("Spin")]: del mv[k]
            mv.update(r["move"])
if os.environ.get("GUANO"):
    for f in glob.glob(SP + "/guano_*.jsonl"):
        for line in open(f):
            r = json.loads(line); MT[r["a"] >> 4]["move"].update(r["move"])
assert len(MT) == 4096, len(MT)
camt = np.array([MT[b]["camt"] for b in range(4096)])
camx = np.full(65536, -1, np.int64)
for f in glob.glob(SP + "/camexact_*.csv"):
    for line in open(f):
        a, c = line.strip().split(","); camx[int(a, 16)] = int(c, 16)

DIRS8 = ["U", "UL", "L", "DL", "D", "DR", "R", "UR"]
A = np.arange(65536)
TURNS = [("", A.copy())]
CARD_ONLY = bool(os.environ.get("CARD_ONLY"))   # no ESS, no diagonal taps/spins/pins
ks = [] if CARD_ONLY and not os.environ.get("ESS_ONCE") else [k for k in range(-8, 9) if k]
MAXSIP = 4 if CARD_ONLY else 2
ess = lambda a, k: (a + k * 0x708) & 0xFFFF
spn = lambda a, n: (a - n * 0x1E0) & 0xFFFF
TURNS += [(f"ESS {'L' if k > 0 else 'R'}x{abs(k)}", ess(A, k)) for k in ks]
for d in (["U", "L", "D", "R"] if CARD_ONLY else DIRS8):
    tap = np.array([MT[b]["turn"][d][0] for b in range(4096)])[A >> 4]
    TURNS.append((f"Tap {d}", tap))
    TURNS += [(f"Tap {d} + ESS {'L' if k > 0 else 'R'}x{abs(k)}", ess(tap, k)) for k in ks]
    TURNS += [(f"Tap {d} + SpinInPlace x{n}", spn(tap, n)) for n in range(1, MAXSIP + 1)]
TURNS += [(f"SpinInPlace x{n}", spn(A, n)) for n in range(1, MAXSIP + 1)]
np.array([t for _, t in TURNS], dtype=np.uint16).tofile(OUT + "/turns.bin")
np.array([(1 if n.startswith("Tap") else 0) | (2 if "ESS" in n else 0) for n, _ in TURNS], dtype=np.int32).tofile(OUT + "/turnkind.bin")

MNAMES = list(MT[0]["move"].keys()) + ["CornerSE", "BackWall"]
if CARD_ONLY: MNAMES = [m for m in MNAMES if m not in ("CornerSE",) and not any(m.endswith(d) for d in ("UL", "UR", "DL", "DR")) and m not in ("HSpinD", "SpinD", "SpinDt")]
if os.environ.get("HSPIN"): MNAMES = [m for m in MNAMES if not m.startswith("Spin") or m.startswith("SpinInPlace")]
kinds = []
buf = bytearray()
for name in MNAMES:
    kinds.append(1 if name == "CornerSE" else 2 if name == "BackWall" else 3 if name.startswith(("Spin", "HSpin")) else 0)
    for b in range(4096):
        if name in ("CornerSE", "BackWall"):
            ok = 1 if name == "CornerSE" else int(camt[b] == 0 and b == 0)
            buf += struct.pack("<ddHHB", 0.0, 0.0, 0, 0, ok); continue
        fr, ff = MT[b]["move"][name]
        dx = sum(d[2] for d in fr); dz = sum(d[3] for d in fr)
        keep = name in ("SidehopL", "SidehopR", "ScootFwd", "Backflip") or name.startswith("Guano")
        buf += struct.pack("<ddHHB", dx, dz, 0 if keep else 1, ff, 1)
open(OUT + "/moves.bin", "wb").write(buf)
np.array(kinds, dtype=np.int32).tofile(OUT + "/movekind.bin")

RAYW = sorted(APPROACH)
rays = []
for w in RAYW:
    w8, w9 = APPROACH[w]; x0, x1, z0, z1 = GRIDS[w9 & 0xFFF0]["box"]
    rays.append(((x0 + x1) / 2, (z0 + z1) / 2, float(sinf(w)), float(cosf(w)), float(sinf(w8)), float(cosf(w8)), x0, x1, z0, z1))
np.array(rays, dtype=np.float64).tofile(OUT + "/rays.bin")

def camfinal(f): return np.where(camx[f] >= 0, camx[f], camt[f >> 4])
fin = np.full((65536, 16), -1, np.int16); cnt = np.zeros(65536, int)
for ti, (_, tf) in enumerate(TURNS):
    w = camfinal(tf)
    w = np.where(np.isin(w, RAYW), w, w + 1)
    for ri, W in enumerate(RAYW):
        idx = np.nonzero((w == W) & (cnt < 8))[0]
        fin[idx, 2 * cnt[idx]] = ti; fin[idx, 2 * cnt[idx] + 1] = ri; cnt[idx] += 1
fin.tofile(OUT + "/final.bin")
json.dump(dict(turns=[n for n, _ in TURNS], moves=MNAMES, rays=RAYW), open(OUT + "/names.json", "w"))
print("turns", len(TURNS), "moves", len(MNAMES), "rays", len(RAYW), "facings with a final turn", (cnt > 0).sum(), "max", cnt.max())
