"""Simulate MM's actor heap (ZeldaArena) allocator, starting from real RAM snapshots.

Allocator rules (decomp libc64/__osMalloc.c; JP node header = 0x30):
  malloc(size):  first free block from the HEAD with block.size >= size; split only if size+0x30 < block.size.
  mallocR(size): same search from the TAIL backwards; carve from the END of the block.
  free(addr):    mark free; merge with next if adjacent+free, then with prev if adjacent+free.
Actors: overlay code via malloc (mallocR if ALLOCTYPE_PERMANENT), then instance via malloc.

Use:
  h = Heap.from_rdram(open("frame795.rdram","rb").read())
  a = h.malloc(0x1A0); h.free(a)
  diff(h_before, h_after) -> (allocated, freed)
  infer_order(h_before, h_after) -> list of ("malloc"/"mallocR", size, node) reproducing h_after exactly
"""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from actor_names import ACTOR_NAMES

NODE = 0x30
HEAD = 0x803FFF70
def a16(x): return (x + 15) & ~15

class Heap:
    def __init__(self, blocks):
        self.blocks = [list(b) for b in blocks]     # [node_addr, size, free, label], address order

    @classmethod
    def from_rdram(cls, d, head=HEAD):
        u16 = lambda a: struct.unpack_from(">H", d, a & 0x7FFFFF)[0]
        u32 = lambda a: struct.unpack_from(">I", d, a & 0x7FFFFF)[0]
        out, cur = [], head
        while cur:
            if u16(cur) != 0x7373: raise ValueError(f"bad node {cur:08X}")
            free, size = u16(cur + 2), u32(cur + 4)
            lab = ""
            if not free and size >= 0x144:
                aid, cat = u16(cur + NODE), d[(cur + NODE + 2) & 0x7FFFFF]
                if aid in ACTOR_NAMES and cat < 12: lab = ACTOR_NAMES[aid]
            out.append((cur, size, bool(free), lab))
            cur = u32(cur + 8)
        return cls(out)

    def copy(self): return Heap(self.blocks)

    def malloc(self, size, label=""):
        size = a16(size)
        for i, b in enumerate(self.blocks):
            if b[2] and b[1] >= size:
                if size + NODE < b[1]:
                    self.blocks.insert(i + 1, [b[0] + size + NODE, b[1] - size - NODE, True, ""])
                    b[1] = size
                b[2] = False; b[3] = label
                return b[0]
        return None

    def mallocR(self, size, label=""):
        size = a16(size)
        for i in range(len(self.blocks) - 1, -1, -1):
            b = self.blocks[i]
            if b[2] and b[1] >= size:
                if size + NODE < b[1]:
                    new = [b[0] + b[1] - size, size, False, label]
                    b[1] -= size + NODE
                    self.blocks.insert(i + 1, new)
                    return new[0]
                b[2] = False; b[3] = label
                return b[0]
        return None

    def free(self, node):
        i = next(k for k, b in enumerate(self.blocks) if b[0] == node)
        b = self.blocks[i]
        if b[2]: return
        b[2] = True; b[3] = ""
        if i + 1 < len(self.blocks):
            n = self.blocks[i + 1]
            if n[2] and n[0] == b[0] + NODE + b[1]:
                b[1] += n[1] + NODE; del self.blocks[i + 1]
        if i > 0:
            p = self.blocks[i - 1]
            if p[2] and b[0] == p[0] + NODE + p[1]:
                p[1] += b[1] + NODE; del self.blocks[i]

    def used(self): return {b[0]: (b[1], b[3]) for b in self.blocks if not b[2]}
    def node_of(self, label):
        return [b[0] for b in self.blocks if not b[2] and b[3] == label]
    def same_layout(self, other):
        return [(b[0], b[1], b[2]) for b in self.blocks] == [(b[0], b[1], b[2]) for b in other.blocks]
    def dump(self, lo=0, hi=0xFFFFFFFF):
        for n, s, f, l in self.blocks:
            if lo <= n < hi: print(f"  {n:08X} {'FREE' if f else 'used'} {s:06X} {l}")

