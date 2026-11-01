import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
def check(setup):
    setup = [a.strip() for a in setup.split("|")]
    for si, a in enumerate(setup):
        m = re.match(r"Spin(U|UL|L|DL|D|DR|R|UR)(t?)$", a)
        if not m: continue
        g.load(ENTRY); g.run([(6, 0, 0, 0)])
        for b in setup[:si]: do(g, b)
        g.target_untarget_snap(); g.save("/dev/shm/_s3.m64")
        do(g, a); ref = g.pos()
        sx, sy = N8[m.group(1)]
        out = []
        for k in (1, 2, 3, 4):
            g.load("/dev/shm/_s3.m64"); g.run([(10, R, sx, sy), (k, 0, sx, sy), (1, A, sx, sy), (25, R, sx, sy)]); g.target_untarget_snap()
            p = g.pos(); out.append(f"k={k}:{'SAME' if p == ref else f'({p[0]:.4f},{p[2]:.4f}) {p[3]:04X}'}")
        print(f"  {a}: scripted ({ref[0]:.4f},{ref[2]:.4f}) {ref[3]:04X} | shield method " + " ".join(out))
for s in ["Tap DL + ESS Lx3|Backflip|Tap D + ESS Lx1|SpinU|Tap U|SpinUR|Tap L|ScootFwd|ESS Rx1",
          "Tap L + ESS Lx4|Backflip|ESS Lx1|SpinRt|Tap D|SpinLt|ESS Lx6|ScootFwd|ESS Rx2"]:
    print(s); check(s)
