"""Build deterministic 'anchor' states from a start state using ESS turns and Z camera resets.
usage: anchors.py START.m64 OUTDIR depth"""
import sys, os, json, hashlib; sys.path.insert(0,'/home/user/mmcliptesting/emu'); from game import *
ESS={'U':(0,20),'UR':(14,14),'R':(20,0),'DR':(14,-14),'D':(0,-20),'DL':(-14,-14),'L':(-20,0),'UL':(-14,14)}
start,outdir,depth=sys.argv[1],sys.argv[2],int(sys.argv[3])
os.makedirs(outdir,exist_ok=True)
g=Game('rom/kz.z64')
def key():
    return hashlib.md5(g.read(LINK+0x24,12)+g.read(LINK+0xBE,2)+g.read(PLAY+0x220+0x50,24)).hexdigest()
def apply(prim):
    if prim=='Z': g.frame(Z,0,0); g.frame(0,0,0,n=20)
    else: g.frame(0,*ESS[prim],n=30); g.frame(0,0,0,n=2)
g.load(start); g.frame(0,0,0,n=2)
seen={key():[]}; frontier=[[]]; anchors=[[]]
g.set_input(0); g.save(os.path.join(outdir,'a0.m64'))
files={'':'a0.m64'}
for d in range(depth):
    nf=[]
    for seq in frontier:
        for prim in ['Z']+list(ESS):
            if seq and seq[-1]==prim: continue
            g.load(os.path.join(outdir,files['/'.join(seq)])); apply(prim)
            k=key()
            if k in seen: continue
            ns=seq+[prim]; seen[k]=ns
            fn='a%d.m64'%len(files); files['/'.join(ns)]=fn
            g.set_input(0); g.save(os.path.join(outdir,fn))
            nf.append(ns); anchors.append(ns)
    frontier=nf
    print('depth',d+1,'anchors',len(anchors),flush=True)
json.dump({'/'.join(s):files['/'.join(s)] for s in anchors},open(os.path.join(outdir,'anchors.json'),'w'),indent=0)
