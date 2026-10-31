import sys; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
g = G(ROM)
for name, sx, sy in [("back", 0, -128), ("left", -128, 0), ("right", 127, 0)]:
    g.load(ENTRY); g.run([(6, 0, 0, 0), (6, Z, 0, 0)])
    tr = []; g.run([(120, Z, sx, sy)], tr)
    print(name, [(round(s[0], 4), round(s[2], 4), f"{s[3]:04X}") for s in tr[::15]], repr(tr[-1][0]), repr(tr[-1][2]))
    g.run([(30, 0, 0, 0)]); print("   rest", g.st())
