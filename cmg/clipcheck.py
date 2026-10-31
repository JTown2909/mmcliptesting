"""Clip oracle for the chest-minigame counter clip, from exodus's Yes/No grids
(Link's position on the clip frame, keyed by that frame's movement-angle bin) and the
camera drift while walking targeted then spinning untargeted (from imbued's measurements:
untargeted camera angles near 0 creep +0x10 every 1-2 frames toward 0x0000)."""
import csv, glob, os, re, numpy as np
from sim import *
EXO = os.environ.get("EXODUS", "/tmp/claude-0/-home-user-mmcliptesting/a78033bb-8150-5832-a8b0-7d77af0af2f6/scratchpad/ext/Chest-Minigame-Deku-Clip/exodus_csvs")
GRIDS = {}
for f in glob.glob(EXO + "/*.csv"):
    W = int(re.search(r"- ([0-9A-F]{4})\.csv", f).group(1), 16)
    rows = list(csv.reader(open(f, encoding="utf-8-sig")))
    xs = np.array([float(v) for v in rows[0][1:] if v])
    zs, Y = [], []
    for r in rows[1:]:
        if r and r[0]:
            zs.append(float(r[0])); Y.append([v.strip().lower() == "yes" for v in r[1:1 + len(xs)]])
    Y = np.array(Y); zs = np.array(zs)
    yi = np.argwhere(Y)
    GRIDS[W] = dict(xs=xs, zs=zs, Y=Y, box=(xs[yi[:, 1]].min(), xs[yi[:, 1]].max(), zs[yi[:, 0]].min(), zs[yi[:, 0]].max()))
LAST = [(0xFE91, 2), (0xFEA1, 2), (0xFEB1, 2), (0xFEC1, 2), (0xFED1, 2), (0xFEE1, 2), (0xFEF1, 2), (0xFF01, 1),
        (0xFF11, 2), (0xFF21, 2), (0xFF31, 2), (0xFF41, 1), (0xFF51, 2), (0xFF61, 2), (0xFF71, 1), (0xFF81, 1),
        (0xFF91, 2), (0xFFA1, 1), (0xFFB1, 1), (0xFFC1, 1), (0xFFD1, 1), (0xFFE1, 1), (0xFFF1, 1), (0x0000, 10**9)]
APPROACH = {}  # walking camera angle -> (angle of the speed-8 frame, angle of the clip frame)
for i, (w, _) in enumerate(LAST[:-2]):
    w8, n8 = LAST[i + 1]
    w9 = w8 if n8 == 2 else LAST[i + 2][0]
    if (w9 & 0xFFF0) in GRIDS: APPROACH[w] = (w8, w9)

def in_grid(W, x, z):
    G = GRIDS[W & 0xFFF0]
    xs, zs = G["xs"], G["zs"]
    i = int(np.argmin(abs(zs - z))); j = int(np.argmin(abs(xs - x)))
    if abs(zs[i] - z) > (zs[1] - zs[0]) * 0.75 or abs(xs[j] - x) > (xs[1] - xs[0]) * 0.75: return False
    return bool(G["Y"][i, j])

def approach_exact(x, z, w, extra):
    """position on the clip frame after starting to walk (targeted) from rest at (x,z) with camera w."""
    w8, w9 = APPROACH[w]
    x, z = move(F(x), F(z), w, [2, 4, 6, 6] + [6] * extra)
    x, z = move(x, z, w8, [8])
    return float(x), float(z), w9

def candidates(X, Z, W):
    """vectorised prefilter: arrays of rest positions with walking angle W (scalar).
    returns (idx, extra) of entries whose approximate clip-frame position is inside the Yes box."""
    w8, w9 = APPROACH[W]
    G = GRIDS[w9 & 0xFFF0]; x0, x1, z0, z1 = G["box"]
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    sw, cw = float(sinf(W)), float(cosf(W)); s8, c8 = float(sinf(w8)), float(cosf(w8))
    dx = cx - X.astype(np.float64) - 12 * s8; dz = cz - Z.astype(np.float64) - 12 * c8
    t = dx * sw + dz * cw
    e = np.rint((t / 1.5 - 18) / 6)
    ok = (e >= 0) & (e <= 75)
    qx = X + 1.5 * (18 + 6 * e) * sw + 12 * s8; qz = Z + 1.5 * (18 + 6 * e) * cw + 12 * c8
    ok &= (qx > x0 - 0.003) & (qx < x1 + 0.003) & (qz > z0 - 0.03) & (qz < z1 + 0.03)
    idx = np.nonzero(ok)[0]
    return idx, e[idx].astype(int)

def check(x, z, w):
    """exact check for all walk lengths; returns list of extra values that clip."""
    if w not in APPROACH: return []
    out = []
    for i, e in zip(*candidates(np.array([x]), np.array([z]), w)):
        for ee in (e - 1, e, e + 1):
            if 0 <= ee <= 75:
                qx, qz, w9 = approach_exact(x, z, w, ee)
                if in_grid(w9, qx, qz): out.append(ee)
    return out

if __name__ == "__main__":
    print(sorted(hex(k) for k in APPROACH))
    print(check(-235.5843963623047, 254.25750732421875, 0xFFA1), "(want 59)")
