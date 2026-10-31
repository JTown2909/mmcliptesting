"""Map which post-move positions Q the wall collision pushes 'behind' the corner.
Link stands still; every frame we teleport him (pos and prevPos) to Q and read where he ends up."""
import sys, struct; sys.path.insert(0,'/home/user/mmcliptesting/emu'); sys.path.insert(0,'.'); from game import *
import importlib
crit=importlib.import_module(sys.argv[1]); state=sys.argv[2]
x0,x1,dx=map(float,sys.argv[3].split(':')); z0,z1,dz=map(float,sys.argv[4].split(':'))
pz=float(sys.argv[5]) if len(sys.argv)>5 else 0.0     # prevPos z offset
g=Game('rom/kz.z64'); g.load(state); g.frame(0,0,0,n=2)
y=g.pos()[1]
g.set_input(0); g.save('/dev/shm/qmap_base.m64')
z=z0
while z<=z1+1e-6:
    row=''; x=x0
    while x<=x1+1e-6:
        g.write(LINK+0x24, struct.pack('>fff',x,y,z)); g.write(LINK+0x108, struct.pack('>fff',x,y,z-pz))
        g.frame(0,0,0); p=g.pos()
        b=crit.behind(p[0],p[2])
        row+= '#' if b>3 else ('+' if abs(p[0]-x)>0.01 or abs(p[2]-z)>0.01 else '.')
        if b>3: g.load('/dev/shm/qmap_base.m64')
        x+=dx
    print('%7.2f %s'%(z,row),flush=True); z+=dz
