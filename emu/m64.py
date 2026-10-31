"""Lockstep Python frontend for mupen64plus-core.

The emulator thread blocks inside the frame (VI) callback until the Python
side calls step(); RAM is accessed directly through DebugMemGetPointer.
"""
import ctypes as C, os, threading, struct

BIN = os.environ.get("M64_BIN", "/tmp/claude-0/-home-user-mmcliptesting/a78033bb-8150-5832-a8b0-7d77af0af2f6/scratchpad/bin")

M64CMD_ROM_OPEN, M64CMD_EXECUTE, M64CMD_STOP = 1, 5, 6
M64CMD_STATE_LOAD, M64CMD_STATE_SAVE = 10, 11
M64CMD_SET_FRAME_CALLBACK, M64CMD_CORE_STATE_SET = 15, 17
M64CORE_SPEED_LIMITER = 5
PLUGIN_RSP, PLUGIN_GFX, PLUGIN_AUDIO, PLUGIN_INPUT = 1, 2, 3, 4

# N64 button bits (BUTTONS union, little endian bitfield layout used by mupen)
R_DPAD, L_DPAD, D_DPAD, U_DPAD = 1 << 0, 1 << 1, 1 << 2, 1 << 3
START, Z, B, A = 1 << 4, 1 << 5, 1 << 6, 1 << 7
R_CBUTTON, L_CBUTTON, D_CBUTTON, U_CBUTTON = 1 << 8, 1 << 9, 1 << 10, 1 << 11
R_TRIG, L_TRIG = 1 << 12, 1 << 13

def pad(buttons=0, x=0, y=0):
    return (buttons & 0xFFFF) | ((x & 0xFF) << 16) | ((y & 0xFF) << 24)

DEBUGCB = C.CFUNCTYPE(None, C.c_void_p, C.c_int, C.c_char_p)
STATECB = C.CFUNCTYPE(None, C.c_void_p, C.c_int, C.c_int)
FRAMECB = C.CFUNCTYPE(None, C.c_uint)

