"""Rank EXACT setups from recon output by a rough human execution-time estimate (seconds).
Costs are guesses for comparison only: ESS group 0.6 + 0.25/tap, tap turn 1.2 (target/untarget,
camera settle), spin in place 1.3 each, sidehop 0.7, scoot 0.6, backflip 1.0, directional spin 1.3,
corner pin 2.5, back-wall pin 1.5, final walk (10 + extra) frames at 20 fps."""
import sys, re
def cost(acts, extra):
    c = 0.0
    for a in acts:
        for p in a.split(" + "):
            p = p.strip()
            m = re.match(r"ESS [LR]x(\d+)", p)
            if m: c += 0.6 + 0.25 * int(m.group(1)); continue
            m = re.match(r"SpinInPlace x(\d+)", p)
            if m: c += 1.3 * int(m.group(1)); continue
            if p.startswith("Tap"): c += 1.2; continue
            m = re.match(r"Guano[LR](\d)", p)
            if m: c += 0.6 + 0.8 * int(m.group(1)); continue
            c += {"SidehopL": .7, "SidehopR": .7, "ScootFwd": .6, "Backflip": 1.0, "CornerSE": 2.5, "BackWall": 1.5}.get(p, 1.3)
    return c + (10 + extra) / 20
if __name__ == '__main__':
    rows = []
    for line in open(sys.argv[1]):
        if not line.startswith("EXACT"): continue
        body, rest = line[6:].split(" => ")
        acts = [a.strip() for a in body.split("|")]
        ex = [int(v) for v in re.findall(r"(?<![a-z])(\d+)(?![\d(])", rest.split("extra=")[1].replace("int64", ""))]
        for e in ex[:1]:
            rows.append((cost(acts, e), len(acts), " | ".join(acts), e))
    rows.sort()
    imb = cost("ESS Rx7|ScootFwd|ESS Rx8|SidehopL|ScootFwd|ESS Rx3|SidehopL|Tap D + SpinInPlace x1".split("|"), 59)
    print(f"# imbued's setup: {imb:.2f}s; {len(rows)} exact setups")
    seen = set()
    for c, n, s, e in rows:
        if s in seen: continue
        seen.add(s); print(f"{c:6.2f}  extra={e:2d}  {s}")
