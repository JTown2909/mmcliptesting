import sys; sys.path.insert(0, ".")
from verify import *
g = G(ROM)
g.load(ENTRY); g.run([(6, 0, 0, 0)]); g.target_untarget_snap(); g.run([(1, 0, 0, 0)]); g.save("/dev/shm/_st.m64")
for pre in (1, 3, 6):
    for hold in (1, 3, 8):
        for rel in ("stick first", "R first(2f)", "both"):
            g.load("/dev/shm/_st.m64"); tr = []
            seq = [(pre, R, 0, 0), (hold, R, -69, -69)]
            if rel == "stick first": seq += [(3, R, 0, 0)]
            elif rel == "R first(2f)": seq += [(2, 0, -69, -69)]
            seq += [(20, 0, 0, 0)]
            g.run(seq, tr); x, y, z, f = g.pos()
            mid = sorted({s[3] for s in tr})
            print(f"R {pre}f, R+DL {hold}f, release {rel:12s}: facing={f:04X} pos=({x:.3f},{z:.3f}) facings seen {[hex(v) for v in mid]}")
