import sys, math, struct; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
g = G(ROM); g.load(ENTRY); g.run([(4,0,0,0)])
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
def camyaw():
    c = PLAY + 0x220
    at = [g.f32(c + 0x50 + 4*i) for i in range(3)]; eye = [g.f32(c + 0x5C + 4*i) for i in range(3)]
    return int(round(math.atan2(at[0]-eye[0], at[2]-eye[2]) / (2*math.pi) * 65536)) & 0xFFFF
def show(t): print(t, f"facing={g.u16(LINK+0xBE):04X} e7c={g.u16(0x803E6E7C):04X} fb2={g.u16(0x803E6FB2):04X} atan={camyaw():04X}")
show("entry")
for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, 0x3000)
for i in range(8): g.frame(Z); show(f"Z{i}")
for i in range(20): g.frame(0); show(f"n{i}")
c = PLAY + 0x220
print([hex(o) for o in range(0, 0x200, 2) if g.u16(c + o) in (0x300C, 0x300B, 0x300D)])
