"""Read/patch BizHawk Mupen64Plus .State files (zip: Core.bin.zst = 4-byte prefix + m64p state; RDRAM at 0x1C0,
stored as little-endian 32-bit words).

    st = BizState("in.State"); st.w16(0x801EF46C, 0x9555); st.save("out.State")
Requires the `zstd` command-line tool.
"""
import zipfile, subprocess, struct

RDRAM_OFF = 0x1C0

class BizState:
    def __init__(self, path):
        self.zin = zipfile.ZipFile(path)
        self.core = bytearray(subprocess.run(["zstd", "-d", "-c"], input=self.zin.read("Core.bin.zst"),
                                             capture_output=True, check=True).stdout)
        assert self.core[4:12] == b"M64+SAVE"
    def _off(self, a): a &= 0x7FFFFF; return RDRAM_OFF + (a & ~3) + (3 - (a & 3))
    def r8(self, a): return self.core[self._off(a)]
    def w8(self, a, v): self.core[self._off(a)] = v & 0xFF
    def r16(self, a): return (self.r8(a) << 8) | self.r8(a + 1)
    def w16(self, a, v): self.w8(a, v >> 8); self.w8(a + 1, v)
    def r32(self, a): return (self.r16(a) << 16) | self.r16(a + 2)
    def w32(self, a, v): self.w16(a, v >> 16); self.w16(a + 2, v)
    def save(self, path):
        zc = subprocess.run(["zstd", "-q", "-c", "-3"], input=bytes(self.core), capture_output=True, check=True).stdout
        with zipfile.ZipFile(path, "w") as zout:
            for info in self.zin.infolist():
                data = zc if info.filename == "Core.bin.zst" else self.zin.read(info.filename)
                zout.writestr(info, data)
    def m64p(self, path):
        import gzip
        with gzip.open(path, "wb", compresslevel=1) as f: f.write(bytes(self.core[4:]))
