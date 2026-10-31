"""Ports of imbued's Chest-Minigame-Deku-Clip lua movement primitives (test-cmg-solution.lua)
onto the headless harness. Each primitive is a list of (n_frames, buttons, x, y)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "emu"))
from game import *

R = R_TRIG
CAM = PLAY + 0x220 + 0x136  # Camera camDir.y (yaw)
SP = os.environ.get("SP", "/tmp/claude-0/-home-user-mmcliptesting/a78033bb-8150-5832-a8b0-7d77af0af2f6/scratchpad")
ROM = SP + "/rom/kz.z64"
ENTRY = SP + "/st/counter-clip.m64"

class G(Game):
    def run(self, seq, trace=None):
        for n, b, x, y in seq:
            for _ in range(n):
                self.frame(b, x, y)
                if trace is not None: trace.append(self.st())
        self.set_input(0, 0, 0)
    def st(self):
        x, y, z, a = self.pos()
        return (x, y, z, a, self.u16(CAM), self.u16(LINK + 0x32), self.f32(LINK + 0x70))
    def cam(self): return self.u16(CAM)
    def target_untarget_snap(self):
        self.run([(6, Z, 0, 0)])
        old = self.cam(); self.run([(10, 0, 0, 0)]); new = self.cam()
        while old != new:
            self.run([(10, 0, 0, 0)]); old, new = new, self.cam()

def ess(n, left):
    s = -20 if left else 20
    out = [(6, Z, 0, 0), (6, 0, 0, 0)]
    if n <= 9: out.append((n + 1, 0, s, 0))
    else:
        for _ in range(n): out += [(2, 0, s, 0), (6, Z, 0, 0)]
    return out
def hold_sidehop(left):
    s = -128 if left else 127
    return [(6, Z, 0, 0), (1, Z | A, s, 0), (7, Z | R, s, 0)]
def shield_scoot_forward():
    return [(10, Z | R, 0, 127), (3, Z, 0, 127), (3, Z | R, 0, 127), (1, Z | R, 0, 0)]
def hold_backflip():
    return [(6, Z, 0, 0), (1, Z | A, 0, -128), (12, Z | R, 0, -128)]
def spin_in_place(k):
    out = [(30, 0, 0, 0)]
    for _ in range(k): out += [(6, Z, 0, 0), (22, A, 0, 0)]
    return out + [(6, Z, 0, 0)]
CARD = dict(LEFT=(-128, 0), RIGHT=(127, 0), DOWN=(0, -128), UP=(0, 127))
def cardinal(g, d):
    g.target_untarget_snap(); g.run([(1, 0, 0, 0), (1, 0) + CARD[d]]); g.target_untarget_snap()
def final_walk(extra):
    return [(6, Z, 0, 0), (4 + extra, Z, 0, 127), (10, A, 0, 127)]