class M64:
    def __init__(self, rom, verbose=False):
        self.core = C.CDLL(os.path.join(BIN, "libmupen64plus.so.2"), mode=C.RTLD_GLOBAL)
        self.rsp = C.CDLL(os.path.join(BIN, "mupen64plus-rsp-hle.so"))
        self.inp = C.CDLL(os.path.join(BIN, "harness-input.so"))
        self.gfx = C.CDLL(os.path.join(BIN, os.environ.get("M64_GFX", "video-stub.so")))
        self.buttons = C.c_uint.in_dll(self.inp, "harness_buttons")
        self.polls = C.c_int.in_dll(self.inp, "harness_polls")
        self.verbose = verbose
        self._dbg = DEBUGCB(self._on_debug)
        self._state = STATECB(self._on_state)
        self._saved = threading.Event()
        self._frame = FRAMECB(self._on_frame)
        cfg = os.path.join(BIN, "cfg"); os.makedirs(cfg, exist_ok=True)
        r = self.core.CoreStartup(0x020001, cfg.encode(), BIN.encode(), None, self._dbg, None, self._state)
        assert r == 0, r
        cpu = os.environ.get("M64_CPU")
        if cpu is not None:
            h = C.c_void_p()
            self.core.ConfigOpenSection(b"Core", C.byref(h))
            v = C.c_int(int(cpu))
            self.core.ConfigSetParameter(h, b"R4300Emulator", 1, C.byref(v))  # M64TYPE_INT
        for lib in (self.gfx, self.rsp, self.inp):
            lib.PluginStartup(C.c_void_p(self.core._handle), None, self._dbg)
        data = open(rom, "rb").read()
        self._rom = C.create_string_buffer(data, len(data))
        assert self.core.CoreDoCommand(M64CMD_ROM_OPEN, len(data), self._rom) == 0
        assert self.core.CoreAttachPlugin(PLUGIN_GFX, C.c_void_p(self.gfx._handle)) == 0
        assert self.core.CoreAttachPlugin(PLUGIN_INPUT, C.c_void_p(self.inp._handle)) == 0
        assert self.core.CoreAttachPlugin(PLUGIN_RSP, C.c_void_p(self.rsp._handle)) == 0
        lim = C.c_int(0)
        self.core.CoreDoCommand(M64CMD_CORE_STATE_SET, M64CORE_SPEED_LIMITER, C.byref(lim))
        self.core.CoreDoCommand(M64CMD_SET_FRAME_CALLBACK, 0, C.cast(self._frame, C.c_void_p))
        self.core.DebugMemGetPointer.restype = C.c_void_p
        self._go = threading.Semaphore(0)
        self._done = threading.Semaphore(0)
        self.vi = 0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._done.acquire()  # first VI reached
        lim = C.c_int(0)
        self.core.CoreDoCommand(M64CMD_CORE_STATE_SET, M64CORE_SPEED_LIMITER, C.byref(lim))
        self.ram = (C.c_ubyte * 0x800000).from_address(self.core.DebugMemGetPointer(1))

    def _on_debug(self, ctx, level, msg):
        if self.verbose or level <= 2:
            print("[m64]", level, msg.decode(errors="replace"))

    def _on_state(self, ctx, param, value):
        if param == 11:  # M64CORE_STATE_SAVECOMPLETE
            self._saved.set()

    def _run(self):
        self.core.CoreDoCommand(M64CMD_EXECUTE, 0, None)

    def _on_frame(self, n):
        self.vi = n
        self._done.release()
        self._go.acquire()

    def step(self, n=1):
        for _ in range(n):
            self._go.release()
            if not self._done.acquire(timeout=10):
                raise TimeoutError("emulator produced no frame for 10s (game hung?) vi=%d" % self.vi)

    # ---- memory (RDRAM is stored as native-endian 32-bit words) ----
    def _addr(self, a):
        return a & 0x7FFFFF

    def read(self, addr, n):
        a = self._addr(addr)
        return bytes(self.ram[(i ^ 3)] for i in range(a, a + n))

    def write(self, addr, data):
        a = self._addr(addr)
        for i, b in enumerate(data):
            self.ram[(a + i) ^ 3] = b

    def u8(self, a): return self.ram[self._addr(a) ^ 3]
    def u16(self, a): return struct.unpack(">H", self.read(a, 2))[0]
    def s16(self, a): return struct.unpack(">h", self.read(a, 2))[0]
    def u32(self, a): return struct.unpack(">I", self.read(a, 4))[0]
    def f32(self, a): return struct.unpack(">f", self.read(a, 4))[0]

    def rdram_bytes(self):
        """Whole RDRAM as big-endian bytes."""
        raw = bytes(self.ram)
        import array
        arr = array.array("I", raw); arr.byteswap()
        return arr.tobytes()

    def set_input(self, buttons=0, x=0, y=0):
        self.buttons.value = pad(buttons, x, y)

    def save(self, path):
        """Runs ONE game frame with the currently held input, then snapshots.
        (mupen64plus only saves at a VI boundary.)  load() restores exactly."""
        self._saved.clear()
        self.core.CoreDoCommand(M64CMD_STATE_SAVE, 1, os.path.abspath(path).encode())
        self.step(1)
        assert self._saved.wait(30), "savestate did not complete"
        # the snapshot is taken mid-frame, before the next controller read, so the
        # held input is part of the state: remember it and restore it on load
        with open(path + ".inp", "w") as f:
            f.write(str(self.buttons.value))

    def load(self, path):
        if os.path.exists(path + ".inp"):
            self.buttons.value = int(open(path + ".inp").read())
        self.core.CoreDoCommand(M64CMD_STATE_LOAD, 0, os.path.abspath(path).encode())
        self.step(1)
