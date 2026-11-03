"""Shortest motion sequences between Link angles (JP N64, human), using rylieb/mm-angle-finder's
motion models (motions.py: ESS steps, camera-favoured ESS-up snaps, C-up turns).

Usage: python3 tools/angle_search.py FINDER_DIR TARGET START [START...] [--deku] [--top N]
  FINDER_DIR = clone of https://github.com/rylieb/mm-angle-finder (for motions.py + camera table)
Costs follow the finder: a run of the same ESS/C-up motion costs 0.1 then 0.05 per repeat (one frame).
"""
import sys, os, heapq

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    finder, target, starts = args[0], int(args[1], 16), [int(x, 16) for x in args[2:]]
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 8
    cwd = os.getcwd(); os.chdir(finder); sys.path.insert(0, finder)
    import motions
    os.chdir(cwd)
    moves = {"ess left": motions.ess_left, "ess right": motions.ess_right, "ess up": motions.ess_up_adjust,
             "c-up left": motions.c_up_left, "c-up right": motions.c_up_right}
    if "--deku" in sys.argv:
        moves["deku spin"] = motions.deku_spin; moves["mask transition"] = motions.mask_transition
    base = {"ess left": .1, "ess right": .1, "ess up": .1, "c-up left": 3.05, "c-up right": 3.05,
            "deku spin": .9, "mask transition": 1.5}
    def cost(prev, m):
        if prev == m and m in ("ess left", "ess right", "c-up left", "c-up right"): return .05
        if {prev, m} in ({"ess left", "ess right"}, {"c-up left", "c-up right"}): return 100
        return base[m]
    # Dijkstra over (angle, last motion)
    pq = [(0.0, s, None, ()) for s in starts]; best = {}; found = []
    while pq and len(found) < top:
        c, a, last, path = heapq.heappop(pq)
        if (a, last) in best and best[(a, last)] <= c: continue
        best[(a, last)] = c
        if a == target and path: found.append((c, path)); continue
        if c > 60: break
        for m, fn in moves.items():
            b = fn(a)
            if b is None or b is False: continue
            b &= 0xFFFF
            heapq.heappush(pq, (c + cost(last, m), b, m, path + ((m, b),)))
    for c, path in found:
        steps = []
        for m, b in path:
            if steps and steps[-1][0] == m: steps[-1][1] += 1; steps[-1][2] = b
            else: steps.append([m, 1, b])
        start = (path[0][1] - 0) if False else None
        print(f"cost {c:5.2f}: " + "  ->  ".join(f"{m} x{n} ({b:04X})" for m, n, b in steps))

if __name__ == "__main__":
    main()
