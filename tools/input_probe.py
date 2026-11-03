"""Play a scripted input sequence from a savestate and print every change to Link's angles.

Usage: python3 tools/input_probe.py ROM STATE "SEQ" [FRAMES]
SEQ is a Python list of (start_frame, end_frame, buttons) using names from m64sim:
  CU, Z, A, B, R, L, START, CL, CR, CD, DU..., and stick(x, y) (raw N64 values, -128..127).
Example: "[(20,23,CU),(50,52,stick(10,0))]" = enter first person, then 2 frames of light right stick.
Frames are game frames (emulator callbacks). Prints shape.rot.y, Player.yaw (+0xAD4), parallelYaw (+0xAD6).
"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m64sim import *
from bizstate import BizState

P = 0x803FFFA0
def main():
    rom, state, seq = sys.argv[1], sys.argv[2], eval(sys.argv[3])
    frames = int(sys.argv[4]) if len(sys.argv) > 4 else 120
    if state.endswith(".State"):
        tmp = os.path.join(tempfile.mkdtemp(), "s.st"); BizState(state).m64p(tmp); state = tmp
    sim = Sim(rom=rom, input_so=os.path.join(os.path.dirname(os.path.abspath(__file__)), "scriptinput", "scriptinput.so"))
    seen = []
    def script(s, n):
        if n == 2: s.load_state(state)
        b = 0
        for a, e, bt in seq:
            if a <= n < e: b |= bt
        s.buttons(b)
        if n >= 15:
            v = (s.r16(P + 0xBE), s.r16(P + 0xAD4), s.r16(P + 0xAD6))
            if not seen or seen[-1][1:] != v: seen.append((n,) + v)
        return n < frames
    sim.run(script)
    prev = None
    for f, sh, yw, par in seen:
        d = "" if prev is None else f"  d={((sh - prev + 0x8000) & 0xFFFF) - 0x8000:+d}"
        print(f"frame {f:4d} shape={sh:04X} yaw={yw:04X} parallelYaw={par:04X}{d}"); prev = sh

if __name__ == "__main__":
    main()
