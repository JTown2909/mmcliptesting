import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
for pre in (3, 15):
  for k, ahold in [(0, 1), (0, 2), (0, 3), (0, 6), (1, 1), (1, 3), (2, 1), (2, 3)]:
    g.load("/dev/shm/_um.m64")
    g.run([(pre, R, 69, 69)] + ([(k, 0, 69, 69)] if k else []) + [(ahold, A, 69, 69), (8, 0, 69, 69), (25, R, 69, 69), (20, R, 0, 0)])
    x, y, z, f = g.pos()
    print(f"shield+stick {pre:2d}f, A {k} frame(s) after release, A held {ahold}f: end ({x:.4f},{z:.4f}) facing={f:04X}")
