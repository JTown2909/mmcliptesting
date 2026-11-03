"""Minimal headless mupen64plus frontend (ctypes) for scripted RAM dumps.

Usage: python3 m64run.py ROM FRAME OUT.bin   (needs DISPLAY, e.g. Xvfb)
Dumps the 8MB RDRAM (big-endian word order as the N64 sees it) at video frame FRAME.
"""
import ctypes as C, sys, os, struct

LIB = "/usr/lib/x86_64-linux-gnu/"
PLUG = LIB + "mupen64plus/"
core = C.CDLL(LIB + "libmupen64plus.so.2", mode=C.RTLD_GLOBAL)
DBGCB = C.CFUNCTYPE(None, C.c_void_p, C.c_int, C.c_char_p)
STCB = C.CFUNCTYPE(None, C.c_void_p, C.c_int, C.c_int)
FRCB = C.CFUNCTYPE(None, C.c_uint)

@DBGCB
def dbg(ctx, level, msg):
    if level <= 2: print("m64p:", msg.decode(errors="replace"))
@STCB
def st(ctx, p, v): pass

def run(rom, frame, out):
    assert core.CoreStartup(0x020001, None, b"/usr/share/games/mupen64plus", None, dbg, None, st) == 0
    data = open(rom, "rb").read()
    assert core.CoreDoCommand(1, len(data), C.c_char_p(data)) == 0
    plugs = []
    for typ, name in ((2, "video-glide64mk2"), (3, "audio-sdl"), (4, "input-sdl"), (1, "rsp-hle")):
        h = C.CDLL(PLUG + f"mupen64plus-{name}.so")
        h.PluginStartup(C.c_void_p(core._handle), None, dbg)
        assert core.CoreAttachPlugin(typ, C.c_void_p(h._handle)) == 0, name
        plugs.append(h)
    core.DebugMemGetPointer.restype = C.c_void_p

    @FRCB
    def onframe(n):
        if n == frame:
            p = core.DebugMemGetPointer(1)  # M64P_DBG_PTR_RDRAM
            raw = C.string_at(p, 0x800000)
            # mupen stores RDRAM as host-endian 32-bit words; convert to N64 big-endian
            words = struct.unpack("<%dI" % (len(raw) // 4), raw)
            open(out, "wb").write(struct.pack(">%dI" % len(words), *words))
            core.CoreDoCommand(6, 0, None)  # stop
    core.CoreDoCommand(15, 0, C.cast(onframe, C.c_void_p))
    core.CoreDoCommand(5, 0, None)  # execute (blocks)
    core.CoreDoCommand(2, 0, None)

if __name__ == "__main__":
    run(sys.argv[1], int(sys.argv[2]), sys.argv[3])
