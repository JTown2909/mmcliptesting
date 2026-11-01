import sys; sys.path.insert(0, "../cmg"); sys.path.insert(0, "../emu")
from prims import *
from colgeo import static_polys
LP = SP + "/st/laundry-pool.m64"
g = G(ROM); g.load(LP); g.run([(4, 0, 0, 0)])
x, y, z, f = g.pos(); print(f"entry ({x:.3f},{y:.3f},{z:.3f}) facing {f:04X} cam {g.cam():04X} scene {g.u16(PLAY + 0xA4):04X}")
P = static_polys(g)
X0, X1, Z0, Z1 = -1800, -1250, 200, 560
for p in P:
    xs = [v[0] for v in p["v"]]; zs = [v[2] for v in p["v"]]; ys = [v[1] for v in p["v"]]
    if max(xs) < X0 or min(xs) > X1 or max(zs) < Z0 or min(zs) > Z1: continue
    nx, ny, nz = p["n"]
    kind = "floor" if ny > 0.5 else "ceil" if ny < -0.5 else "wall"
    if kind == "ceil": continue
    if kind == "wall" and (min(ys) > 40 or max(ys) < -60): continue
    print(f"{kind:5s} {p['i']:4d} n=({nx:+.2f},{ny:+.2f},{nz:+.2f}) x[{min(xs)},{max(xs)}] y[{min(ys)},{max(ys)}] z[{min(zs)},{max(zs)}]")
