import math
CORNER = (-1431.0, 435.0)
def behind(x, z):
    """how far Link is behind the laundry-pool corner walls (positive = out of bounds)"""
    if x > -1431:
        return z - 435
    return -(0.39 * (x + 1431) - 0.921 * (z - 435))

class ClipDetector:
    """clip = Link goes from in front of the corner walls to >3 units behind them,
    within 45 units of the corner vertex, and stays in this scene"""
    def __init__(self): self.prev = None; self.hit = False
    def feed(self, x, z):
        b = behind(x, z)
        near = math.hypot(x - CORNER[0], z - CORNER[1]) < 45
        if self.prev is not None and self.prev < 0 and b > 3 and near:
            self.hit = True
        self.prev = b
        return self.hit
