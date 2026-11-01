"""Summarise EXACT setups by several measures: number of inputs groups, ESS taps, tap turns,
spins-in-place, walk frames, and the rough time estimate from rank.py."""
import sys, re
from rank import cost
rows = {}
for line in open(sys.argv[1]):
    if not line.startswith("EXACT"): continue
    body, rest = line[6:].split(" => ")
    acts = [a.strip() for a in body.split("|")]
    e = int(re.findall(r"(?<![a-z])(\d+)(?![\d(])", rest.split("extra=")[1].replace("int64", ""))[0])
    parts = [p.strip() for a in acts for p in a.split(" + ")]
    ess = sum(int(m.group(1)) for p in parts for m in [re.match(r"ESS [LR]x(\d+)", p)] if m)
    taps = sum(p.startswith("Tap") for p in parts)
    sip = sum(int(m.group(1)) for p in parts for m in [re.match(r"SpinInPlace x(\d+)", p)] if m)
    moves = len(parts) - sum(bool(re.match(r"ESS|Tap|SpinInPlace", p)) for p in parts)
    key = " | ".join(acts)
    rows[key] = dict(s=key, steps=len(parts), ess=ess, taps=taps, sip=sip, moves=moves, extra=e, t=cost(acts, e))
R = list(rows.values())
print(len(R), "distinct exact setups")
for title, k in [("time estimate", lambda r: r["t"]), ("fewest steps", lambda r: (r["steps"], r["ess"], r["t"])),
                 ("fewest ESS taps", lambda r: (r["ess"], r["steps"], r["t"])), ("no ESS, fewest steps", None)]:
    sel = sorted([r for r in R if r["ess"] == 0], key=lambda r: (r["steps"], r["t"])) if k is None else sorted(R, key=k)
    print(f"\n== {title}")
    for r in sel[:int(sys.argv[2]) if len(sys.argv) > 2 else 8]:
        print(f"  t={r['t']:5.2f} steps={r['steps']:2d} ess={r['ess']:2d} taps={r['taps']} sip={r['sip']} walk={r['extra']:2d}  {r['s']}")
