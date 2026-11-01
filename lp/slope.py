import sys, struct; sys.path.insert(0, "../cmg")
from verify import *
LP = SP + "/st/laundry-pool.m64"
g = G(ROM)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
def tele(x, z, y):
    for b in (LINK + 0x24, LINK + 0x108): g.write(b, struct.pack(">f", x)); g.write(b + 4, struct.pack(">f", y)); g.write(b + 8, struct.pack(">f", z))
for (x, z, y) in [(-1471.215, 378.778, -34.17), (-1520, 360, -60), (-1580, 330, -100), (-1460, 395, -25)]:
    for f in (0x2000, 0xB059):
        res = []
        for mv in ("SidehopL", "ScootFwd", "Backflip"):
            g.load(LP); g.run([(2, 0, 0, 0)]); tele(x, z, y); g.run([(10, 0, 0, 0)])
            for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, f)
            g.target_untarget_snap(); x0, y0, z0, _ = g.pos(); do(g, mv); x1, y1, z1, _ = g.pos()
            res.append(f"{mv}=({x1-x0:+.4f},{z1-z0:+.4f})")
        print(f"at ({x},{z}) facing {f:04X} cam {g.cam():04X}: " + " ".join(res))
