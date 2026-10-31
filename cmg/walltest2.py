import sys, struct; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
g = G(ROM)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
for face in (0x0000, 0x9688, 0xCEC8, 0x3000):
  for name, sx, sy in [("downleft", -90, -90), ("down", 0, -128)]:
    g.load(ENTRY); g.run([(2, 0, 0, 0)])
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, face)
    g.run([(6, Z, 0, 0)])
    tr = []; g.run([(150, Z, sx, sy)], tr)
    g.run([(1, Z, 0, 0), (30, 0, 0, 0)]); x, y, z, a, c, m, s = g.st()
    print(f"{face:04X} {name:9s} end=({tr[-1][0]!r},{tr[-1][2]!r}) rest=({x!r},{z!r}) facing={a:04X} cam={c:04X}")
