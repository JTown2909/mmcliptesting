import sys, ctypes as C, time; sys.path.insert(0, ".")
import os; os.environ["M64_GFX"] = "video-angrylion-headless.so"; os.environ["M64_RSP"] = "mupen64plus-rsp-cxd4.so"
print("init", flush=True)
from prims import *
g = G(ROM)
print("started", flush=True)
cnt = C.c_int.in_dll(g.gfx, "harness_count")
t = time.time(); g.load(ENTRY); print("loaded", time.time() - t, cnt.value, flush=True)
for i in range(3): t = time.time(); g.frame(0); print("frame", time.time() - t, cnt.value, flush=True)
