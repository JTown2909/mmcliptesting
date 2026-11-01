import sys, math; sys.path.insert(0, ".")
from prims import *
g = G(ROM); g.load(ENTRY); g.run([(6,0,0,0)])
import struct
for b in (LINK+0x24, LINK+0x108): g.write(b, struct.pack(">f",-700.0)); g.write(b+8, struct.pack(">f",465.0))
g.run([(20,0,0,0)])
def d():
    c = PLAY + 0x220; eye = [g.f32(c + 0x5C + 4*i) for i in range(3)]
    x,y,z,a = g.pos(); return round(math.hypot(eye[0]-x, eye[2]-z),1)
print("idle", d()); g.run([(6,Z,0,0)]); print("target", d())
g.target_untarget_snap()
mx=0
for n,b,x,y in [(21,0,0,0),(1,A,127,0),(20,R,127,0)]:
    for _ in range(n): g.frame(b,x,y); mx=max(mx,d())
print("spin max", mx)