def diff(before, after):
    ub, ua = before.used(), after.used()
    alloc = sorted((n, ua[n][0], ua[n][1]) for n in ua if n not in ub or ub[n][0] != ua[n][0])
    freed = sorted((n, ub[n][0], ub[n][1]) for n in ub if n not in ua or ua[n][0] != ub[n][0])
    return alloc, freed

def infer_order(before, after, max_nodes=200000):
    """Find frees + an ordered list of malloc/mallocR calls turning `before` into `after` exactly.
    Frees are applied first (their order doesn't change the result). DFS over which new block comes next."""
    alloc, freed = diff(before, after)
    h0 = before.copy()
    for n, _, _ in freed: h0.free(n)
    target = {n: s for n, s, _ in alloc}
    labels = {n: l for n, _, l in alloc}
    seen = [0]
    def dfs(h, remaining, seq):
        if not remaining:
            return seq if h.same_layout(after) else None
        seen[0] += 1
        if seen[0] > max_nodes: return None
        tried = set()
        for n in sorted(remaining):
            s = target[n]
            for kind in ("malloc", "mallocR"):
                if (kind, s) in tried: continue
                tried.add((kind, s))
                h2 = h.copy()
                got = (h2.malloc if kind == "malloc" else h2.mallocR)(s, labels[n])
                if got in remaining and target[got] == s:
                    r = dfs(h2, remaining - {got}, seq + [(kind, s, got, labels[got])])
                    if r is not None: return r
        return None
    return freed, dfs(h0, frozenset(target), [])

# ---------------------------------------------------------------- actors & rooms
import pickle
OVL_TABLE = 0x801A9E60          # JP 1.0 gActorOverlayTable (0x20-byte entries), derived from Moon Stone's overlayEntry
PERMANENT = 2
ROOMS = {   # actor lists from the ROM (observatory scene), spawn order
    "torch": ["En_St"] + ["En_Water_Effect"] * 5 + ["En_Light"] + ["Obj_Syokudai"] * 6 +
             ["Obj_Tokeidai", "Bg_Astr_Bombwall", "En_Encount2", "En_St", "En_Test4", "Obj_Mure", "En_Box"] +
             ["Obj_Tsubo"] * 4,
    "pot":   ["En_Bji_01", "En_Niw", "Obj_Moon_Stone", "Obj_Tokeidai", "En_Test4"] + ["Obj_Tsubo"] * 3 +
             ["En_Kakasi", "Obj_Sound"],
}
INFO = pickle.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "actorinfo_jp10.pkl"), "rb"))

class World:
    """Heap + overlay-table state, initialised from a RAM snapshot."""
    def __init__(self, d):
        self.heap = Heap.from_rdram(d)
        self.ovl = {}
        for name, x in INFO.items():
            o = (OVL_TABLE + 0x20 * x["id"]) & 0x7FFFFF
            addr = struct.unpack_from(">I", d, o + 0x10)[0]
            n = d[o + 0x1E]
            self.ovl[name] = [addr - NODE if addr else None, n]
    def copy(self):
        w = World.__new__(World); w.heap = self.heap.copy(); w.ovl = {k: list(v) for k, v in self.ovl.items()}
        return w
    EXTRA = {"En_Kakasi": [0xB0, 0xB0]}   # extra allocations made when the pot room loads; NEVER freed (leak, observed)
    def spawn(self, name):
        x = INFO[name]; e = self.ovl[name]
        if x["ovl"] and e[0] is None:
            e[0] = (self.heap.mallocR if x["alloc"] & PERMANENT else self.heap.malloc)(x["ovl"], "ovl_" + name)
        node = self.heap.malloc(x["inst"], name)
        self.heap_last = node
        for sz in self.EXTRA.get(name, []): self.heap.malloc(sz, name + "_leak")
        e[1] += 1
        return node
    def kill(self, name, node):
        self.heap.free(node)
        e = self.ovl[name]; e[1] -= 1
        if e[1] <= 0 and e[0] is not None and not (INFO[name]["alloc"] & PERMANENT):
            self.heap.free(e[0]); e[0] = None; e[1] = 0
    def load_room(self, room, skip=(), door=False):
        """Spawn a room's actors in list order; the room's own En_Test4 deletes itself (sIsLoaded).
        door=True: entering through a door re-spawns its En_Door instance first."""
        out = []
        if door: self.spawn("En_Door")
        for i, name in enumerate(ROOMS[room]):
            if i in skip: continue
            out.append((name, self.spawn(name)))
        for name, node in out:
            if name == "En_Test4": self.kill(name, node)
        return [o for o in out if o[0] != "En_Test4"]

