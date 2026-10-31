import sys, json, math, hashlib, os; sys.path.insert(0,'/home/user/mmcliptesting/emu'); sys.path.insert(0,'.'); from game import *
import importlib
part,nparts,adir=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
crit=importlib.import_module(sys.argv[4])
NEAR=float(sys.argv[5])
HOLDF=int(sys.argv[6]) if len(sys.argv)>6 else 90
MINSPD=float(sys.argv[7]) if len(sys.argv)>7 else 5.0
g=Game('rom/kz.z64')
NOTCH={'U':(0,80),'UR':(56,56),'R':(80,0),'DR':(56,-56),'D':(0,-80),'DL':(-56,-56),'L':(-80,0),'UL':(-56,56)}
anchors=sorted(json.load(open(adir+'/anchors.json')).items())[part::nparts]
tmp='/dev/shm/br_%s_%d.m64'%(os.path.basename(adir),part)
hits=0; tested=0
for seq,fn in anchors:
    for Y in NOTCH:
        hold=NOTCH[Y]
        g.load(adir+'/'+fn); seen=set(); k=0
        while k < HOLDF:
            p=g.pos()
            h=hashlib.md5(g.read(LINK+0x24,12)+g.read(LINK+0xBE,2)+g.read(LINK+0x70,4)+g.read(LINK+0xAD4,2)+g.read(PLAY+0x220+0x50,24)).digest()
            if math.hypot(p[0]-crit.CORNER[0],p[2]-crit.CORNER[1])<NEAR and g.f32(LINK+0x70)>=MINSPD and h not in seen:
                seen.add(h)
                g.set_input(0,*hold); g.save(tmp); k+=1        # frame k (hold) runs inside save
                det=crit.ClipDetector(); tested+=1
                g.frame(A,*hold)                               # A held on frame k
                for i in range(15):
                    q=g.pos()
                    if det.feed(q[0],q[2]): break
                    g.frame(0,*hold)
                if det.hit:
                    hits+=1; print('HIT anchor',seq or '-','hold',Y,'A on hold frame',k,'clip+',i,[round(v,2) for v in q[:3]],flush=True)
                g.load(tmp)
            else:
                g.frame(0,*hold); k+=1
    print('anchor done',seq,'tested',tested,flush=True)
print('done',part,'tested',tested,'hits',hits,flush=True)
