"""Minimal MM ROM file access: locate dmadata, list files, Yaz0-decompress.
Usage: from romfiles import Rom; r = Rom(path); r.files -> [(vstart, vend, pstart, pend)], r.read(i) -> bytes
"""
import struct

def yaz0(src):
    assert src[:4] == b"Yaz0"
    size = struct.unpack_from(">I", src, 4)[0]
    dst = bytearray(); i = 16
    while len(dst) < size:
        code = src[i]; i += 1
        for bit in range(8):
            if len(dst) >= size: break
            if code & (0x80 >> bit):
                dst.append(src[i]); i += 1
            else:
                b1, b2 = src[i], src[i + 1]; i += 2
                dist = ((b1 & 0xF) << 8 | b2) + 1
                n = b1 >> 4
                if n == 0: n = src[i] + 0x12; i += 1
                else: n += 2
                s = len(dst) - dist
                for k in range(n): dst.append(dst[s + k])
    return bytes(dst)

class Rom:
    def __init__(self, path):
        self.d = open(path, "rb").read()
        pat = struct.pack(">IIII", 0, 0x1060, 0, 0)
        off = self.d.find(pat)
        while off != -1 and struct.unpack_from(">I", self.d, off + 16)[0] != 0x1060:
            off = self.d.find(pat, off + 4)
        self.dma = off; self.files = []
        i = off
        while True:
            vs, ve, ps, pe = struct.unpack_from(">IIII", self.d, i)
            if vs == 0 and ve == 0 and i != off: break
            self.files.append((vs, ve, ps, pe)); i += 16
    def read(self, k):
        vs, ve, ps, pe = self.files[k]
        if ps == 0xFFFFFFFF: return b""
        if pe == 0: return self.d[ps:ps + (ve - vs)]
        return yaz0(self.d[ps:pe])