class Route(World):
    """World + room ownership, so whole sequences of events can be simulated.
    Events: ("load", room, door) | ("unload", room) | ("spawn", name, tag) | ("kill", tag)"""
    PERSIST = {"Player", "En_Test4", "En_Door", "En_Holl", "En_Elf"}
    def __init__(self, d, loaded_room):
        super().__init__(d)
        self.rooms = {loaded_room: []}
        self.tags = {}
        names = set(ROOMS[loaded_room])
        for n, s, f, lab in self.heap.blocks:
            if not f and lab in names and lab not in self.PERSIST:
                self.rooms[loaded_room].append([lab, n])
    def copy(self):
        r = Route.__new__(Route); r.heap = self.heap.copy(); r.ovl = {k: list(v) for k, v in self.ovl.items()}
        r.rooms = {k: [list(x) for x in v] for k, v in self.rooms.items()}; r.tags = dict(self.tags); return r
    def spawn_tracked(self, name):
        return [self.spawn(name) and name, self.heap_last]
    def kill_tracked(self, a):
        self.kill(a[0], a[1])
    def do(self, ev):
        k = ev[0]
        if k == "load":
            room, door = ev[1], ev[2]
            lst = [self.spawn_tracked("En_Door")] if door else []
            lst += [self.spawn_tracked(n) for n in ROOMS[room]]
            for a in lst:
                if a[0] == "En_Test4": self.kill_tracked(a)
            self.rooms[room] = [a for a in lst if a[0] != "En_Test4"]
        elif k == "unload":
            for a in self.rooms.pop(ev[1], []): self.kill_tracked(a)
        elif k == "spawn":            # ("spawn", name, tag[, room]) - room-owned actors die when that room unloads
            a = self.spawn_tracked(ev[1]); self.tags[ev[2]] = a
            if len(ev) > 3: self.rooms.setdefault(ev[3], []).append(a)
        elif k == "killnode":         # ("killnode", node) - kill whatever room actor lives at this node
            for v in self.rooms.values():
                for a in v:
                    if a[1] == ev[1]:
                        v.remove(a); self.kill_tracked(a); return self
            raise KeyError(hex(ev[1]))
        elif k == "mark":             # ("mark", tag, room, name, idx) - remember the idx-th live actor of a room
            live = [a for a in self.rooms[ev[2]] if a[0] == ev[3]]
            self.tags[ev[1]] = live[ev[4]]
        elif k == "rawR":             # ("rawR", size) - non-actor allocation from the top, never freed
            self.heap.mallocR(ev[1], "raw")
        elif k == "raw":
            self.heap.malloc(ev[1], "raw")
        elif k == "adopt":            # ("adopt", name, node, tag[, room]) - an actor already in the snapshot
            a = [ev[1], ev[2]]; self.tags[ev[3]] = a
            if len(ev) > 4: self.rooms.setdefault(ev[4], []).append(a)
        elif k == "kill":
            a = self.tags.pop(ev[1])
            for v in self.rooms.values():
                if a in v: v.remove(a)
            self.kill_tracked(a)
        elif k == "killroomactor":     # e.g. a pot broken / thrown: kill the n-th live actor of that name in a room
            room, name, idx = ev[1], ev[2], ev[3]
            live = [a for a in self.rooms[room] if a[0] == name]
            a = live[idx]; self.rooms[room].remove(a); self.kill_tracked(a)
        return self

def layout_diff(sim_heap, real_heap):
    A = {(b[0], b[1], b[2]) for b in sim_heap.blocks}; B = {(b[0], b[1], b[2]) for b in real_heap.blocks}
    return sorted(A - B), sorted(B - A)
