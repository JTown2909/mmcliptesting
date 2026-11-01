"""Repair near-miss setups: replay the first p (turn, move) pairs in the emulator, then re-search the
remaining pairs with the C search starting from the emulator's exact state, and verify the results.
usage: repair.py tablesdir failing_list.txt out.txt"""
import sys, os, json, subprocess, shutil; sys.path.insert(0, ".")
from verify import *
TD, FL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
N = json.load(open(TD + "/names.json")); MOVES = set(N["moves"])
SP_ = "/tmp/claude-0/-home-user-mmcliptesting/a78033bb-8150-5832-a8b0-7d77af0af2f6/scratchpad"
work = SP_ + f"/repair_{os.getpid()}"; os.makedirs(work, exist_ok=True)
for f in ("turns.bin", "moves.bin", "movekind.bin", "final.bin", "rays.bin", "turnkind.bin", "names.json"): shutil.copy(f"{TD}/{f}", work)
g = G(ROM); out = open(OUT, "a")
def pairs(acts):
    P, cur = [], []
    for a in acts:
        cur.append(a)
        if a in MOVES: P.append(cur); cur = []
    return P, cur
seen = set()
for line in open(FL):
    acts = [a.strip() for a in line.strip().split("|") if a.strip()]
    P, tail = pairs(acts)
    for p in (2, 3):
        if p >= len(P): continue
        prefix = [a for pr in P[:p] for a in pr]
        key = tuple(prefix)
        if key in seen: continue
        seen.add(key)
        g.load(ENTRY); g.run([(6, 0, 0, 0)])
        for a in prefix: do(g, a)
        x, y, z, f = g.pos()
        depth = 4 - p
        for fn in os.listdir(work):
            if fn.startswith("level") or fn == "hits.txt": os.remove(os.path.join(work, fn))
        subprocess.run([os.path.abspath("c/search"), work, str(depth), repr(x), repr(z), str(f)], capture_output=True)
        r = subprocess.run(["python3", "recon.py", work, repr(x), repr(z), str(f)], capture_output=True, text=True,
                           env=dict(os.environ, CARD_ONLY="1", HSPIN="1", GUANO="1"))
        for l in r.stdout.splitlines():
            if not l.startswith("EXACT"): continue
            suffix = l[6:].split(" => ")[0]
            full = " | ".join(prefix) + " | " + suffix
            out.write(full + "\n"); out.flush()
print("done")
