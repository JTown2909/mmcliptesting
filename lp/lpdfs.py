"""Laundry pool: emulator DFS over human-friendly steps (no frame-counted runs).
usage: lpdfs.py part nparts depth"""
import sys, os; sys.path.insert(0, ".")
from lpfinal import *
part, nparts, DEPTH = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
H8 = dict(U=(0, 80), UL=(-69, 69), L=(-80, 0), DL=(-69, -69), D=(0, -80), DR=(69, -69), R=(80, 0), UR=(69, 69))
TURNS = [f"ESS {d}x{k}" for d in "LR" for k in range(1, 9)] + [f"Tap {d}" for d in H8] + ["SpinInPlace x1"]
MOVES = ["SidehopL", "SidehopR", "ScootFwd", "Backflip", "ZSpinU", "ZSpinL", "ZSpinR", "ScootL1", "ScootR1"] + [f"Pin {d}" for d in H8]
STEPS = TURNS + MOVES
BOX = (-1441.0, -1432.0, 360.0, 392.0)
g = G(ROM); g.load(LP); g.run([(2, 0, 0, 0)])
pid = os.getpid(); stk = [f"/dev/shm/_ld{pid}_{i}.m64" for i in range(DEPTH + 3)]
out = open(SP + f"/lpdfs_{part}.txt", "a")
def step(a):
    if a.startswith("Pin "):
        sx, sy = H8[a[4:]]
        g.target_untarget_snap(); g.run([(6, Z, 0, 0), (130, Z, sx, sy)])
        x0, _, z0, _ = g.pos(); g.run([(20, Z, sx, sy)]); x1, _, z1, _ = g.pos()
        g.run([(10, Z, 0, 0), (10, 0, 0, 0)])
        return (x0, z0) == (x1, z1)          # only accept if Link really stopped
    do(g, a); return True
def allowed(prev, a):
    if prev is None: return True
    if prev.startswith("ESS") and (a.startswith("ESS") or a.startswith("Tap")): return False
    if prev.startswith("Tap") and a.startswith("Tap"): return False
    return True
seen = set(); nodes = [0]; hits = [0]
def inbox(x, z): return BOX[0] < x < BOX[1] and BOX[2] < z < BOX[3]
def try_final(path, d):
    """Link in the box: try 0-2 extra turns to bring the facing into 0200..0480, then the finish."""
    g.save(stk[d + 1])
    opts = [[]] + [[t] for t in TURNS] + [[t, u] for t in TURNS for u in TURNS if allowed(t, u)]
    for extra in opts:
        g.load(stk[d + 1]); ok = True
        for t in extra: do(g, t)
        x, y, z, f = g.pos()
        if not (0x0200 <= f <= 0x0480): continue
        g.save(stk[d + 2])
        for e in (0, 1, 2):
            g.load(stk[d + 2])
            if final(g, e):
                msg = "CLIP " + " | ".join(path + extra) + f" | tap target | Up {4 + e} + A   (rest {x:.4f},{z:.4f} facing {f:04X})"
                print(msg, flush=True); out.write(msg + "\n"); out.flush(); hits[0] += 1
def dfs(path, d, prev):
    g.save(stk[d])
    x, y, z, f = g.pos()
    if inbox(x, z): try_final(path, d); g.load(stk[d])
    if d == DEPTH: return
    for a in STEPS:
        if not allowed(prev, a): continue
        if d == 0 and STEPS.index(a) % nparts != part: continue
        g.load(stk[d])
        if not step(a): continue
        x, y, z, f = g.pos()
        key = (round(x, 4), round(z, 4), f, d + 1)
        if key in seen: continue
        seen.add(key); nodes[0] += 1
        dfs(path + [a], d + 1, a)
    if d == 1: print(f"  done branch {path} nodes {nodes[0]} hits {hits[0]}", flush=True)
dfs([], 0, None)
print("finished nodes", nodes[0], "hits", hits[0], flush=True)
