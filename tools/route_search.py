"""Search setup variants with the heap simulator, starting from the movie's frame-255 heap.
Variant parameters (see build()): first trip on/off, bombs pulled in each room, whether each explosion
overlaps a room load, which pot is carried. Prints every variant that works.
Usage: python3 tools/route_search.py DUMPDIR"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from heapsim import *
from route_check import INIT, verdict

def build(trip1, b0_in_torch, kP, kT, ex1_over_load, target, ex2_over_load, kill_pot2):
    ev = []
    if trip1:
        ev += [("load", "torch", False), ("unload", "pot")]
        if b0_in_torch: ev += [("spawn", "En_Clear_Tag", "c1"), ("kill", "b0")]
        ev += [("load", "pot", True)]
        if b0_in_torch: ev += [("kill", "c1")]
        ev += [("unload", "torch")]
    else:
        ev += [("spawn", "En_Clear_Tag", "c1"), ("kill", "b0"), ("kill", "c1")]   # first bomb used up in the pot room
    # trip 2: pull kP bombs in the pot room (the last one is carried and explodes in the torch room)
    for i in range(kP - 1): ev.append(("spawn", "En_Bom", f"p{i}", "pot"))
    ev += [("spawn", "En_Bom", "bx"), ("load", "torch", False), ("unload", "pot"),
           ("spawn", "En_Clear_Tag", "c2"), ("kill", "bx")]
    for i in range(kT): ev.append(("spawn", "En_Bom", f"t{i}", "torch"))
    if not ex1_over_load: ev.append(("kill", "c2"))
    ev.append(("load", "pot", True))
    if ex1_over_load: ev.append(("kill", "c2"))
    ev.append(("unload", "torch"))
    # SRM: explosion 2, carry a pot into the torch room
    ev += [("spawn", "En_Bom", "b6", "pot"), ("spawn", "En_Clear_Tag", "c3"), ("kill", "b6")]
    if kill_pot2: ev.append(("killroomactor", "pot", "Obj_Tsubo", 1 if target == 0 else 0))
    ev.append(("mark", "target", "pot", "Obj_Tsubo", 0 if (kill_pot2 and target != 0) else target))
    if not ex2_over_load: ev.append(("kill", "c3"))
    ev.append(("load", "torch", False))
    if ex2_over_load: ev.append(("kill", "c3"))
    ev += [("unload", "pot"), ("load", "pot", True)]
    return ev

def simulate(base, ev):
    r = Route(base, "pot")
    for e in INIT: r.do(e)
    for e in ev: r.do(e)
    return verdict(r)

if __name__ == "__main__":
    base = open(os.path.join(sys.argv[1], "frame255.rdram"), "rb").read()
    movie = dict(trip1=True, b0_in_torch=True, kP=2, kT=3, ex1_over_load=True, target=0, ex2_over_load=True, kill_pot2=True)
    print("movie parameters:", simulate(base, build(**movie))[0])
    works = []
    for trip1, b0t, kP, kT, ex1, tgt, ex2, kp2 in itertools.product((True, False), (True, False), (1, 2, 3, 4), range(0, 6),
                                                                 (True, False), (0, 1, 2), (True, False), (True, False)):
        if not trip1 and b0t: continue
        try:
            msg, ok = simulate(base, build(trip1, b0t, kP, kT, ex1, tgt, ex2, kp2))
        except Exception:
            continue
        if ok: works.append((trip1, b0t, kP, kT, ex1, tgt, ex2, kp2))
    print(len(works), "working variants")
    for w in works:
        print("  trip1=%s b0_in_torch=%s bombs_pot=%d bombs_torch=%d ex1_over_load=%s carry_pot=%d ex2_over_load=%s destroy_other_pot=%s" % w)
