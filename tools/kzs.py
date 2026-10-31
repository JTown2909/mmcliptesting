"""Decode kz-lite (.kzs) save state files into a flat, uncompressed byte stream.

File layout: kz_state_hdr_t (u16 z2_version, u16 state_version, u32 size,
char name[64]) followed by the kz lz token stream (see kz src/state_lz.c).
"""
import struct, sys

HDR = struct.Struct(">HHI64s")

def decompress(data):
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        t = data[i]; i += 1
        if t < 0x80:
            out += data[i:i + t + 1]; i += t + 1
        else:
            if i + 2 > n:
                break
            mlen = t & 0x7F
            dist = (data[i] << 8) | data[i + 1]; i += 2
            if mlen == 0x7F:
                while True:
                    e = data[i]; i += 1; mlen += e
                    if e != 0xFF:
                        break
            mlen += 3
            s = len(out) - dist
            for k in range(mlen):
                out.append(out[s + k])
    return bytes(out)

def load(path):
    raw = open(path, "rb").read()
    zv, sv, size, name = HDR.unpack_from(raw)
    return dict(z2_version=zv, state_version=sv, size=size,
                name=name.split(b"\0")[0].decode(errors="replace")), decompress(raw[HDR.size:])

if __name__ == "__main__":
    for p in sys.argv[1:]:
        h, d = load(p)
        print(p, h, "uncompressed", hex(len(d)))
