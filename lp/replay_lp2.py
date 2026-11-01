import sys, struct; sys.path.insert(0, "../cmg")
from verify import *
LP = SP + "/st/laundry-pool.m64"
g = G(ROM)
def hx(v): return struct.pack(">f", v).hex().upper()
def show(t):
    x, y, z, f = g.pos(); print(f"{t:30s} x={hx(x)} ({x:.4f}) z={hx(z)} ({z:.4f}) facing={f:04X} cam={g.cam():04X}")
for L, Rr in [(10, 15), (14, 15), (20, 15), (10, 25), (20, 40), (30, 60)]:
    g.load(LP); g.run([(2, 0, 0, 0), (12, 0, 20, 0), (6, Z, 0, 0), (10, 0, 0, 0)])
    g.run([(L, 0, -80, 0)]); show(f"left {L}")
    g.run([(Rr, 0, 80, 0)]); show(f"right {Rr}")
    g.run([(8, R, 0, 0)]); show("shield")
