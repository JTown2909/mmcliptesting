import sys, struct; sys.path.insert(0, "../cmg")
from verify import *
g = G(ROM)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
def tele(x, z, y):
    for b in (LINK + 0x24, LINK + 0x108): g.write(b, struct.pack(">f", x)); g.write(b + 4, struct.pack(">f", y)); g.write(b + 8, struct.pack(">f", z))
g.load(SP + "/st/laundry-pool.m64"); g.run([(2, 0, 0, 0)]); g.save("/dev/shm/_ca.m64")
for (x, z, y) in [(-1480, 378, -40), (-1520, 360, -60), (-1700, 450, -110), (-1750, 330, -110), (-1250, 395, 50), (-1100, 600, 200), (-1600, 560, -100), (-1800, 220, -110)]:
    out = []
    for f in (0x2000, 0xB059, 0x0400, 0x6000):
        g.load("/dev/shm/_ca.m64"); tele(x, z, y + 30); g.run([(15, 0, 0, 0)])
        for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, f)
        g.run([(6, Z, 0, 0)]); c = g.cam(); g.target_untarget_snap(); s = g.cam()
        out.append(f"{f:04X}->t{c:04X}/s{s:04X}")
    px, py, pz, _ = g.pos()
    print(f"({x},{z}) -> stand ({px:.1f},{py:.1f},{pz:.1f}) " + " ".join(out), flush=True)
