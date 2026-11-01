import sys, math; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
pre = "ESS Lx8|SidehopR|ESS Lx7|ScootFwd|ESS Lx7|SidehopL|ScootFwd".split("|")
g.load(ENTRY); g.run([(6, 0, 0, 0)])
for a in pre: do(g, a.strip())
g.target_untarget_snap(); g.save("/dev/shm/_hw.m64")
def camgeo():
    c = PLAY + 0x220
    at = [g.f32(c + 0x50 + 4*i) for i in range(3)]; eye = [g.f32(c + 0x5C + 4*i) for i in range(3)]
    yaw = math.atan2(at[0]-eye[0], at[2]-eye[2]) / (2*math.pi) * 65536
    return yaw % 65536, math.hypot(at[0]-eye[0], at[2]-eye[2]), eye[1]-at[1]
for k in (0, 30, 60, 90, 120, 150, 200, 300, 400):
    g.load("/dev/shm/_hw.m64"); g.run([(k, 0, 0, 0)]) if k else None
    yaw, dist, h = camgeo()
    g.run([(4, R, 0, 0), (8, R, -80, 0), (1, 0, -80, 0), (1, A, -80, 0), (8, 0, -80, 0), (25, R, -80, 0), (10, R, 0, 0), (12, 0, 0, 0)])
    x, _, z, f = g.pos()
    print(f"wait {k:3d}: cam yaw(at-eye) {yaw:8.1f} dist {dist:6.2f} height {h:6.2f} | end ({x:.4f},{z:.4f}) facing {f:04X}")
