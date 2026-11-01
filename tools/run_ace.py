"""Run the credits-warp ACE from a savestate in headless mupen64plus and report key frames.

Usage (needs DISPLAY with Xvfb; see tools/setup_env.sh):
  python3 tools/run_ace.py ROM STATE [options]

STATE is a BizHawk .State (converted on the fly) or an m64p .st (gzip).
Options:
  --name1 HEX16      overwrite created-file name bytes at 0x8050B28C (e.g. 0807BD233886AC66)
  --name2 HEX16      overwrite playing-file name bytes at 0x801EF48C (e.g. 0803B34FA0C6070D)
  --time HH:MM       set gSaveContext.save.time right after loading
  --drop HEX         force Moon Stone draw pointer to 0x8040<HEX> (pot drop angle test)
  --lookdown VI      frame to push the stick the other way (stop the ACE); default never
  --frames N         total VI frames to run (default 600)
  --shot VI          take a screenshot at this frame (repeatable); saved under the core's screenshot dir

Input script: C-Up held VI 20-25, then stick (0,-80) = look up from VI 60.
Printed events: ACE fired (En_Test4 patch byte became F6), En_Test4 daytimeIndex/nextBell changes,
scene change (gSaveContext.save.entrance leaves 0x4C10 = observatory), and "alive" every 100 VI.
If "alive" stops, the game stopped producing frames (crash/hang).
"""
import argparse, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m64sim import Sim, CU, stick
from bizstate import BizState

SC = 0x801EF460          # gSaveContext (JP 1.0)
T4 = 0x80414540          # En_Test4 instance in the route's heap layout
PATCH = 0x80413A03       # En_Test4 code byte that becomes F6
NAME1, NAME2 = 0x8050B28C, 0x801EF48C
MOON_DRAW = 0x80419FCC   # Obj_Moon_Stone instance + 0x13C (draw func)
OBSERVATORY_ENTRANCE = 0x4C10

def hours(t): return f"{t * 1440 / 65536 / 60:.3f}h"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom"); ap.add_argument("state")
    ap.add_argument("--name1"); ap.add_argument("--name2"); ap.add_argument("--time")
    ap.add_argument("--drop"); ap.add_argument("--lookdown", type=int, default=10**9)
    ap.add_argument("--frames", type=int, default=600)
    ap.add_argument("--shot", type=int, action="append", default=[])
    ap.add_argument("--input-so", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                       "scriptinput", "scriptinput.so"))
    a = ap.parse_args()

    state = a.state
    if state.endswith(".State"):
        tmp = os.path.join(tempfile.mkdtemp(), "state.st"); BizState(state).m64p(tmp); state = tmp

    sim = Sim(rom=a.rom, input_so=a.input_so)
    ev, last = {}, {}
    def note(k, n, msg):
        if k not in ev: ev[k] = n; print(f"VI {n:5d} {msg}", flush=True)

    def script(s, n):
        if n == 2: s.load_state(state)
        if n == 5:
            if a.time:
                h, m = map(int, a.time.split(":")); s.w16(SC + 0xC, (h * 60 + m) * 0x10000 // 1440)
            if a.name1: s.wbytes(NAME1, bytes.fromhex(a.name1))
            if a.name2: s.wbytes(NAME2, bytes.fromhex(a.name2))
            if a.drop: s.w32(MOON_DRAW, 0x80400000 | int(a.drop, 16))
        if 20 <= n < 26: s.buttons(CU)
        elif 60 <= n < a.lookdown: s.buttons(stick(0, -80))
        elif n >= a.lookdown: s.buttons(stick(0, 80))
        else: s.buttons(0)
        if n % 100 == 0: print(f"VI {n:5d} alive", flush=True)
        if n in a.shot: s.screenshot()
        if n > 10:
            t, ent = s.r16(SC + 0xC), s.r32(SC)
            if s.r8(PATCH) == 0xF6: note("ace", n, f"ACE fired, time {hours(t)}")
            if ent == OBSERVATORY_ENTRANCE:
                dti, nb = s.r8(T4 + 0x144), s.r16(T4 + 0x148)
                if (last.get("dti"), last.get("nb")) != (dti, nb):
                    print(f"VI {n:5d} En_Test4 daytimeIdx={dti} nextBell={hours(nb)} time={hours(t)}", flush=True)
                    last.update(dti=dti, nb=nb)
            else:
                note("ent", n, f"scene change, entrance {ent:04X}")
        return n < a.frames
    sim.run(script)

if __name__ == "__main__":
    main()
