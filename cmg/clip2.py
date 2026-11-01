import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM); g.load(ENTRY); g.run([(6, 0, 0, 0)])
for a in "Tap L + ESS Rx5|SidehopR|Tap DR + ESS Rx3|SpinLt|Tap DR + ESS Rx2|SpinULt|Tap L + ESS Rx6".split("|"): do(g, a)
g.save(SP + "/st/cc_f6d9.m64")
for e in (34,):
    g.load(SP + "/st/cc_f6d9.m64"); tr = []
    g.run(final_walk(e) + [(20, 0, 0, 127)], tr)
    for i, s in enumerate(tr): 
        if s[2] > 760: print(i, f"{s[0]:.4f} {s[2]:.4f} face={s[3]:04X} cam={s[4]:04X} mv={s[5]:04X} spd={s[6]:.3f}")
