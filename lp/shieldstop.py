import sys, math; sys.path.insert(0, ".")
from lpfinal import *
g = G(ROM); g.load(LP); g.run([(2, 0, 0, 0), (12, 0, 20, 0), (6, Z, 0, 0), (1, 0, 0, 0)])
g.save("/dev/shm/_ss0.m64")
for d, (sx, sy) in (("L", (-80, 0)), ("R", (80, 0)), ("U", (0, 80))):
    for n in (3, 6, 10, 14):
        g.load("/dev/shm/_ss0.m64"); g.run([(n, 0, sx, sy)])
        x0, _, z0, f0 = g.pos(); sp = g.f32(LINK + 0x70); mv = g.u16(LINK + 0x32)
        g.run([(10, R, 0, 0)]); x1, _, z1, f1 = g.pos()
        dx, dz = x1 - x0, z1 - z0; dist = math.hypot(dx, dz)
        ang = int(math.atan2(dx, dz) / (2 * math.pi) * 65536) & 0xFFFF if dist > 0 else 0
        print(f"run {d} {n:2d}: speed {sp:.3f} mv {mv:04X} facing {f0:04X} -> shield moved {dist:.3f} at {ang:04X}, facing {f1:04X}")
