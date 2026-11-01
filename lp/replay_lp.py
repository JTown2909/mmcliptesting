import sys, struct; sys.path.insert(0, "../cmg")
from verify import *
LP = SP + "/st/laundry-pool.m64"
g = G(ROM)
def hx(v): return struct.pack(">f", v).hex().upper()
def show(t):
    x, y, z, f = g.pos(); print(f"{t:34s} x={hx(x)} ({x:.4f}) z={hx(z)} ({z:.4f}) facing={f:04X} cam={g.cam():04X}")
g.load(LP); g.run([(2, 0, 0, 0)]); show("entry")
g.run([(12, 0, 20, 0)]); show("ESS right x12 frames")
for hold in (20, 40, 80):
    g.load(LP); g.run([(2, 0, 0, 0), (12, 0, 20, 0), (6, Z, 0, 0)])
    g.run([(hold, Z, -80, 0)]); show(f"Z+left {hold}")
    g.run([(hold, Z, 80, 0)]); show(f"Z+right {hold}")
    g.run([(10, Z | R, 0, 0)]); show("shield")
    g.run([(10, Z | R, 0, 0), (20, 0, 0, 0)]); show("released")
