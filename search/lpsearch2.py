import sys; sys.path.insert(0,'/home/user/mmcliptesting/emu'); sys.path.insert(0,'.'); from game import *; from lpcrit import ClipDetector
part,nparts=int(sys.argv[1]),int(sys.argv[2])
g=Game('rom/kz.z64')
NOTCH={'U':(0,80),'UR':(56,56),'R':(80,0),'DR':(56,-56),'D':(0,-80),'DL':(-56,-56),'L':(-80,0),'UL':(-56,56)}
ESS={'U':(0,20),'UR':(14,14),'R':(20,0),'DR':(14,-14),'D':(0,-20),'DL':(-14,-14),'L':(-20,0),'UL':(-14,14)}
anchors=[]
for X in [None]+list(ESS):
    for z in (0,1):
        anchors.append((X,z))
anchors=anchors[part::nparts]
hits=0
for X,z in anchors:
    name='/dev/shm/lpA_%s_%d.m64'%(X,z)
    g.load('st/lpE.m64')
    if X: g.frame(0,*ESS[X],n=30)
    if z: g.frame(Z,0,0); g.frame(0,0,0,n=12)
    g.set_input(0); g.save(name)
    for Y in NOTCH:
        for k in range(1,71):
            for post in ('hold','none'):
                g.load(name); det=ClipDetector()
                for i in range(k+16):
                    stick = NOTCH[Y] if (i<=k+1 or post=='hold') else (0,0)
                    g.frame(A if i==k else 0, *stick); q=g.pos()
                    if det.feed(q[0],q[2]): break
                if det.hit:
                    hits+=1; print('HIT ess',X,'Z',z,'hold',Y,'A@',k,post,'at frame',i,[round(v,2) for v in q[:3]],flush=True)
print('done',part,'hits',hits,flush=True)
