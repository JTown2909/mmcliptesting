"""Laundry pool: emulator search over  prefix | run d1 n1 | [run d2 n2] | shield | [tap] | final approach.
usage: lpsearch.py part nparts prefixes(comma list: '', 'T', 'ESS L3+T', ...)"""
import sys, os, math, struct; sys.path.insert(0, ".")
from lpfinal import *
part, nparts = int(sys.argv[1]), int(sys.argv[2])
PREFIXES = sys.argv[3].split(",")
N1 = N2 = 30
NOTCH = dict(U=(0, 80), UL=(-69, 69), L=(-80, 0), DL=(-69, -69), D=(0, -80), DR=(69, -69), R=(80, 0), UR=(69, 69))
BOX = (-1441.0, -1432.0, 360.0, 392.0)        # where a clipping rest position (e = 0..2) can be
g = G(ROM); g.load(LP); g.run([(2, 0, 0, 0)])
base = f"/dev/shm/_ls_base{os.getpid()}.m64"; g.save(base)
tmp = f"/dev/shm/_ls_{os.getpid()}"
out = open(SP + f"/lpsearch_{part}.txt", "a")
def near_box(x, z, m): return BOX[0] - m < x < BOX[1] + m and BOX[2] - m < z < BOX[3] + m
def do_prefix(p):
    g.load(base)
    if not p: return
    for a in p.split("+"):
        a = a.strip()
        if a == "T": g.run([(8, Z, 0, 0)])
        else: do(g, a)
def finals(label):
    """state = Link shielded at rest. try optional tap turns then the final approach."""
    g.save(tmp + "_sh.m64")
    x, y, z, f = g.pos()
    for tap in [None] + list("U L D R".split()):
        g.load(tmp + "_sh.m64"); g.run([(4, 0, 0, 0)])
        if tap: do(g, f"Tap {tap}")
        fx, _, fz, ff = g.pos()
        if not (0x0200 <= ff <= 0x0480): continue
        g.save(tmp + "_ft.m64")
        for e in (0, 1, 2):
            g.load(tmp + "_ft.m64")
            if final(g, e):
                msg = f"CLIP {label} | shield{' | Tap ' + tap if tap else ''} | walk {4 + e} => rest ({fx:.4f},{fz:.4f}) facing {ff:04X}"
                print(msg, flush=True); out.write(msg + "\n"); out.flush()
tasks = [(p, d1) for p in PREFIXES for d1 in NOTCH]
for p, d1 in tasks[part::nparts]:
    do_prefix(p); g.save(tmp + "_p.m64")
    s1, t1 = NOTCH[d1]
    for n1 in range(1, N1 + 1):
        g.load(tmp + "_p.m64"); g.run([(n1, 0, s1, t1)]); g.save(tmp + "_r1.m64")
        x, _, z, _ = g.pos()
        if near_box(x, z, 16):
            g.run([(10, R, 0, 0)]); x2, _, z2, _ = g.pos()
            if near_box(x2, z2, 0.5): finals(f"{p or '-'} | run {d1} {n1}")
        for d2 in NOTCH:
            if d2 == d1: continue
            s2, t2 = NOTCH[d2]
            g.load(tmp + "_r1.m64")
            for n2 in range(1, N2 + 1):
                g.frame(0, s2, t2)
                x, _, z, _ = g.pos()
                if near_box(x, z, 16):
                    g.save(tmp + "_r2.m64")
                    g.run([(10, R, 0, 0)]); x2, _, z2, _ = g.pos()
                    if near_box(x2, z2, 0.5): finals(f"{p or '-'} | run {d1} {n1} | run {d2} {n2}")
                    g.load(tmp + "_r2.m64")
    print("done", p, d1, flush=True)
