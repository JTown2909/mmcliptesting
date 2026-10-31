import sys, math, struct; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
g = G(ROM); g.load(ENTRY)
def setf(a, v): g.write(a, struct.pack(">f", v))
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
def tele(x, z, yaw):
    for base in (LINK + 0x24, LINK + 0x108):
        setf(base, x); setf(base + 8, z)
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, yaw)
ang = int(sys.argv[1], 16)
tele(-236.0, 800.0, ang); g.run([(1, 0, 0, 0), (6, Z, 0, 0)])
for i in range(30):
    g.frame(Z, 0, 127); x, y, z, a = g.pos()
    if i % 5 == 4: print(i, f"{x:.6f} {z:.6f} yaw={a:04X} spd={g.f32(LINK+0xAD0):.3f} mv={g.u16(LINK+0xAD4):04X} cam={g.cam():04X}")
g.save(SP + f"/st/cc_pin_{ang:04X}.m64")
