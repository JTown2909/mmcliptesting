"""Execute an ESS plan in the emulator from a state and report shape/yaw/parallelYaw after each phase.
Plan items: ("cw", target_angle) / ("ccw", target_angle) = ESS-rotate until shape == target (one 0x708 step per
frame, stick kept ~45 deg ahead); ("up",) = hold ESS up until Link stops turning; ("zup", wait) = tap Z, wait `wait` frames, then ESS up; ("z",) = tap Z.
Usage: python3 tools/ess_plan_test.py ROM STATE "PLAN"   e.g. "[('cw',0x8103),('up',),('cw',0x2CA1),('z',)]"
"""
import sys, os, math, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m64sim import *
from bizstate import BizState
P = 0x803FFFA0

def main():
    rom, state, plan = sys.argv[1], sys.argv[2], eval(sys.argv[3])
    if state.endswith(".State"):
        t = os.path.join(tempfile.mkdtemp(), "s.st"); BizState(state).m64p(t); state = t
    sim = Sim(rom=rom, input_so=os.path.join(os.path.dirname(os.path.abspath(__file__)), "scriptinput", "scriptinput.so"))
    st = {"i": 0, "wait": 0, "cam": None, "stable": 0, "prev": None, "log": [], "t0": None}
    def angle(s): return s.r16(P + 0xBE)
    def script(s, n):
        if n == 2: s.load_state(state); return True
        if n < 20: s.buttons(0); return True
        sh = angle(s)
        if st["cam"] is None: st["cam"] = sh
        if st["i"] >= len(plan):
            st["log"].append(("end", sh, s.r16(P + 0xAD4), s.r16(P + 0xAD6))); return False
        step = plan[st["i"]]
        if step[0] in ("cw", "ccw"):
            if sh == step[1]:
                s.buttons(0); st["log"].append((f"{step[0]} to {step[1]:04X}", sh, s.r16(P + 0xAD4), s.r16(P + 0xAD6)))
                st["i"] += 1; st["wait"] = n
            else:
                lead = -0x2000 if step[0] == "cw" else 0x2000
                rel = ((sh + lead - st["cam"]) & 0xFFFF) * 2 * math.pi / 0x10000
                s.buttons(stick(round(-20 * math.sin(rel)), round(20 * math.cos(rel))))
                if n - st["wait"] > 200: st["log"].append(("timeout", sh, 0, 0)); return False
        elif step[0] == "up":
            s.buttons(stick(0, 20))
            st["stable"] = st["stable"] + 1 if sh == st["prev"] else 0
            if st["stable"] >= 4:
                s.buttons(0); st["cam"] = sh
                st["log"].append(("ess up", sh, s.r16(P + 0xAD4), s.r16(P + 0xAD6))); st["i"] += 1; st["stable"] = 0
        elif step[0] == "zup":          # tap Z (camera re-centres behind Link), wait, then ESS up
            if st["t0"] is None: st["t0"] = n
            k = n - st["t0"]
            if k < 3: s.buttons(Z)
            elif k < 3 + step[1] if len(step) > 1 else k < 15: s.buttons(0)
            else:
                s.buttons(stick(0, 20))
                st["stable"] = st["stable"] + 1 if sh == st["prev"] else 0
                if st["stable"] >= 4:
                    s.buttons(0); st["cam"] = sh; st["t0"] = None; st["stable"] = 0
                    st["log"].append(("Z + ess up", sh, s.r16(P + 0xAD4), s.r16(P + 0xAD6))); st["i"] += 1
        elif step[0] == "z":
            if st["t0"] is None: st["t0"] = n
            s.buttons(Z if n - st["t0"] < 3 else 0)
            if n - st["t0"] > 8:
                st["log"].append(("Z", sh, s.r16(P + 0xAD4), s.r16(P + 0xAD6))); st["i"] += 1; st["t0"] = None
        st["prev"] = sh
        return n < 2000
    sim.run(script)
    for what, sh, yw, par in st["log"]:
        print(f"{what:16s} shape={sh:04X} yaw={yw:04X} parallelYaw={par:04X}")

if __name__ == "__main__":
    main()
