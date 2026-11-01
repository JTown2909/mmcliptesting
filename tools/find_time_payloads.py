"""Enumerate credits-warp filename payloads that set the clock to 00:00-05:59 (instant midnight bell).

Payload shape (JP 1.0):
  created file:  j 0x801EF48C ; xori a2, a0, IMM      (a0 = Obj_Moon_Stone actor at draw time)
  playing file:  j 0x800ECD3C ; sb   a2, OFF(a2)      (writes F6 over En_Test4's FFF1 low byte, then
                                                      runs CutsceneCmd_SetTime with time bytes at a2+6/a2+7)
Constraints: a2 low byte must be F6, a2+OFF == patch byte, every filename byte <= 0xDE (typeable).
Usage: python3 find_time_payloads.py s6.rdram [a0=0x80419E90] [patch=0x80413A03]
"""
import sys

JP = ("0123456789"
      "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
      "ぁぃぅぇぉっゃゅょがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ"
      "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
      "ァィゥェォッャュョガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポヴ"
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
assert len(JP) == 0xDF

def name(bs): return "".join(JP[b] if b < len(JP) else f"<{b:02X}>" for b in bs)

def settime(h, m):
    t = int(h * 60.0 / (1440 / 65536)) + int((m + 1) / (1440 / 65536))
    return t & 0xFFFF

def main():
    d = open(sys.argv[1], "rb").read()
    a0 = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x80419E90
    patch = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x80413A03
    for hi in range(0x100):
        a2 = (a0 & 0xFFFF0000) | (hi << 8) | 0xF6
        off = patch - a2
        if not -0x8000 <= off < 0x8000: continue
        imm, off16 = (a0 ^ a2) & 0xFFFF, off & 0xFFFF
        f1 = bytes.fromhex("0807BD233886") + imm.to_bytes(2, "big")
        f2 = bytes.fromhex("0803B34FA0C6") + off16.to_bytes(2, "big")
        if max(f1 + f2) > 0xDE: continue
        h, m = d[(a2 + 6) & 0x7FFFFF], d[(a2 + 7) & 0x7FFFFF]
        t = settime(h, m)
        if t < 0x4000:
            mins = t * 1440 / 65536
            print(f"a2={a2:08X} time {int(mins // 60):02d}:{int(mins % 60):02d}  "
                  f"file1 {f1.hex().upper()} {name(f1)}   file2 {f2.hex().upper()} {name(f2)}")

if __name__ == "__main__":
    main()
