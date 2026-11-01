"""Replay an action list (as printed by search.py) in the emulator and test the clip.
usage: verify.py "ESS Rx7 | ScootFwd | ..." extra"""
import sys, re; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *

# stick for camera-relative angle k*0x2000 (0=up, 0x4000=left, ...)
N8 = dict(U=(0, 127), UL=(-90, 90), L=(-128, 0), DL=(-90, -90), D=(0, -128), DR=(90, -90), R=(127, 0), UR=(90, 90))
H8 = dict(U=(0, 80), UL=(-69, 69), L=(-80, 0), DL=(-69, -69), D=(0, -80), DR=(69, -69), R=(80, 0), UR=(69, 69))
NOTCH8 = [(0, 127), (-90, 90), (-128, 0), (-90, -90), (0, -128), (90, -90), (127, 0), (90, 90)]
def do(g, a):
    a = a.strip()
    if not a: return
    if "+" in a and not a.startswith("Tap"):
        for p in a.split("+"): do(g, p)
        return
    m = re.match(r"ESS ([LR])x(\d+)", a)
    if m: g.run(ess(int(m.group(2)), m.group(1) == "L")); return
    if a.startswith("Tap") and "+" in a:
        p, q = a.split("+", 1); do(g, p); do(g, q); return
    m = re.match(r"Tap (\w+)", a)
    if m:
        sx, sy = N8[m.group(1)]
        g.target_untarget_snap(); g.run([(1, 0, 0, 0), (1, 0, sx, sy)]); g.target_untarget_snap(); return
    m = re.match(r"Scoot([LR])(\d)$", a)
    if m:  # sideways shield scoot chain, earliest re-shield (3-frame release), chain reset first
        sx = -80 if m.group(1) == "L" else 80
        g.target_untarget_snap(); g.run([(6, 0, 0, 0), (6, Z, 0, 0)])
        for _ in range(int(m.group(2))):
            g.run([(10, Z | R, sx, 0), (3, Z, sx, 0), (4, Z | R, sx, 0), (1, Z | R, 0, 0)])
        g.run([(10, 0, 0, 0)]); return
    m = re.match(r"Guano([LR])(\d)$", a)
    if m:  # imbued's guano shield scoot chain, chain reset first
        sx = -80 if m.group(1) == "L" else 80
        g.target_untarget_snap(); g.run([(6, 0, 0, 0), (6, Z, 0, 0)])
        for _ in range(int(m.group(2))):
            g.run([(10, Z | R, sx, 0)]); k = 0
            while g.f32(LINK + 0x70) == 0 and k < 12: g.run([(1, Z, sx, 0)]); k += 1
            g.run([(3, Z | R, sx, 0), (1, Z | R, 0, 0)])
        g.run([(10, 0, 0, 0)]); return
    m = re.match(r"ZSpin(U|L|R)$", a)
    if m:  # targeted shield spin: hold Z throughout, shield + direction, release shield, A one frame later
        sx, sy = H8[m.group(1)]
        g.target_untarget_snap()
        g.run([(6, Z, 0, 0), (4, R | Z, 0, 0), (8, R | Z, sx, sy), (1, Z, sx, sy), (1, A | Z, sx, sy), (8, Z, sx, sy), (25, R | Z, sx, sy), (10, R, 0, 0), (12, 0, 0, 0)])
        g.target_untarget_snap(); return
    m = re.match(r"HSpin(U|UL|L|DL|D|DR|R|UR)$", a)
    if m:  # console method: shield, hold direction, release shield, A one frame later, re-shield
        sx, sy = H8[m.group(1)]
        g.target_untarget_snap()
        g.run([(4, R, 0, 0), (8, R, sx, sy), (1, 0, sx, sy), (1, A, sx, sy), (8, 0, sx, sy), (25, R, sx, sy), (10, R, 0, 0), (12, 0, 0, 0)])
        g.target_untarget_snap(); return
    m = re.match(r"Spin(U|UL|L|DL|D|DR|R|UR)(t?)$", a)
    if m:
        sx, sy = N8[m.group(1)]
        g.target_untarget_snap()
        g.run([(21, 0, 0, 0)] + ([(1, 0, sx, sy)] if m.group(2) else []) + [(1, A, sx, sy), (20, R, sx, sy)])
        g.target_untarget_snap(); return
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
    if a == "CornerSE":  # cardinal-only: target + the cardinal toward the east wall, then toward the south wall
        g.run([(6, Z, 0, 0)]); c = g.cam()
        C4 = [(0, 80), (-80, 0), (0, -80), (80, 0)]  # stick for camera-relative 0, +0x4000, +0x8000, +0xC000
        def best(target):
            return min(range(4), key=lambda k: abs(((c + k * 0x4000 - target + 0x8000) & 0xFFFF) - 0x8000))
        kx, kz = best(0x4000), best(0x8000)
        g.run([(300, Z) + C4[kx], (400, Z) + C4[kz], (10, Z, 0, 0), (30, 0, 0, 0)]); return
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
    ok = any(s[2] > 845 and s[0] > -240 for s in tr)
    if verbose: print("  CLIP" if ok else "  no clip", [(round(s[0], 4), round(s[2], 4)) for s in tr[-30:-24]])
    return ok

if __name__ == "__main__":
    acts = [s for s in sys.argv[1].split("|")]
    verify(acts, int(sys.argv[2]))
