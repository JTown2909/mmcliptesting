"""Boot the kz-lite ROM headless and load a .kzs state through kz itself.

kz-lite keeps its states in a 512k heap at 0x80700000.  We save a throwaway
state (D-Left) to find kz.states[slot], then write the .kzs file as a single
chunk into a free heap block and point the slot at it, then load (D-Right).
"""
import struct
from m64 import *

KZ_STATES_SLOT0 = 0x80068BCC   # found by scanning after a D-Left save (JP 1.0 kz-lite v3)
LINK = 0x803FFFA0
PLAY = 0x803E6CF0

def press(e, btn, frames=2, after=10):
    e.set_input(btn); e.step(frames); e.set_input(0); e.step(after)

def heap_blocks(e):
    ram = e.rdram_bytes(); a = 0x700000; out = []
    while 0x700000 <= a < 0x780000:
        free, heap, size, prev, nxt = struct.unpack_from(">hhIII", ram, a)
        out.append((0x80000000 + a, free, size))
        if nxt == 0: break
        a = nxt & 0x7FFFFF
    return out

def boot_and_load(rom, kzs_path):
    e = M64(rom)
    e.step(200)
    press(e, L_DPAD)                 # throwaway save so kz initializes the slot
    data = open(kzs_path, "rb").read()
    hdr = e.u32(KZ_STATES_SLOT0)
    regions = [(hdr - 12, e.u32(hdr - 12 + 8))]          # the throwaway state's own chunk
    free_blocks = [(a, s) for a, f, s in heap_blocks(e) if f and s >= 0x800]
    free_blocks.sort(key=lambda b: -b[1])
    regions += [((a + 0x20) & ~0xF, s - 0x40) for a, s in free_blocks]
    chunks, off = [], 0
    for addr, cap in regions:
        if off >= len(data): break
        n = min(cap, len(data) - off)
        chunks.append((addr, data[off:off + n])); off += n
        if addr != regions[0][0]:
            e.write((addr - 0x20) & ~0xF if False else [a for a, _ in free_blocks if (a + 0x20) & ~0xF == addr][0], b"\0\0")  # mark block used
    assert off == len(data), "not enough kz heap for this state"
    for i, (addr, part) in enumerate(chunks):
        nxt = chunks[i + 1][0] if i + 1 < len(chunks) else 0
        e.write(addr, struct.pack(">III", nxt, len(part), len(part)) + part)
    e.write(KZ_STATES_SLOT0, struct.pack(">I", chunks[0][0] + 12))
    press(e, R_DPAD, after=20)
    return e

def link_pos(e):
    return (e.f32(LINK + 0x24), e.f32(LINK + 0x28), e.f32(LINK + 0x2C), e.u16(LINK + 0xBE))
