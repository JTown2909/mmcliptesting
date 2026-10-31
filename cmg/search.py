"""Breadth-first search over (turn, move) pairs from the room entry, using the exact fp32
movement model (sim.py), emulator-measured camera/cardinal tables (gen_cam.py) and the
exodus clip grids (clipcheck.py). Every hit is printed as an action list for emulator verification."""
import sys, os, glob, numpy as np
from sim import *
from clipcheck import APPROACH, candidates, check

SP = "/tmp/claude-0/-home-user-mmcliptesting/a78033bb-8150-5832-a8b0-7d77af0af2f6/scratchpad"
camt = np.zeros(4096, np.int64); snap = np.zeros(4096, np.int64); card = np.zeros((3, 4096), np.int64)
for f in glob.glob(SP + "/cam_table_*.csv"):
    for line in open(f):
        v = [int(t, 16) for t in line.strip().split(",")]
        b = v[0] >> 4; camt[b] = v[1]; snap[b] = v[2]; card[0, b], card[1, b], card[2, b] = v[3], v[5], v[7]
assert (camt != 0).sum() > 4000, "camera table incomplete"
DIRS = ["LEFT", "RIGHT", "DOWN"]
ESS = 0x708
def T_ess(k): return lambda A: (A + k * ESS) & 0xFFFF
def T_card(d): return lambda A: card[d, A >> 4]
def T_spin(n): return lambda A: (A - n * 0x1E0) & 0xFFFF
def comp(f, g): return lambda A: g(f(A))
TURNS = [("", lambda A: A)]
ks = [k for k in range(-8, 9) if k]
TURNS += [(f"ESS {'L' if k > 0 else 'R'}x{abs(k)}", T_ess(k)) for k in ks]
for d in range(3):
    TURNS.append((f"Card {DIRS[d]}", T_card(d)))
    TURNS += [(f"Card {DIRS[d]} + ESS {'L' if k > 0 else 'R'}x{abs(k)}", comp(T_card(d), T_ess(k))) for k in ks]
    TURNS += [(f"Card {DIRS[d]} + SpinInPlace x{n}", comp(T_card(d), T_spin(n))) for n in (1, 2)]
TURNS += [(f"SpinInPlace x{n}", T_spin(n)) for n in (1, 2)]
def M_vel(off, vels):
    def f(X, Z, A):
        x2, z2 = move(X, Z, (camt[A >> 4] + off) & 0xFFFF, vels)
        return x2, z2, valid(x2, z2)
    return f
def M_cornerSE(X, Z, A):
    # hold target + the notch pointing into the SE corner until stopped, release stick first:
    # lands on exactly (66, 134) with facing unchanged (verified in emulator, independent of hold length)
    return np.full_like(X, F(66.0)), np.full_like(Z, F(134.0)), np.ones(len(X), bool)
def M_backwall(X, Z, A):
    # target + hold Down straight back into the south wall; exact only if the back direction is exactly -z
    ok = (((camt[A >> 4] + 0x8000) & 0xFFFF) == 0x8000) & (((X > -346) & (X < -114)) | ((X > -26) & (X < 66)))
    return X.copy(), np.full_like(Z, F(134.0)), ok
MOVES = [("SidehopL", M_vel(0x4000, V_SIDEHOP)), ("SidehopR", M_vel(0xC000, V_SIDEHOP)), ("ScootFwd", M_vel(0, V_SCOOT)),
         ("Backflip", M_vel(0x8000, V_BACKFLIP))]
if os.environ.get("WALLS"): MOVES += [("CornerSE", M_cornerSE), ("BackWall", M_backwall)]

def valid(X, Z):
    return (X > -1666) & (X < 66) & (Z > 134) & (Z < 797)

def final_check(X, Z, A, level, hist):
    hits = []
    for tn, tf in TURNS:
        f = tf(A); w = camt[f >> 4]
        for W in np.unique(w):
            if int(W) not in APPROACH: continue
            sel = np.nonzero(w == W)[0]
            idx, e = candidates(X[sel], Z[sel], int(W))
            for i in sel[idx]:
                ex = check(float(X[i]), float(Z[i]), int(W))
                if ex:
                    hits.append((hist(level, i) + ([tn] if tn else []), float(X[i]), float(Z[i]), int(f[i]), int(W), ex))
    return hits

def run(x0, z0, a0, depth, label):
    X = np.array([x0], F); Z = np.array([z0], F); A = np.array([a0], np.int64)
    levels = [(None, None)]  # (parent idx, action idx)
    acts = [(t, m) for t in range(len(TURNS)) for m in range(len(MOVES))]
    def hist(level, i):
        out = []
        while level > 0:
            par, act = levels[level]
            t, m = acts[act[i]]
            out = ([TURNS[t][0]] if TURNS[t][0] else []) + [MOVES[m][0]] + out
            i = par[i]; level -= 1
        return out
    for level in range(depth + 1):
        hits = final_check(X, Z, A, level, hist)
        for h in hits:
            print(label, "L%d" % level, " | ".join(h[0]), f"start=({h[1]:.6f},{h[2]:.6f}) facing={h[3]:04X} walk={h[4]:04X} extra={h[5]}", flush=True)
        print(label, "level", level, "states", len(X), "hits", len(hits), flush=True)
        if level == depth: break
        NX, NZ, NA, NP, NACT = [], [], [], [], []
        for ai, (t, m) in enumerate(acts):
            A2 = TURNS[t][1](A)
            x2, z2, ok = MOVES[m][1](X, Z, A2)
            NX.append(x2[ok]); NZ.append(z2[ok]); NA.append(A2[ok]); NP.append(np.nonzero(ok)[0]); NACT.append(np.full(ok.sum(), ai))
        X = np.concatenate(NX); Z = np.concatenate(NZ); A = np.concatenate(NA)
        par = np.concatenate(NP); act = np.concatenate(NACT)
        key = np.stack([X.view(np.int32).astype(np.int64), Z.view(np.int32).astype(np.int64), A], 1)
        _, first = np.unique(key, axis=0, return_index=True)
        first.sort()
        X, Z, A, par, act = X[first], Z[first], A[first], par[first], act[first]
        levels.append((par, act))

if __name__ == "__main__":
    run(F(-70.0), F(209.75), 0, int(sys.argv[1]) if len(sys.argv) > 1 else 2, "entry")
