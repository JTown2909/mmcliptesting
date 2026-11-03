"""Re-simulate the runner's movie heap events from frame 255 and compare with real RAM snapshots.
Usage: python3 tools/route_check.py DUMPDIR   (DUMPDIR has frameN.rdram from bk2replay.py --dump)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from heapsim import *

# Traced from the runner's daytime movie (game frames). Initial state = frame 255 (pot room loaded,
# its door at 0x8040B3B0, one bomb out at 0x804146A0). Bombs belong to the room they are pulled in.
INIT = [("adopt", "En_Door", 0x8040B3B0, "door0", "pot"), ("adopt", "En_Bom", 0x804146A0, "b0")]
MOVIE_EVENTS = [
    (257, "enter torch room (1st trip)",     [("load", "torch", False)]),
    (282, "pot room unloads",                [("unload", "pot")]),
    (295, "bomb explodes",                   [("spawn", "En_Clear_Tag", "c1")]),
    (306, "bomb actor removed",              [("kill", "b0")]),
    (331, "back to pot room",                [("load", "pot", True),
                                              # unexplained one-time top-of-heap blocks on the 1st re-entry
                                              ("rawR", 0x520), ("rawR", 0x420)]),
    (360, "explosion ends, torch unloads",   [("kill", "c1"), ("unload", "torch")]),
    (375, "pull 2 bombs (pot room)",         [("spawn", "En_Bom", "b1", "pot"), ("spawn", "En_Bom", "b2")]),
    (396, "enter torch room (2nd trip)",     [("load", "torch", False)]),
    (421, "pot room unloads",                [("unload", "pot")]),
    (444, "EXPLOSION 1",                     [("spawn", "En_Clear_Tag", "c2")]),
    (455, "bomb actor removed",              [("kill", "b2")]),
    (481, "pull 3 bombs (torch room)",       [("spawn", "En_Bom", "b3", "torch"), ("spawn", "En_Bom", "b4", "torch"),
                                              ("spawn", "En_Bom", "b5", "torch")]),
    (502, "back to pot room (target pot)",   [("load", "pot", True)]),
    (514, "explosion 1 ends",                [("kill", "c2")]),
    (532, "torch room unloads",              [("unload", "torch")]),
    (709, "pull bomb",                       [("spawn", "En_Bom", "b6", "pot")]),
    (778, "EXPLOSION 2",                     [("spawn", "En_Clear_Tag", "c3")]),
    (790, "bomb actor removed",              [("kill", "b6")]),
    (782, "second pot destroyed",            [("killroomactor", "pot", "Obj_Tsubo", 1)]),
    (797, "pick up first pot (target)",      [("mark", "target", "pot", "Obj_Tsubo", 0)]),
    (798, "carry pot into torch room",       [("load", "torch", False)]),
    (809, "explosion 2 ends, pot room unloads (SRM)", [("kill", "c3"), ("unload", "pot")]),
    (855, "back to pot room: Moon Stone",    [("load", "pot", True)]),
]

def verdict(r):
    """Success = Moon Stone instance exactly 0x80 before the carried pot's instance, with its code in 0x8040xxxx."""
    moon = [n for n, s, f, l in r.heap.blocks if l == "Obj_Moon_Stone"]
    tgt = r.tags.get("target")
    ovl = r.ovl["Obj_Moon_Stone"][0]
    ok = bool(moon) and tgt is not None and moon[-1] == tgt[1] - 0x80 and ovl is not None and (ovl + NODE) >> 16 == 0x8040
    return (f"Moon Stone node {hex(moon[-1]) if moon else None}, carried pot node {hex(tgt[1]) if tgt else None}, "
            f"Moon Stone code {hex(ovl + NODE) if ovl else None} -> {'WORKS' if ok else 'fails'}"), ok

def run(r, events, check=None, verbose=True):
    for f, desc, evs in events:
        for e in evs: r.do(e)
        if check:
            so, ro = layout_diff(r.heap, check(f))
            if verbose:
                print(f"frame {f:4d} {desc:42s} {'MATCH' if not so and not ro else 'differs'}")
                if so or ro:
                    print("     sim only :", [(hex(a), hex(b), c) for a, b, c in so][:5])
                    print("     real only:", [(hex(a), hex(b), c) for a, b, c in ro][:5])
    return r

if __name__ == "__main__":
    dd = sys.argv[1]
    D = lambda f: open(os.path.join(dd, f"frame{f}.rdram"), "rb").read()
    r = Route(D(255), "pot")
    for e in INIT: r.do(e)
    have = {int(n[5:-6]) for n in os.listdir(dd) if n.startswith("frame")}
    run(r, MOVIE_EVENTS, check=lambda f: Heap.from_rdram(D(f)) if f in have else r.heap)
    print(verdict(r)[0])
