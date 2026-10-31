"""Find and walk MM arena (heap) chains in a big-endian RDRAM dump.

JP 1.0/1.1 use the debug-style ArenaNode (0x30 bytes); US/EU use 0x10.
Usage: python3 heapscan.py rdram.bin [nodesize]
"""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from actor_names import ACTOR_NAMES

def u16(d, a): return struct.unpack_from(">H", d, a)[0]
def u32(d, a): return struct.unpack_from(">I", d, a)[0]
def s16(d, a): return struct.unpack_from(">h", d, a)[0]

def is_node(d, a):
    return 0 <= a < len(d) - 0x30 and u16(d, a) == 0x7373 and u16(d, a + 2) in (0, 1)

def chains(d, ns):
    """Return list of chains (lists of node offsets) starting at nodes with prev == NULL."""
    out = []
    for a in range(0, len(d) - 0x30, 0x10):
        if not is_node(d, a) or u32(d, a + 0xC) != 0:
            continue
        chain, cur = [], a
        while True:
            chain.append(cur)
            nxt = u32(d, cur + 8)
            if nxt == 0: break
            nxt &= 0x7FFFFF
            if not is_node(d, nxt) or (u32(d, nxt + 0xC) & 0x7FFFFF) != cur or len(chain) > 5000:
                chain.append(None)  # corrupted / broken link
                break
            cur = nxt
        if len(chain) > 2: out.append(chain)
    return out

def actor_at(d, a, ns):
    """Return (id, category) if the block at node `a` looks like an Actor instance."""
    data = a + ns
    if u16(d, a + 2) or u32(d, a + 4) < 0x144: return None
    aid, cat = s16(d, data), d[data + 2]
    upd = u32(d, data + 0x138)
    if aid == 0 and cat != 2: return None
    if aid in ACTOR_NAMES and cat < 12 and (upd == 0 or 0x80000000 <= upd < 0x80800000):
        return aid, cat
    return None

def label(d, chain, ns):
    """Map node -> text. Actor instances by ID; overlay code blocks by which actor's update/init ptr lands in them."""
    nodes = [a for a in chain if a is not None]
    lab = {}
    for a in nodes:
        act = actor_at(d, a, ns)
        if act:
            data = a + ns
            lab[a] = f"{ACTOR_NAMES[act[0]]} (id {act[0]:03X} cat {act[1]})"
            for off in (0x138, 0x130, 0x13C):
                fp = u32(d, data + off) & 0x7FFFFF
                for b in nodes:
                    if b + ns <= fp < b + ns + u32(d, b + 4) and b not in lab:
                        lab[b] = f"ovl_{ACTOR_NAMES[act[0]]} (code)"
                        break
    return lab

def describe(d, a, ns, lab):
    size = u32(d, a + 4)
    return f"node {0x80000000|a:08X} data {0x80000000|(a+ns):08X} {'FREE' if u16(d,a+2) else 'used'} size={size:06X} {lab.get(a, '')}"

if __name__ == "__main__":
    d = open(sys.argv[1], "rb").read()
    ns = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x30
    for c in chains(d, ns):
        print(f"--- chain head {0x80000000|c[0]:08X}, {len(c)} nodes{' (BROKEN)' if c[-1] is None else ''}")
        lab = label(d, c, ns)
        for a in c:
            if a is not None: print("  ", describe(d, a, ns, lab))
