import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
pre = "ESS Lx8|SidehopR|ESS Lx7|ScootFwd|ESS Lx7|SidehopL|ScootFwd".split("|")
g.load(ENTRY); g.run([(6, 0, 0, 0)])
for a in pre: do(g, a.strip())
g.target_untarget_snap()
for k in range(0, 100, 5):
    print(k, f"shape {g.u16(LINK+0xBE):04X} world {g.u16(LINK+0x32):04X} yaw {g.u16(LINK+0xAD4):04X} cam {g.cam():04X}",
          f"camB10 {g.s16(LINK+0xB10)} B14 {g.s16(LINK+0xB14)} head {g.s16(LINK+0xBC):04X} {g.s16(LINK+0xC0) & 0xFFFF:04X}")
    g.run([(5, 0, 0, 0)])
