"""Exact (fp32) flat-ground movement model for Deku Link in the chest minigame room,
following the game's Actor_UpdatePos: pos += (speed * Math_SinS(angle)) * 1.5."""
import os, numpy as np
F = np.float32
_TAB = np.load(os.path.join(os.path.dirname(__file__), "sintab.npy")).astype(np.int64)
SHT_MINV = F(1.0) / F(32767.0)
def sins(a):
    a = (np.asarray(a, dtype=np.int64) & 0xFFFF) >> 4
    v = np.where(a & 0x400, _TAB[0x3FF - (a & 0x3FF)], _TAB[a & 0x3FF])
    return np.where(a & 0x800, -v, v)
def sinf(a): return (sins(a).astype(F) * SHT_MINV).astype(F)
def cosf(a): return sinf(np.asarray(a, dtype=np.int64) + 0x4000)

V_SIDEHOP = [F(8.5), F(8.3999996185303), F(8.2999992370605), F(8.1999988555908), F(8.0999984741211),
             F(7.9999985694885), F(6.9999985694885)]
V_BACKFLIP = [F(6.0), F(5.9000000953674), F(5.8000001907349), F(5.7000002861023), F(5.6000003814697),
              F(5.5000004768372), F(5.4000005722046), F(5.300000667572), F(5.2000007629395),
              F(5.1000008583069), F(5.0000009536743), F(4.0000009536743)]
V_SCOOT = [F(2.0), F(2.0)]
R15 = F(1.5)

def move(x, z, ang, vels):
    """apply a list of per-frame speeds at movement angle `ang` (arrays ok)."""
    x = np.asarray(x, dtype=F).copy(); z = np.asarray(z, dtype=F).copy()
    s, c = sinf(ang), cosf(ang)
    for v in vels:
        x = (x + (F(v) * s).astype(F) * R15).astype(F)
        z = (z + (F(v) * c).astype(F) * R15).astype(F)
    return x, z
