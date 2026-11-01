"""Emulator-verify action lists (one per line on stdin, 'A | B | ...'): run the setup, then try every
import os
walk length the clip oracle allows from the emulator's actual end state (±2)."""
import sys, re; sys.path.insert(0, ".")
from verify import *
from clipcheck import APPROACH, candidates
import numpy as np
g = G(ROM)
tmp = "/dev/shm/_vb%d.m64" % os.getpid()
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    acts = [a.strip() for a in line.split("|")]
    g.load(ENTRY); g.run([(6, 0, 0, 0)])
    for a in acts: do(g, a)
    x, y, z, f = g.pos()
    g.save(tmp); g.run([(6, Z, 0, 0)]); w = g.cam()
    ws = [w] if w in APPROACH else [w + 1] if w + 1 in APPROACH else []
    es = set()
    for W in ws:
        for i, e in zip(*candidates(np.array([x]), np.array([z]), W)): es |= {e - 2, e - 1, e, e + 1, e + 2}
    if not es:
        tz = (824.2 - z) / 9; es = set(range(int(tz) - 6, int(tz) + 1))
    ok = []
    for e in sorted(es):
        if e < 0: continue
        g.load(tmp); tr = []
        g.run(final_walk(e) + [(20, 0, 0, 127)], tr)
        if any(s[2] > 845 and s[0] > -240 for s in tr): ok.append(e)
    print("CLIP" if ok else "fail", line, f"end=({x:.5f},{z:.5f}) facing={f:04X} cam={w:04X} walk extras={ok}", flush=True)
