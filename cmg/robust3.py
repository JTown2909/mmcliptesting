import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
g.load(ENTRY); g.run([(6, 0, 0, 0)]); g.target_untarget_snap(); g.run([(1, 0, 0, 0)]); g.save("/dev/shm/_rt.m64")
for d in ("DL", "D", "L", "U"):
    sx, sy = N8[d]
    for n in (1, 2, 3, 4):
        for shield in (False, True):
            g.load("/dev/shm/_rt.m64")
            g.run([(n, R if shield else 0, sx, sy), (20, 0, 0, 0)]); x, y, z, f = g.pos()
            print(f"tap {d:2s} {n} frames{' +shield' if shield else ''}: ({x:.5f},{z:.5f}) facing={f:04X}")
