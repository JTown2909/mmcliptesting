import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
setup = [a.strip() for a in sys.argv[1].split("|")]
idx = [i for i, a in enumerate(setup) if re.match(r"Spin(U|UL|L|DL|D|DR|R|UR)t?$", a)]
for si in idx:
    g.load(ENTRY); g.run([(6, 0, 0, 0)])
    for a in setup[:si]: do(g, a)
    g.target_untarget_snap(); g.run([(21, 0, 0, 0)]); g.save("/dev/shm/_rb.m64")
    m = re.match(r"Spin(\w+?)(t?)$", setup[si]); sx, sy = N8[m.group(1)]
    print(setup[si])
    for early in (0, 1, 2, 3, 4, 6):          # stick held this many frames before A
        for late in (0, 1, 2):                # ... or stick arrives this many frames after A
            if early and late: continue
            g.load("/dev/shm/_rb.m64")
            seq = ([(early, 0, sx, sy)] if early else []) + ([(late, A, 0, 0)] if late else []) + [(1, A, sx, sy), (25, R, sx, sy), (15, 0, 0, 0)]
            g.run(seq); x, y, z, f = g.pos()
            print(f"  stick {'-' if early else '+'}{early or late}: ({x:.6f},{z:.6f}) facing={f:04X}")
