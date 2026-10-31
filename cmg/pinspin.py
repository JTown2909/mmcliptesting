import sys, math, struct; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
g = G(ROM)
st = sys.argv[1]; T = int(sys.argv[2])
NOTCH = [(0,127),(-90,90),(-127,0),(-90,-90),(0,-128),(90,-90),(127,0),(90,90)]
hits = 0
g.load(st)
base = SP + "/st/_pp.m64"
for t in range(T):
    g.save(base)  # state at slide frame t
    x0, _, z0, a0 = g.pos()
    for (sx, sy) in NOTCH:
        for zb in (0, Z):
            g.load(base)
            tr = []
            g.run([(1, A | zb, sx, sy), (14, zb, sx, sy)], tr)
            mz = max(s[2] for s in tr)
            if mz > 845 or tr[-1][0] > -228 and tr[-1][2] > 835:
                hits += 1; print("HIT", t, sx, sy, zb, f"{x0:.5f} {z0:.5f}", [(round(s[0],3), round(s[2],3)) for s in tr[:6]])
    g.load(base); g.run([(1, Z, 0, 127)])
print("done", hits)
