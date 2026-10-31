"""Replay an action list (as printed by search.py) in the emulator and test the clip.
usage: verify.py "ESS Rx7 | ScootFwd | ..." extra"""
import sys, re; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *

# stick for camera-relative angle k*0x2000 (0=up, 0x4000=left, ...)
NOTCH8 = [(0, 127), (-90, 90), (-128, 0), (-90, -90), (0, -128), (90, -90), (127, 0), (90, 90)]
def do(g, a):
    a = a.strip()
    if not a: return
    if "+" in a:
        for p in a.split("+"): do(g, p)
        return
    m = re.match(r"ESS ([LR])x(\d+)", a)
    if m: g.run(ess(int(m.group(2)), m.group(1) == "L")); return
    m = re.match(r"Card (\w+)", a)
    if m: cardinal(g, m.group(1)); return
    m = re.match(r"SpinInPlace x(\d+)", a)
    if m: g.run(spin_in_place(int(m.group(1)))); return
    if a == "SidehopL": g.run(hold_sidehop(True)); return
    if a == "SidehopR": g.run(hold_sidehop(False)); return
    if a == "ScootFwd": g.run(shield_scoot_forward()); return
    if a == "Backflip": g.run(hold_backflip()); return
    if a == "CornerSE":
        g.run([(6, Z, 0, 0)]); c = g.cam()
        k = min(range(8), key=lambda k: abs(((c + k * 0x2000) & 0xFFFF) - 0x6000))
        sx, sy = NOTCH8[k]
        g.run([(150, Z, sx, sy), (10, Z, 0, 0), (30, 0, 0, 0)]); return
    if a == "BackWall": g.run([(6, Z, 0, 0), (150, Z, 0, -128), (10, Z, 0, 0), (30, 0, 0, 0)]); return
    raise ValueError(a)

def verify(actions, extra, verbose=True, g=None):
    g = g or G(ROM)
    g.load(ENTRY); g.run([(6, 0, 0, 0)])
    for a in actions:
        do(g, a)
        if verbose:
            x, y, z, f, c, m, s = g.st(); print(f"  {a:34s} x={x:.6f} z={z:.6f} facing={f:04X} cam={c:04X}")
    tr = []
    g.run(final_walk(extra) + [(20, 0, 0, 127)], tr)
    ok = max(s[2] for s in tr) > 845
    if verbose: print("  CLIP" if ok else "  no clip", [(round(s[0], 4), round(s[2], 4)) for s in tr[-30:-24]])
    return ok

if __name__ == "__main__":
    acts = [s for s in sys.argv[1].split("|")]
    verify(acts, int(sys.argv[2]))
