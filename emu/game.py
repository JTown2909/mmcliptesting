"""MM JP 1.0 game helpers on top of the m64 harness."""
import math, struct
from m64 import *

LINK = 0x803FFFA0
PLAY = 0x803E6CF0

class Game(M64):
    def link(self):
        L = LINK
        return dict(x=self.f32(L + 0x24), y=self.f32(L + 0x28), z=self.f32(L + 0x2C),
                    yaw=self.u16(L + 0xBE), speed=self.f32(L + 0x70),
                    movedir=self.u16(L + 0x32), state1=self.u32(L + 0xA6C) if False else 0)
    def pos(self):
        L = LINK
        return (self.f32(L + 0x24), self.f32(L + 0x28), self.f32(L + 0x2C), self.u16(L + 0xBE))
    def frame(self, buttons=0, x=0, y=0, n=1):
        self.set_input(buttons, x, y); self.step(n)
