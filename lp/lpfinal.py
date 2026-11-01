"""Laundry pool final approach oracle by emulation: Link standing at P with facing f,
tap target and let the camera settle, hold Up (4+e) frames then A+Up; clip = ends behind the back wall."""
import sys, struct, math; sys.path.insert(0, "../cmg")
from verify import *
LP = SP + "/st/laundry-pool.m64"
def seth(g, a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
def setf(g, a, v): g.write(a, struct.pack(">f", v))
def place(g, x, z, f, base="/dev/shm/_lpf0.m64"):
    g.load(base)
    for b in (LINK + 0x24, LINK + 0x108): setf(g, b, x); setf(g, b + 8, z)
    for o in (0x32, 0xBE, 0xAD4): seth(g, LINK + o, f)
    g.run([(20, 0, 0, 0)])
def final(g, e=0, trace=None):
    g.run([(1, Z, 0, 0), (1, 0, 0, 0)]); g.target_untarget_snap()
    tr = [] if trace is None else trace
    g.run([(4 + e, 0, 0, 80), (25, A, 0, 80)], tr)
    return any(s[0] < -1438 and s[2] > 430 for s in tr)
if __name__ == "__main__":
    g = G(ROM); g.load(LP); g.run([(2, 0, 0, 0)]); g.save("/dev/shm/_lpf0.m64")
    x0 = struct.unpack(">f", bytes.fromhex("C4B3A704"))[0]; z0 = struct.unpack(">f", bytes.fromhex("43BE5D01"))[0]
    for f in (0x0400, 0x03F0, 0x0410, 0x0380, 0x0480):
        place(g, x0, z0, f); x, y, z, ff = g.pos()
        tr = []; ok = final(g, 0, tr)
        print(f"P0 facing {f:04X}: placed ({x:.4f},{y:.2f},{z:.4f}) {ff:04X} -> {'CLIP' if ok else 'no'}", [(round(s[0],3), round(s[2],3), f"{s[5]:04X}") for s in tr[2:7]])
