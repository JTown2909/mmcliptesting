"""Rebuild candidate paths from c/search output, re-check them exactly (fp32), print action lists."""
import sys, os, glob, json, numpy as np
from sim import *
from clipcheck import APPROACH, check
SP = "/tmp/claude-0/-home-user-mmcliptesting/a78033bb-8150-5832-a8b0-7d77af0af2f6/scratchpad"
D = sys.argv[1] if len(sys.argv) > 1 else SP + "/cs"
x0, z0, a0 = (float(v) for v in (sys.argv[2:5] if len(sys.argv) > 4 else (-70, 209.75, 0)))
N = json.load(open(D + "/names.json"))
TURNS = np.fromfile(D + "/turns.bin", dtype=np.uint16).reshape(-1, 65536)
MT = {}
for f in glob.glob(SP + "/moves_*.jsonl"):
    for line in open(f):
        r = json.loads(line); MT[r["a"] >> 4] = r
HSPIN = bool(os.environ.get("HSPIN"))
if HSPIN:
    for f in glob.glob(SP + "/hspin_*.jsonl"):
        for line in open(f):
            r = json.loads(line)
            mv = MT[r["a"] >> 4]["move"]
            for k in [k for k in mv if k.startswith("Spin")]: del mv[k]
            mv.update(r["move"])
if os.environ.get("GUANO"):
    for f in glob.glob(SP + "/guano_*.jsonl"):
        for line in open(f):
            r = json.loads(line); MT[r["a"] >> 4]["move"].update(r["move"])
camt = np.array([MT[b]["camt"] for b in range(4096)])
camx = {}
for f in glob.glob(SP + "/camexact_*.csv"):
    for line in open(f):
        a, c = line.strip().split(","); camx[int(a, 16)] = int(c, 16)
ST = np.dtype(dict(names=["x", "z", "a", "par", "t", "m"], formats=["<f8", "<f8", "<u2", "<i4", "<i2", "<i2"],
                   offsets=[0, 8, 16, 20, 24, 26], itemsize=32))
LV = {}
def level(L):
    if L not in LV: LV[L] = np.fromfile(f"{D}/level{L}.bin", dtype=ST)
    return LV[L]
def path(L, i):
    out = []
    while L > 0:
        s = level(L)[i]; out.append((int(s["t"]), int(s["m"]))); i = int(s["par"]); L -= 1
    return out[::-1]
def exact(steps):
    x, z, a = F(x0), F(z0), int(float(a0))
    for t, m in steps:
        a = int(TURNS[t][a]); name = N["moves"][m]
        if name == "CornerSE": x, z = F(66), F(134); continue
        if name == "BackWall": z = F(134); continue
        fr, ff = MT[a >> 4]["move"][name]
        for sp, ang, _, _ in fr:
            v = np.frombuffer(bytes.fromhex(sp), dtype=">f4")[0].astype(F)
            x, z = move(x, z, ang, [v])
        if name.startswith(("Spin", "HSpin")): a = ff
    return x, z, a
seen = set()
for line in open(D + "/hits.txt"):
    L, idx, par, t, m, ft, x, z, e = line.split()
    L, idx, par, t, m, ft = map(int, (L, idx, par, t, m, ft))
    if idx >= 0: steps = path(L, idx)
    elif idx == -1: steps = path(L - 1, par) + [(t, m)]
    else: steps = path(L - 2, par) + [(t // 64, t % 64), (m // 64, m % 64)]
    key = (tuple(steps), ft)
    if key in seen: continue
    seen.add(key)
    X, Zz, a = exact(steps)
    f = int(TURNS[ft][a]); w = camx.get(f, int(camt[f >> 4]))
    if w not in APPROACH: w += 1
    ex = check(float(X), float(Zz), w)
    acts = []
    for tt, mm in steps:
        if N["turns"][tt]: acts.append(N["turns"][tt])
        acts.append(N["moves"][mm])
    if N["turns"][ft]: acts.append(N["turns"][ft])
    print("EXACT" if ex else "near ", " | ".join(acts), f"=> ({float(X):.6f},{float(Zz):.6f}) facing={f:04X} walk={w:04X} extra={ex}", flush=True)
