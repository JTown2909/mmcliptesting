import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
def trace(label, seq):
    g.load(ENTRY); g.run([(6, 0, 0, 0)]); g.target_untarget_snap(); g.run([(6, 0, 0, 0), (6, Z, 0, 0)])
    print(label)
    i = 0
    for n, b, x, y in seq:
        for _ in range(n):
            x0, _, z0, _ = g.pos(); g.frame(b, x, y); x1, _, z1, f = g.pos()
            btn = "+".join(k for k, m in (("Z", Z), ("R", R)) if b & m)
            print(f"  f{i:2d} {btn:4s} stick({x:4d},{y:4d})  speed={g.f32(LINK + 0x70):.3f} moved=({x1 - x0:+.3f},{z1 - z0:+.3f})")
            i += 1
trace("guano scoot (Left): shield+Left, release shield until moving, reshield",
      [(4, Z | R, -80, 0), (2, Z, -80, 0), (4, Z | R, -80, 0)])
trace("guano scoot, release shield 1 frame only",
      [(4, Z | R, -80, 0), (1, Z, -80, 0), (5, Z | R, -80, 0)])
trace("shield scoot forward (imbued: release 3 frames)",
      [(4, Z | R, 0, 80), (3, Z, 0, 80), (4, Z | R, 0, 80)])
for rel in (3, 4, 5):
    trace(f"guano scoot (Left), release shield {rel} frames", [(4, Z | R, -80, 0), (rel, Z, -80, 0), (5, Z | R, -80, 0)])
