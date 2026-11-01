import sys, struct; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
g = G(ROM); g.load(ENTRY); g.run([(6,0,0,0)])
g.run(ess(7, False)); g.run([(6, Z, 0, 0)])
for i in range(10):
    x0 = g.f32(LINK+0x24); g.frame(Z|A if i==0 else Z|R_TRIG, -128, 0); x1 = g.f32(LINK+0x24)
    vx = g.f32(LINK+0x5C)
    print(i, x1-x0, vx, struct.unpack('>f', struct.pack('>f', vx*1.5))[0], g.f32(LINK+0x70))
