import sys, struct; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
def tele(x, z):
    for b in (LINK + 0x24, LINK + 0x108): g.write(b, struct.pack(">f", x)); g.write(b + 8, struct.pack(">f", z))
for (x, z) in [(-70, 209.75), (-200, 400), (-300, 650), (0, 500)]:
    for f in (0x0000, 0x1234, 0x5C47, 0x9688, 0xC342, 0xE354):
        g.load(ENTRY); g.run([(4, 0, 0, 0)]); tele(x, z); g.run([(5, 0, 0, 0)])
        for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, f)
        g.target_untarget_snap(); do(g, "CornerSE"); p = g.pos()
        print(f"from ({x},{z}) facing {f:04X}: ({p[0]!r},{p[2]!r}) facing {p[3]:04X}")
