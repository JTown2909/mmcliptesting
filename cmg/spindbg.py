import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM); g.load(ENTRY); g.run([(6, 0, 0, 0)])
do(g, "Tap L + ESS Rx8"); g.target_untarget_snap(); print("cam after snap", hex(g.cam()), hex(g.u16(LINK+0xBE)))
tr = []; x0,_,z0,_ = g.pos()
g.run([(21, 0, 0, 0), (1, A, 127, 0), (20, R, 127, 0)], tr)
prev=(x0,z0)
out=[]
for s in tr:
    if (s[0],s[2])!=prev: out.append((round(s[0]-prev[0],3), round(s[2]-prev[1],3), hex(s[5]))); prev=(s[0],s[2])
print(out)
