"""Spin table for the console method: (camera settled) hold R, hold R + direction, release R,
press A one frame later (direction held), re-press R 8 frames after A, release everything.
One JSON line per facing bin, moves named HSpin<d>."""
import sys, json, struct, glob; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
part, nparts = int(sys.argv[1]), int(sys.argv[2])
N8 = dict(U=(0, 80), UL=(-69, 69), L=(-80, 0), DL=(-69, -69), D=(0, -80), DR=(69, -69), R=(80, 0), UR=(69, 69))
g = G(ROM); g.load(ENTRY); g.run([(4, 0, 0, 0)])
for b_ in (LINK + 0x24, LINK + 0x108):
    g.write(b_, struct.pack(">f", -180.0)); g.write(b_ + 8, struct.pack(">f", 470.0))
g.run([(10, 0, 0, 0)])
base = f"/dev/shm/_zs_base{part}.m64"; g.save(base); S = f"/dev/shm/_zs_s{part}.m64"
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
done = set()
for f in glob.glob(SP + "/zspin_*.jsonl"):
    for line in open(f):
        try: done.add(json.loads(line)["a"] >> 4)
        except Exception: pass
out = open(SP + f"/zspin_{part}.jsonl", "a")
for b in range(part, 4096, nparts):
    if b in done: continue
    a = b * 16
    g.load(base)
    for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, a)
    g.run([(6, Z, 0, 0)]); g.target_untarget_snap(); g.save(S)
    r = dict(a=a, move={})
    for d, (sx, sy) in [(k, N8[k]) for k in ("U", "L", "R")]:
        g.load(S); fr = []
        for n, bt, x, y in [(6, Z, 0, 0), (4, R | Z, 0, 0), (8, R | Z, sx, sy), (1, Z, sx, sy), (1, A | Z, sx, sy), (8, Z, sx, sy), (25, R | Z, sx, sy), (10, R, 0, 0), (12, 0, 0, 0)]:
            for _ in range(n):
                x0, z0 = g.f32(LINK + 0x24), g.f32(LINK + 0x2C)
                g.frame(bt, x, y)
                x1, z1 = g.f32(LINK + 0x24), g.f32(LINK + 0x2C)
                if x1 != x0 or z1 != z0: fr.append((g.read(LINK + 0x70, 4).hex(), g.u16(LINK + 0x32), x1 - x0, z1 - z0))
        g.set_input(0, 0, 0)
        r["move"][f"ZSpin{d}"] = [fr, g.u16(LINK + 0xBE)]
    out.write(json.dumps(r) + "\n"); out.flush()
