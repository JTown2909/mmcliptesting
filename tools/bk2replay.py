"""Replay a BizHawk .bk2 (Mupen64Plus core, starts from savestate) in headless mupen64plus.

BizHawk logs one input row per VI; the game polls once per game frame. Each emulator callback (one game
frame) sets the controller to the row at (VIs since start + offset). Sync is approximate: check milestones.

Usage: python3 tools/bk2replay.py ROM MOVIE.bk2 [--offset N] [--frames N] [--heaplog FILE]
Prints milestones: held actor, Link angle changes, Moon Stone draw pointer, ACE, scene change.
--heaplog writes every actor-heap allocation/free (per game frame) with actor/overlay labels.
"""
import argparse, os, sys, tempfile, zipfile, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m64sim import *
from bizstate import BizState
import heapscan

P, SC, PATCH, MOON_DRAW = 0x803FFFA0, 0x801EF460, 0x80413A03, 0x80419FCC
BTN = [None, None, None, None, DU, DD, DL, DR, START, Z, B, A, CU, CD, CL, CR, L, R]  # after X,Y

def parse(path):
    z = zipfile.ZipFile(path)
    rows = []
    for line in z.read("Input Log.txt").decode().splitlines():
        if not line.startswith("|") or "LogKey" in line: continue
        f = line.strip("|").split("|")
        x, y, btns = f[1].split(",")
        b = 0
        for i, c in enumerate(btns):
            if c != "." and i < len(BTN) and BTN[i]: b |= BTN[i]
        rows.append(stick(int(x), int(y)) | b)
    tmp = tempfile.mkdtemp()
    open(os.path.join(tmp, "s.State"), "wb").write(open(path, "rb").read())
    st = BizState(os.path.join(tmp, "s.State")); stpath = os.path.join(tmp, "start.st"); st.m64p(stpath)
    return rows, stpath

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom"); ap.add_argument("movie")
    ap.add_argument("--offset", type=int, default=0); ap.add_argument("--frames", type=int, default=3000)
    ap.add_argument("--heaplog")
    a = ap.parse_args()
    rows, stpath = parse(a.movie)
    sim = Sim(rom=a.rom, input_so=os.path.join(os.path.dirname(os.path.abspath(__file__)), "scriptinput", "scriptinput.so"))
    st = {"vi0": None, "last": None, "nodes": None}
    hl = open(a.heaplog, "w") if a.heaplog else None

    from actor_names import ACTOR_NAMES
    def heap_nodes(s):
        """Walk the actor arena from its head with direct RAM reads (fast). Returns node -> (free, size, label)."""
        out, cur = {}, 0x803FFF70
        for _ in range(4000):
            if s.r16(cur) != 0x7373: break
            free, size = s.r16(cur + 2), s.r32(cur + 4)
            lab = ""
            if not free and size >= 0x144:
                aid, cat = s.r16(cur + 0x30), s.r8(cur + 0x32)
                if aid in ACTOR_NAMES and cat < 12: lab = ACTOR_NAMES[aid]
            out[cur & 0x7FFFFF] = (free, size, lab)
            nxt = s.r32(cur + 8)
            if nxt == 0: break
            cur = nxt
        return out

    def script(s, n):
        if n == 2: s.load_state(stpath)
        if n < 5: return True
        if st["vi0"] is None: st["vi0"] = s.vi()
        vi = s.vi() - st["vi0"]
        i = vi + a.offset
        s.buttons(rows[i] if 0 <= i < len(rows) else 0)
        snap = (s.r32(P + 0x34C), s.r16(P + 0xBE), s.r16(P + 0xAD4), s.r16(P + 0xAD6), s.r32(MOON_DRAW),
                s.r8(PATCH), s.r32(SC))
        if snap != st["last"]:
            held, sh, yw, par, md, pb, ent = snap
            print(f"frame {n:5d} VI {vi:5d} held={held:08X} shape={sh:04X} yaw={yw:04X} par={par:04X} "
                  f"moonDraw={md:08X} patch={pb:02X} entr={ent:04X}", flush=True)
            st["last"] = snap
        if hl and n % 1 == 0:
            cur = heap_nodes(s); prev = st["nodes"]
            if prev is not None:
                for k in sorted(set(prev) | set(cur)):
                    if prev.get(k) != cur.get(k):
                        hl.write(f"frame {n} VI {vi} node {0x80000000|k:08X} {prev.get(k)} -> {cur.get(k)}\n")
            st["nodes"] = cur
        return n < a.frames and vi < len(rows) + 200
    sim.run(script)

if __name__ == "__main__":
    main()
