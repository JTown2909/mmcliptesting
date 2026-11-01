"""Rank setups by (estimated time, steps). Steps: tap turn 1, ESS group 1, each spin in place 1,
each guano scoot 1, every other move 1. Input: recon output (EXACT lines) or verify_batch CLIP lines."""
import sys, re
from rank import cost
def parse(line):
    if line.startswith("EXACT"):
        body, rest = line[6:].split(" => "); ex = rest.split("extra=")[1]
    elif line.startswith("CLIP"):
        body, rest = line[5:].split(" end="); ex = rest.split("walk extras=")[1]
    else: return None
    acts = [a.strip() for a in body.split("|")]
    e = [int(v) for v in re.findall(r"\d+", ex.replace("int64", ""))]
    if not e: return None
    steps = 0
    for a in acts:
        for p in a.split(" + "):
            p = p.strip()
            m = re.match(r"(SpinInPlace x|Guano[LR])(\d+)", p)
            steps += int(m.group(2)) if m else 1
    return cost(acts, min(e)), steps, min(e), " | ".join(acts)
if __name__ == "__main__":
    rows = {}
    for line in open(sys.argv[1]):
        r = parse(line)
        if r: rows[r[3]] = r
    R = list(rows.values())
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    mode = sys.argv[3] if len(sys.argv) > 3 else "time"
    key = (lambda r: (r[0], r[1])) if mode == "time" else (lambda r: (r[1], r[0]))
    for r in sorted(R, key=key)[:n]:
        print(f"{r[0]:5.2f}s steps={r[1]:2d} walk={r[2]:2d}  {r[3]}" if mode != "list" else r[3])
