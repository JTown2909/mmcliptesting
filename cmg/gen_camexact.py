"""Targeted camera angle (after 6 frames of Z from rest) for every facing in [lo, hi)."""
import sys, struct; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
lo, hi, part, nparts = int(sys.argv[1], 16), int(sys.argv[2], 16), int(sys.argv[3]), int(sys.argv[4])
g = G(ROM); g.load(ENTRY); g.run([(4, 0, 0, 0)])
base = SP + f"/st/_ce_base{part}.m64"; g.save(base)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
out = open(SP + f"/camexact_{part}.csv", "a")
for a in range(lo + part, hi, nparts):
    g.load(base)
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, a & 0xFFFF)
    g.run([(6, Z, 0, 0)])
    out.write(f"{a & 0xFFFF:04X},{g.cam():04X}\n"); out.flush()
