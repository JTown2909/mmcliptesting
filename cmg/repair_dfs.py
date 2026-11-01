"""Repair step-budget candidates: for each candidate, replay in the emulator up to (and including) each
shield spin / guano scoot, then re-run the step-budget DFS from the emulator's exact state with the
remaining budget. Prints full action lists of exact hits (for verify_batch).
usage: repair_dfs.py tablesdir hitsfile budget maxess out"""
import sys, os, json, subprocess, shutil; sys.path.insert(0, ".")
from verify import *
TD, HF, BUD, MAXESS, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
N = json.load(open(TD + "/names.json"))
SP_ = "/tmp/claude-0/-home-user-mmcliptesting/a78033bb-8150-5832-a8b0-7d77af0af2f6/scratchpad"
work = SP_ + f"/rdfs_{os.getpid()}"; os.makedirs(work, exist_ok=True)
for f in os.listdir(TD):
    if f.endswith(".bin") or f == "names.json": shutil.copy(f"{TD}/{f}", work)
import re
def tcost(n): return sum(int(m.group(1)) if (m := re.match(r"SpinInPlace x(\d+)", p.strip())) else 1 for p in n.split(" + ") if p.strip())
def mcost(n): return int(m.group(1)) if (m := re.match(r"Guano[LR](\d)", n)) else 1
g = G(ROM); out = open(OUT, "a"); seen = set()
for line in open(HF):
    left, right = line.split("|")
    steps = [tuple(int(v) for v in p.split(",")) for p in left.split()]
    for cut in range(1, len(steps) + 1):
        t, m = steps[cut - 1]
        if not (N["moves"][m].startswith("HSpin") or N["moves"][m].startswith("Guano")): continue
        prefix = steps[:cut]
        if tuple(prefix) in seen: continue
        seen.add(tuple(prefix))
        acts = []
        for tt, mm in prefix:
            if N["turns"][tt]: acts.append(N["turns"][tt])
            acts.append(N["moves"][mm])
        used = sum(tcost(N["turns"][tt]) if N["turns"][tt] else 0 for tt, _ in prefix) + sum(mcost(N["moves"][mm]) for _, mm in prefix)
        ess_used = sum(1 for tt, _ in prefix if "ESS" in N["turns"][tt])
        g.load(ENTRY); g.run([(6, 0, 0, 0)])
        for a in acts: do(g, a)
        x, y, z, f = g.pos()
        rem = BUD - used
        if rem < 0: continue
        subprocess.run([os.path.abspath("c/dfs"), work, str(rem), str(MAXESS - ess_used), repr(x), repr(z), str(f)], capture_output=True)
        hf = f"{work}/dfs_hits_{rem}.txt"
        if not os.path.exists(hf) or os.path.getsize(hf) == 0: continue
        r = subprocess.run(["python3", "recon_dfs.py", work, repr(x), repr(z), str(f)], capture_output=True, text=True,
                           env=dict(os.environ, CARD_ONLY="1", HSPIN="1", GUANO="1", DFS_HITS=hf))
        for l in r.stdout.splitlines():
            body = l[6:].split(" => ")[0].split("] ", 1)[1]
            out.write(" | ".join(acts) + " | " + body + "\n"); out.flush()
print("done")
