"""Per facing bin: targeted camera after 6 frames of Z (cam_t), the untargeted camera after
target/untarget/settle (snap), and the facing after a cardinal tap L/R/D (lua cardinal_turn)."""
import sys, struct; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
part, nparts = int(sys.argv[1]), int(sys.argv[2])
g = G(ROM); g.load(ENTRY); g.run([(4, 0, 0, 0)])
base = SP + f"/st/_gc_base{part}.m64"; g.save(base)
tmp = SP + f"/st/_gc_tmp{part}.m64"
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
out = open(SP + f"/cam_table_{part}.csv", "w")
for b in range(part, 4096, nparts):
    a = b * 16
    g.load(base)
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, a)
    g.run([(6, Z, 0, 0)]); camt = g.cam()
    old = g.cam(); g.run([(10, 0, 0, 0)]); new = g.cam()
    while old != new:
        g.run([(10, 0, 0, 0)]); old, new = new, g.cam()
    snap = new
    g.save(tmp)
    res = []
    for d in ("LEFT", "RIGHT", "DOWN"):
        g.load(tmp); g.run([(1, 0, 0, 0), (1, 0) + CARD[d]]); g.target_untarget_snap()
        res.append((g.u16(LINK + 0xBE), g.cam()))
    out.write(f"{a:04X},{camt:04X},{snap:04X}," + ",".join(f"{f:04X},{c:04X}" for f, c in res) + "\n"); out.flush()
print("done", part)
