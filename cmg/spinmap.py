import sys, struct; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
def tele(x, z):
    for b in (LINK + 0x24, LINK + 0x108): g.write(b, struct.pack(">f", x)); g.write(b + 8, struct.pack(">f", z))
g.load(ENTRY); g.run([(4, 0, 0, 0)]); g.save("/dev/shm/_sm.m64")
ref = None
for z in range(800, 140, -60):
    row = []
    for x in range(-1600, 61, 60):
        g.load("/dev/shm/_sm.m64"); tele(x, z); g.run([(10, 0, 0, 0)])
        for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, 0x6000)
        g.run([(6, Z, 0, 0)]); g.target_untarget_snap(); g.run([(1, A, 127, 0), (8, R, 127, 0)])
        f = g.u16(LINK + 0xBE)
        if ref is None: ref = f
        row.append("." if f == ref else "#")
    print(f"{z:4d} " + "".join(row), flush=True)
print("x from -1600 step 60")
