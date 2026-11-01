import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
pre = "ESS Lx8|SidehopR|ESS Lx7|ScootFwd|ESS Lx7|SidehopL|ScootFwd".split("|")
g.load(ENTRY); g.run([(6, 0, 0, 0)])
for a in pre: do(g, a.strip())
g.target_untarget_snap(); g.save("/dev/shm/_hw.m64")
res = []
for k in list(range(0, 12)) + [15, 20, 30, 40, 60, 90, 120]:
    g.load("/dev/shm/_hw.m64"); cams = []
    for _ in range(k): g.frame(0); cams.append(g.cam())
    c = g.cam(); x0, _, z0, _ = g.pos()
    g.run([(4, R, 0, 0), (8, R, -80, 0), (1, 0, -80, 0), (1, A, -80, 0), (8, 0, -80, 0), (25, R, -80, 0), (10, R, 0, 0), (12, 0, 0, 0)])
    x, _, z, f = g.pos()
    print(f"wait {k:3d}: cam before {c:04X}  end ({x:.4f},{z:.4f}) facing {f:04X}")
