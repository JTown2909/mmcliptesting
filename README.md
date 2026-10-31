# MM JP 1.0 credits-warp / ACE research tools

| file | what |
|---|---|
| `tools/mm_ace_watch.lua` | BizHawk Lua: live heap viewer (Zelda arena: every node, free/used, size, actor + overlay labels) and Link angle/position watches. Also prints the address of the `0xFFF1` byte in `ovl_En_Test4` that the credits warp patches. |
| `tools/heapscan.py` | Same heap walk, offline, on a big-endian RDRAM dump. |
| `tools/m64run.py` | Headless mupen64plus frontend (ctypes) that dumps RDRAM at a given frame. |
| `tools/actor_names.py` | Actor ID -> name table generated from zeldaret/mm `actor_table.h`. |
| `tools/kzs.py` | kz-lite `.kzs` savestate decoder. |

Notes (verified on JP 1.0 RAM):
- JP arena nodes are 0x30 bytes (debug-style `ArenaNode`), so actor data = node + 0x30.
- The credits warp's patched byte is `ovl_En_Test4` code + 0xF33 (`ori t4, zero, 0xFFF1` at +0xF30).
  In the current route, 0x80413A03 therefore means En_Test4's overlay code starts at 0x80412AD0.
