import sys, struct; sys.path.insert(0, ".")
from verify import *
g = G(ROM); g.load(ENTRY); g.run([(4, 0, 0, 0)])
for b_ in (LINK + 0x24, LINK + 0x108): g.write(b_, struct.pack(">f", -180.0)); g.write(b_ + 8, struct.pack(">f", 470.0))
g.run([(10, 0, 0, 0)]); g.save("/dev/shm/_hv.m64")
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
for base in (0x9210, 0x5C40):
    for lo in range(0, 16, 3):
        for d in ("L", "U"):
            g.load("/dev/shm/_hv.m64"); a = base + lo
            for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, a)
            g.run([(6, Z, 0, 0)]); g.target_untarget_snap(); c = g.cam(); x0, _, z0, _ = g.pos()
            do(g, f"HSpin{d}"); x, y, z, f = g.pos()
            print(f"facing {a:04X} cam {c:04X} HSpin{d}: d=({x - x0:.4f},{z - z0:.4f}) end facing {f:04X}")
