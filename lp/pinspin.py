import sys, struct; sys.path.insert(0, "../cmg")
from verify import *
LP = SP + "/st/laundry-pool.m64"
g = G(ROM)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
g.load(LP); g.run([(4, 0, 0, 0)]); g.save("/dev/shm/_lp0.m64")
lo, hi, st = (int(v, 16) for v in sys.argv[1:4])
for f in [(lo + i * st) & 0xFFFF for i in range(((hi - lo) & 0xFFFF) // st)]:
    g.load("/dev/shm/_lp0.m64")
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, f)
    g.target_untarget_snap()
    g.run([(6, Z, 0, 0), (60, Z, 0, 80)])
    xp, _, zp, _ = g.pos()
    res = []
    for zb in (Z, 0):
        g.save("/dev/shm/_lp1.m64")
        tr = []; g.run([(1, A | zb, 0, 80), (15, zb, 0, 80)], tr)
        clip = any(s[0] < -1438 and s[2] > 430 for s in tr)
        res.append(("CLIP" if clip else "-") + f"[{'Z' if zb else 'noZ'}]")
        g.load("/dev/shm/_lp1.m64")
    print(f"facing {f:04X}: pinned at ({xp:.4f},{zp:.4f}) " + " ".join(res), flush=True)
