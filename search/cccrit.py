import math
CORNER = (80.0, 840.0)
def front(x):
    if x <= 16: return 811.0
    return 811.0 + (x - 16) * 29.0 / 64.0
def back(x):
    if x <= 16: return 841.0
    return 841.0 + (x - 16) * 29.0 / 64.0
class ClipDetector:
    """clip = Link was in front of the counter and is now behind its back face (or inside the
    wall x>80 region next to it), near the right-hand corner"""
    def __init__(self): self.was_front = False; self.hit = False
    def feed(self, x, z):
        if -175 < x < 80 and z < front(x): self.was_front = True
        if self.was_front and math.hypot(x - CORNER[0], z - CORNER[1]) < 80:
            if (-175 < x < 80 and z > back(x) + 1) or (x > 81 and 800 < z < 960):
                self.hit = True
        return self.hit
