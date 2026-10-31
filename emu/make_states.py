"""usage: make_states.py ROM KZS OUT.m64  -- load a kz state and save a native mupen64plus state"""
import sys
from kzload import *
e = boot_and_load(sys.argv[1], sys.argv[2])
print(sys.argv[2], link_pos(e))
e.save(sys.argv[3])
