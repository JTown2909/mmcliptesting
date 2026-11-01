import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
pre = "ESS Lx8|SidehopR|ESS Lx7|ScootFwd|ESS Lx7|SidehopL|ScootFwd".split("|")
g.load(ENTRY); g.run([(6, 0, 0, 0)])
for a in pre: do(g, a.strip())
g.target_untarget_snap(); g.save("/dev/shm/_hw.m64")
for label, zb in (("untargeted", 0), ("Z held throughout", Z)):
    for k in (0, 5, 10, 30, 60, 90, 150):
        g.load("/dev/shm/_hw.m64"); g.run([(k, 0, 0, 0)]) if k else None
        g.run([(6, zb, 0, 0), (4, R | zb, 0, 0), (8, R | zb, -80, 0), (1, zb, -80, 0), (1, A | zb, -80, 0), (8, zb, -80, 0), (25, R | zb, -80, 0), (10, R, 0, 0), (12, 0, 0, 0)])
        x, _, z, f = g.pos()
        print(f"{label:18s} wait {k:3d}: end ({x:.4f},{z:.4f}) facing {f:04X}")
