"""For each facing f, scan rest positions across the predicted approach line and report which clip."""
import sys, math; sys.path.insert(0, ".")
from lpfinal import *
part, nparts = int(sys.argv[1]), int(sys.argv[2])
g = G(ROM); g.load(LP); g.run([(2, 0, 0, 0)]); g.save(f"/dev/shm/_lpf0.m64")
C = (-1430.97, 434.4)
fs = [f for f in range(0x0000, 0x0A00, 0x40)][part::nparts]
for f in fs:
    w = (f + 0xD8) & 0xFFFF; a = w / 65536 * 2 * math.pi
    dx, dz = math.sin(a), math.cos(a)
    hits = []
    for e in (0,):
        D = 53.95 + 9 * e
        for i in range(-60, 61):
            u = i * 0.05
            x = C[0] - D * dx + u * dz; z = C[1] - D * dz - u * dx
            place(g, x, z, f)
            if final(g, e): hits.append((round(u, 2), round(x, 3), round(z, 3)))
    print(f"facing {f:04X}: {len(hits)} clip points", hits[:3], hits[-1:] if hits else "", flush=True)
