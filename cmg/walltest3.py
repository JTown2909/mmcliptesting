import sys, struct; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
g = G(ROM)
for hold in (60, 61, 62, 63, 90, 151, 200):
  for rel in ("both", "stickfirst"):
    g.load(ENTRY); g.run([(6, 0, 0, 0), (6, Z, 0, 0), (hold, Z, -90, -90)])
    if rel == "both": g.run([(40, 0, 0, 0)])
    else: g.run([(10, Z, 0, 0), (40, 0, 0, 0)])
    x, y, z, a, c, m, s = g.st()
    print(hold, rel, repr(x), repr(z), f"{a:04X} {c:04X}")
