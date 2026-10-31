import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
sys.path.insert(0, "../emu"); from colgeo import static_polys
g = G(ROM); g.load(ENTRY)
for p in static_polys(g):
    nx, ny, nz = p["n"]
    if abs(ny) > 0.5: continue
    ys = [v[1] for v in p["v"]]
    if min(ys) > 60 or max(ys) < 0: continue
    xs = [v[0] for v in p["v"]]; zs = [v[2] for v in p["v"]]
    print(f"{p['i']:4d} n=({nx:+.2f},{nz:+.2f}) x[{min(xs)},{max(xs)}] z[{min(zs)},{max(zs)}] y[{min(ys)},{max(ys)}]")
