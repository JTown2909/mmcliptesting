import sys; sys.path.insert(0, ".")
from verify import *
setup = "Tap DL + ESS Lx3|Backflip|Tap D + ESS Lx1|SpinU|Tap U".split("|")
g = G(ROM); g.load(ENTRY); g.run([(6, 0, 0, 0)])
for a in setup: do(g, a)
g.target_untarget_snap(); g.save("/dev/shm/_um.m64")
print("start", g.pos())
for k in range(0, 4):           # frames between shield release and A (stick held throughout)
    g.load("/dev/shm/_um.m64")
    tr = []
    g.run([(15, R, 69, 69)] + ([(k, 0, 69, 69)] if k else []) + [(1, A, 69, 69), (18, 0, 69, 69), (2, R, 69, 69), (25, R, 0, 0)], tr)
    fac = []
    for s in tr[15:]:
        if not fac or fac[-1] != s[3]: fac.append(s[3])
    x, y, z, f = g.pos()
    print(f"k={k}: end ({x:.4f},{z:.4f}) facing={f:04X}  seq " + " ".join(f"{v:04X}" for v in fac[:18]))
