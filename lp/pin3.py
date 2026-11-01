import sys, struct; sys.path.insert(0, "../cmg")
from verify import *
g = G(ROM)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
g.load(SP + "/st/laundry-pool.m64"); g.run([(4, 0, 0, 0)]); g.save("/dev/shm/_lp0.m64")
N8 = dict(U=(0, 80), UL=(-69, 69), L=(-80, 0), R=(80, 0), UR=(69, 69))
hits = 0
for f in [(0xF680 + i * 0x20) & 0xFFFF for i in range(0x30)]:
    g.load("/dev/shm/_lp0.m64")
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, f)
    g.target_untarget_snap()
    g.run([(6, Z, 0, 0), (200, Z, 0, 80)]); p = g.pos(); g.save("/dev/shm/_lp1.m64")
    res = []
    for zb in (Z, 0):
        for d, (sx, sy) in N8.items():
            g.load("/dev/shm/_lp1.m64"); tr = []
            g.run([(1, A | zb, sx, sy), (16, zb, sx, sy)], tr)
            if any(s[0] < -1438 and s[2] > 430 for s in tr): res.append(f"{'Z' if zb else 'noZ'}+{d}"); hits += 1
    print(f"facing {f:04X} pinned ({p[0]:.4f},{p[2]:.4f}) cam {g.cam():04X}: clips with {res}", flush=True)
print("hits", hits)
