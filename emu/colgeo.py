"""Dump static collision polygons of the current scene (MM JP 1.0)."""
import struct
from game import PLAY

def static_polys(g):
    ram = g.rdram_bytes()
    def u32(a): return struct.unpack_from(">I", ram, a & 0x7FFFFF)[0]
    hdr = u32(PLAY + 0x830)
    nv, = struct.unpack_from(">H", ram, (hdr + 0xC) & 0x7FFFFF)
    vtx = u32(hdr + 0x10)
    npoly, = struct.unpack_from(">H", ram, (hdr + 0x14) & 0x7FFFFF)
    poly = u32(hdr + 0x18)
    V = [struct.unpack_from(">hhh", ram, (vtx + 6 * i) & 0x7FFFFF) for i in range(nv)]
    P = []
    for i in range(npoly):
        typ, a, b, c, nx, ny, nz, d = struct.unpack_from(">HHHHhhhh", ram, (poly + 16 * i) & 0x7FFFFF)
        P.append(dict(i=i, type=typ, v=(V[a & 0x1FFF], V[b & 0x1FFF], V[c & 0x1FFF]), flags=(a >> 13, b >> 13),
                      n=(nx / 32767, ny / 32767, nz / 32767), d=d))
    return P

def near(P, x, z, r):
    out = []
    for p in P:
        xs = [v[0] for v in p["v"]]; zs = [v[2] for v in p["v"]]
        if min(xs) - r <= x <= max(xs) + r and min(zs) - r <= z <= max(zs) + r:
            out.append(p)
    return out
