import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
g.load(ENTRY); g.run([(6, 0, 0, 0)]); g.target_untarget_snap(); g.run([(1, 0, 0, 0)]); g.save("/dev/shm/_sh.m64")
sx, sy = N8["DL"]
print("tap via shield, DL:")
for n in (3, 10):
    for k in (1, 2, 3):
        g.load("/dev/shm/_sh.m64"); g.run([(n, R, sx, sy), (k, 0, sx, sy), (20, 0, 0, 0)]); p = g.pos()
        print(f"  R+stick {n}, then stick {k} frames after release: facing={p[3]:04X} pos=({p[0]:.3f},{p[2]:.3f})")
print("spin via shield, D (scripted ref first):")
sx, sy = N8["D"]
g.load("/dev/shm/_sh.m64"); g.run([(21, 0, 0, 0), (1, A, sx, sy), (25, R, sx, sy), (15, 0, 0, 0)]); p = g.pos()
print(f"  scripted: ({p[0]:.4f},{p[2]:.4f}) {p[3]:04X}")
for k in range(0, 5):
    g.load("/dev/shm/_sh.m64"); g.run([(10, R, sx, sy)] + ([(k, 0, sx, sy)] if k else []) + [(1, A, sx, sy), (25, R, sx, sy), (15, 0, 0, 0)]); p = g.pos()
    print(f"  shield+stick, A {k} frames after release: ({p[0]:.4f},{p[2]:.4f}) {p[3]:04X}")
