"""teleport Link (facing f, standing) to (x0,z0); hold Z+Up; at frame t press A(+Up), detect clip."""
import sys, math, struct; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
g = G(ROM); g.load(ENTRY); g.run([(4,0,0,0)])
g.save(SP + "/st/_xs0.m64")
def setf(a, v): g.write(a, struct.pack(">f", v))
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
def tele(x, z, yaw):
    for base in (LINK + 0x24, LINK + 0x108):
        setf(base, x); setf(base + 8, z)
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, yaw)
f = int(sys.argv[1], 16); z0 = float(sys.argv[2]); xs = [float(v) for v in sys.argv[3].split(":")]
x0 = xs[0]
while x0 <= xs[1] + 1e-9:
    g.load(SP + "/st/_xs0.m64"); tele(x0, z0, f); g.run([(6, Z, 0, 0)])
    tr = []
    for t in range(80):
        g.frame(Z, 0, 127); x, y, z, a = g.pos(); tr.append((x, z))
        if z > 812: break
    g.save(SP + "/st/_xs1.m64")
    res = []
    for k in range(10):
        for zb in (0, Z):
            g.load(SP + "/st/_xs1.m64")
            t2 = []; g.run([(1, A | zb, 0, 127), (12, zb, 0, 127)], t2)
            if max(s[2] for s in t2) > 845: res.append((k, zb))
        g.load(SP + "/st/_xs1.m64"); g.run([(1, Z, 0, 127)]); g.save(SP + "/st/_xs1.m64")
    print(f"{x0:.4f}", tr[-1], res, flush=True)
    x0 += xs[2]
