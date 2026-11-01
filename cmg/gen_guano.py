"""Guano shield-scoot chains (imbued's guano_shield_scoot): from a settled camera, untarget/retarget
to reset the chain, then N scoots left or right while holding Z. Records per-frame movement for each
prefix N = 1..6. One JSON line per facing bin, moves GuanoL<N>/GuanoR<N>."""
import sys, json, struct, glob; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
part, nparts = int(sys.argv[1]), int(sys.argv[2])
g = G(ROM); g.load(ENTRY); g.run([(4, 0, 0, 0)])
for b_ in (LINK + 0x24, LINK + 0x108):
    g.write(b_, struct.pack(">f", -180.0)); g.write(b_ + 8, struct.pack(">f", 470.0))
g.run([(10, 0, 0, 0)])
base = f"/dev/shm/_gu_base{part}.m64"; g.save(base)
def seth(a, v): g.write(a, struct.pack(">H", v & 0xFFFF))
done = set()
for f in glob.glob(SP + "/guano_*.jsonl"):
    for line in open(f):
        try: done.add(json.loads(line)["a"] >> 4)
        except Exception: pass
out = open(SP + f"/guano_{part}.jsonl", "a")
def rec(fr, n, bt, x, y):
    for _ in range(n):
        x0, z0 = g.f32(LINK + 0x24), g.f32(LINK + 0x2C)
        g.frame(bt, x, y)
        x1, z1 = g.f32(LINK + 0x24), g.f32(LINK + 0x2C)
        if x1 != x0 or z1 != z0: fr.append((g.read(LINK + 0x70, 4).hex(), g.u16(LINK + 0x32), x1 - x0, z1 - z0))
for b in range(part, 4096, nparts):
    if b in done: continue
    a = b * 16
    r = dict(a=a, move={})
    for d, sx in (("L", -80), ("R", 80)):
        g.load(base)
        for o in (0x32, 0xBE, 0xAD4): seth(LINK + o, a)
        g.run([(6, Z, 0, 0)]); g.target_untarget_snap()
        fr = []
        rec(fr, 6, 0, 0, 0); rec(fr, 6, Z, 0, 0)
        for n in range(1, 7):
            rec(fr, 10, Z | R, sx, 0)
            k = 0
            while g.f32(LINK + 0x70) == 0 and k < 12:
                rec(fr, 1, Z, sx, 0); k += 1
            rec(fr, 3, Z | R, sx, 0); rec(fr, 1, Z | R, 0, 0)
            r["move"][f"Guano{d}{n}"] = [list(fr), g.u16(LINK + 0xBE)]
        g.set_input(0, 0, 0)
    out.write(json.dumps(r) + "\n"); out.flush()
