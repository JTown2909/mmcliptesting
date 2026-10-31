import sys, struct, numpy as np; sys.path.insert(0, __import__('os').path.dirname(__file__))
from prims import *
g = G(ROM); g.load(ENTRY)
ram = g.rdram_bytes()
pat = struct.pack(">5H", 0, 0x32, 0x64, 0x96, 0xC9)
i = ram.find(pat); print(hex(i), ram.count(pat))
tab = np.array(struct.unpack(">1024H", ram[i:i+2048]), dtype=np.int32)
print(tab[:6], tab[-3:]); np.save("sintab.npy", tab)
