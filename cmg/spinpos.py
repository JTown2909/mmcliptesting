import sys, struct; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
def tele(x, z):
    for b in (LINK + 0x24, LINK + 0x108): g.write(b, struct.pack(">f", x)); g.write(b + 8, struct.pack(">f", z))
for (x, z) in [(-700, 465), (-70, 306.5), (-400, 465), (-700, 306.5), (-1000, 600), (-70, 465)]:
    g.load(ENTRY); g.run([(4, 0, 0, 0)]); tele(x, z); g.run([(10, 0, 0, 0)])
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, 0x6000)
    g.run([(6, Z, 0, 0)]); g.target_untarget_snap()
    x0, _, z0, _ = g.pos()
    do(g, "SpinLt")
    x1, _, z1, f = g.pos()
    print((x, z), round(x1 - x0, 4), round(z1 - z0, 4), hex(f))
