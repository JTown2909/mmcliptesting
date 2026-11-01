import sys, struct; sys.path.insert(0, "../cmg")
from verify import *
g = G(ROM)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
g.load(SP + "/st/laundry-pool.m64"); g.run([(4, 0, 0, 0)]); g.save("/dev/shm/_lp0.m64")
for f in [(0xF000 + i * 0x80) & 0xFFFF for i in range(0x28)]:
    g.load("/dev/shm/_lp0.m64")
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, f)
    g.target_untarget_snap()
    g.run([(6, Z, 0, 0), (240, Z, 0, 80)]); a = g.pos()
    g.run([(60, Z, 0, 80)]); b = g.pos()
    print(f"facing {f:04X}: t240 ({a[0]:.4f},{a[2]:.4f})  t300 ({b[0]:.4f},{b[2]:.4f}) speed {g.f32(LINK+0xAD0):.3f}", flush=True)
