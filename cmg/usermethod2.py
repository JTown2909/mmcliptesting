import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
for n in range(0, 22, 1):
    g.load("/dev/shm/_um.m64")
    g.run([(15, R, 69, 69), (1, 0, 69, 69), (1, A, 69, 69), (n, 0, 69, 69), (25, R, 69, 69), (20, R, 0, 0)])
    x, y, z, f = g.pos()
    print(f"stick-only {n:2d} frames then shield: end ({x:.4f},{z:.4f}) facing={f:04X}")
