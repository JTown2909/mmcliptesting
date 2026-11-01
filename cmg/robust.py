"""Timing sensitivity of the directional spins in a setup: delay the shield press after A by
0..k frames and change the pre-spin wait; report the end position of the spin."""
import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
setup = [a.strip() for a in sys.argv[1].split("|")]
idx = [i for i, a in enumerate(setup) if re.match(r"Spin(U|UL|L|DL|D|DR|R|UR)t?$", a)]
for si in idx:
    g.load(ENTRY); g.run([(6, 0, 0, 0)])
    for a in setup[:si]: do(g, a)
    g.target_untarget_snap(); g.save("/dev/shm/_rb.m64")
    m = re.match(r"Spin(\w+?)(t?)$", setup[si]); sx, sy = N8[m.group(1)]
    print(setup[si])
    for wait in (21, 10, 40):
        for rdelay in (0, 1, 2, 3, 5, 8):
            for hold in (20, 30):
                g.load("/dev/shm/_rb.m64")
                seq = [(wait, 0, 0, 0)] + ([(1, 0, sx, sy)] if m.group(2) else []) + [(1, A, sx, sy)]
                seq += [(rdelay, 0, sx, sy)] if rdelay else []
                seq += [(hold, R, sx, sy), (15, 0, 0, 0)]
                g.run(seq); x, y, z, f = g.pos()
                print(f"  wait={wait:2d} shield+{rdelay} hold={hold}: ({x:.6f},{z:.6f}) facing={f:04X}")
