import sys; sys.path.insert(0, ".")
import verify as V
from verify import *
setup = "Tap DL + ESS Lx3|Backflip|Tap D + ESS Lx1|SpinU|Tap U|SpinUR|Tap L|ScootFwd|ESS Rx1".split("|")
g = G(ROM)
for label, card, diag in [("127/90", 127, 90), ("80/69", 80, 69)]:
    V.N8.update(U=(0, card), UL=(-diag, diag), L=(-card, 0), DL=(-diag, -diag), D=(0, -card), DR=(diag, -diag), R=(card, 0), UR=(diag, diag))
    g.load(ENTRY); g.run([(6, 0, 0, 0)])
    out = []
    for a in setup:
        do(g, a); x, y, z, f = g.pos(); out.append(f"{a}:{f:04X}")
    print(label, " ".join(out), f"end=({x:.4f},{z:.4f})")
