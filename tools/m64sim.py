"""Headless mupen64plus driver: load a savestate, script inputs/pokes per frame, grab screenshots/RAM.

Example:
    sim = Sim(rom, input_so)
    sim.run(script)   # script(sim, frame) called every VI; return False to stop
BizHawk Mupen64Plus states: Core.bin (zstd-decompressed) minus its 4-byte prefix is a m64p state.
"""
import ctypes as C, struct, os

LIB = "/usr/lib/x86_64-linux-gnu/"
PLUG = LIB + "mupen64plus/"
DBGCB = C.CFUNCTYPE(None, C.c_void_p, C.c_int, C.c_char_p)
STCB = C.CFUNCTYPE(None, C.c_void_p, C.c_int, C.c_int)
FRCB = C.CFUNCTYPE(None, C.c_uint)

# N64 button bits (BUTTONS union)
DR, DL, DD, DU, START, Z, B, A = 1, 2, 4, 8, 0x10, 0x20, 0x40, 0x80
CR, CL, CD, CU, R, L = 0x100, 0x200, 0x400, 0x800, 0x1000, 0x2000
def stick(x, y): return ((x & 0xFF) << 16) | ((y & 0xFF) << 24)

class Sim:
    def __init__(self, rom, input_so, verbose=False):
        self.core = C.CDLL(LIB + "libmupen64plus.so.2", mode=C.RTLD_GLOBAL)
        self._dbg = DBGCB(lambda c, l, m: print("m64p:", m.decode(errors="replace")) if (verbose or l <= 1) else None)
        self._st = STCB(lambda c, p, v: None)
        assert self.core.CoreStartup(0x020001, None, b"/usr/share/games/mupen64plus", None, self._dbg, None, self._st) == 0
        data = open(rom, "rb").read()
        assert self.core.CoreDoCommand(1, len(data), C.c_char_p(data)) == 0
        self.plugs = []
        for typ, path in ((2, PLUG + "mupen64plus-video-rice.so"), (3, PLUG + "mupen64plus-audio-sdl.so"),
                          (4, input_so), (1, PLUG + "mupen64plus-rsp-hle.so")):
            h = C.CDLL(path)
            h.PluginStartup(C.c_void_p(self.core._handle), None, self._dbg)
            assert self.core.CoreAttachPlugin(typ, C.c_void_p(h._handle)) == 0, path
            self.plugs.append(h)
        self.inp = self.plugs[2]
        self.core.DebugMemGetPointer.restype = C.c_void_p
        self.rdram = None

    # --- memory (virtual 0x80xxxxxx or physical) ---
    def _ptr(self):
        if self.rdram is None:
            self.rdram = (C.c_uint8 * 0x800000).from_address(self.core.DebugMemGetPointer(1))
        return self.rdram
    def r8(self, a):  a &= 0x7FFFFF; return self._ptr()[(a & ~3) | (3 - (a & 3))]
    def w8(self, a, v): a &= 0x7FFFFF; self._ptr()[(a & ~3) | (3 - (a & 3))] = v & 0xFF
    def r16(self, a): return (self.r8(a) << 8) | self.r8(a + 1)
    def r32(self, a): return (self.r16(a) << 16) | self.r16(a + 2)
    def w16(self, a, v): self.w8(a, v >> 8); self.w8(a + 1, v)
    def w32(self, a, v): self.w16(a, v >> 16); self.w16(a + 2, v)
    def wbytes(self, a, bs):
        for i, b in enumerate(bs): self.w8(a + i, b)
    def dump(self):
        raw = bytes(self._ptr())
        w = struct.unpack("<%dI" % (len(raw) // 4), raw)
        return struct.pack(">%dI" % len(w), *w)

    def buttons(self, b): self.inp.script_set_buttons(C.c_uint32(b))
    def load_state(self, path): self.core.CoreDoCommand(10, 0, C.c_char_p(path.encode()))
    def screenshot(self): self.core.CoreDoCommand(16, 0, None)
    def stop(self): self.core.CoreDoCommand(6, 0, None)

    def run(self, script):
        def cb(n):
            try:
                if script(self, n) is False: self.stop()
            except Exception as e:
                import traceback; traceback.print_exc(); self.stop()
        self._cb = FRCB(cb)
        self.core.CoreDoCommand(15, 0, C.cast(self._cb, C.c_void_p))
        self.core.CoreDoCommand(5, 0, None)

def bizhawk_state_to_m64p(core_bin, out):
    d = open(core_bin, "rb").read()
    assert d[4:12] == b"M64+SAVE"
    import gzip
    with gzip.open(out, "wb", compresslevel=1) as f: f.write(d[4:])
