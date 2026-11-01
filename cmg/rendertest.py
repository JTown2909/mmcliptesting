import sys, ctypes as C; sys.path.insert(0, ".")
import os; os.environ["M64_GFX"] = "video-angrylion-headless.so"
from prims import *
from PIL import Image
g = G(ROM)
fw = C.c_int.in_dll(g.gfx, "harness_w"); fh = C.c_int.in_dll(g.gfx, "harness_h"); cnt = C.c_int.in_dll(g.gfx, "harness_count")
buf = (C.c_ubyte * (1024 * 1024 * 4)).in_dll(g.gfx, "harness_frame")
g.load(ENTRY)
for i in range(5): g.frame(0)
print(fw.value, fh.value, cnt.value)
w, h = fw.value, fh.value
Image.frombytes("RGBA", (w, h), bytes(buf[:w * h * 4])).convert("RGB").save(SP + "/vid/render_test.png")
