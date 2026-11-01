"""Compare the scripted inputs with the human methods:
 tap turn  : scripted = 1-frame stick flick;  human = hold R, tilt stick to the notch, release stick, release R
 spin      : scripted = A + stick same frame; human = hold R + stick, then release R and press A (stick held)"""
import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
setupA = [a.strip() for a in "Tap DL + ESS Lx3|Backflip|Tap D + ESS Lx1|SpinU|Tap U|SpinUR|Tap L|ScootFwd|ESS Rx1".split("|")]
g.load(ENTRY); g.run([(6, 0, 0, 0)]); g.target_untarget_snap(); g.run([(1, 0, 0, 0)]); g.save("/dev/shm/_sh.m64")
for d in ("DL", "D", "U", "L", "UR"):
    sx, sy = N8[d]
    g.load("/dev/shm/_sh.m64"); g.run([(1, 0, sx, sy), (20, 0, 0, 0)]); a1 = g.pos()
    res = []
    for hold in (3, 10):
        g.load("/dev/shm/_sh.m64"); g.run([(2, R, 0, 0), (hold, R, sx, sy), (2, R, 0, 0), (20, 0, 0, 0)]); res.append(g.pos())
    print(f"tap {d}: flick facing={a1[3]:04X} pos=({a1[0]:.3f},{a1[2]:.3f}) | shield-turn " + " ".join(f"facing={p[3]:04X} pos=({p[0]:.3f},{p[2]:.3f})" for p in res))
# spins in setup A
for si, name in [(3, "SpinU"), (5, "SpinUR")]:
    g.load(ENTRY); g.run([(6, 0, 0, 0)])
    for a in setupA[:si]: do(g, a)
    g.target_untarget_snap(); g.run([(21, 0, 0, 0)]); g.save("/dev/shm/_sh2.m64")
    sx, sy = N8[name[4:]]
    g.load("/dev/shm/_sh2.m64"); g.run([(1, A, sx, sy), (25, R, sx, sy), (15, 0, 0, 0)]); p1 = g.pos()
    out = []
    for hold in (3, 10):
        g.load("/dev/shm/_sh2.m64"); g.run([(2, R, 0, 0), (hold, R, sx, sy), (1, A, sx, sy), (25, R, sx, sy), (15, 0, 0, 0)]); out.append(g.pos())
    print(f"{name}: scripted ({p1[0]:.6f},{p1[2]:.6f}) {p1[3]:04X} | shield-prehold " + " ".join(f"({p[0]:.6f},{p[2]:.6f}) {p[3]:04X}" for p in out))
