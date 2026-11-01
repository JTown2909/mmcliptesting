"""Render real game footage (angrylion software renderer + LLE RSP) of a setup, with a caption bar
showing the current step, Link's position/facing and the camera angle.
usage: gamevideo.py out.mp4 "step | step | ..." walk_extra "title" """
import sys, os, ctypes as C, subprocess
os.environ["M64_GFX"] = "video-angrylion-headless.so"; os.environ["M64_RSP"] = "mupen64plus-rsp-cxd4.so"
sys.path.insert(0, ".")
from verify import *
from PIL import Image, ImageDraw, ImageFont
out, steps, extra, title = sys.argv[1], [a.strip() for a in sys.argv[2].split("|")], int(sys.argv[3]), sys.argv[4]
g = G(ROM)
fw = C.c_int.in_dll(g.gfx, "harness_w"); fh = C.c_int.in_dll(g.gfx, "harness_h")
buf = (C.c_ubyte * (1024 * 1024 * 4)).in_dll(g.gfx, "harness_frame")
W, H, BAR = 640, 480, 70
font = ImageFont.load_default()
proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H + BAR}",
                         "-r", "20", "-i", "-", "-pix_fmt", "yuv420p", "-vcodec", "libx264", "-crf", "20", out], stdin=subprocess.PIPE)
cur = ["entering"]; nframes = [0]; clip = [False]
orig = g.frame
def frame(b=0, x=0, y=0, n=1):
    for _ in range(n):
        orig(b, x, y)
        w, h = fw.value, fh.value
        img = Image.frombytes("RGBA", (w, h), bytes(buf[:w * h * 4])).convert("RGB").resize((W, H), Image.NEAREST)
        canvas = Image.new("RGB", (W, H + BAR), (0, 0, 0)); canvas.paste(img, (0, 0))
        d = ImageDraw.Draw(canvas)
        px, py, pz, f = g.pos()
        if pz > 845 and px > -240: clip[0] = True
        btn = " ".join(n for n, m in (("A", A), ("Z", Z), ("R", R)) if b & m)
        d.text((8, H + 4), title, fill=(255, 255, 255), font=font)
        d.text((8, H + 20), cur[0], fill=(255, 230, 120), font=font)
        d.text((8, H + 36), f"x={px:.4f} z={pz:.4f} facing={f:04X} cam={g.cam():04X}", fill=(200, 200, 200), font=font)
        d.text((8, H + 52), f"input: stick ({x},{y}) {btn}" + ("    CLIP" if clip[0] else ""), fill=(160, 220, 255), font=font)
        proc.stdin.write(canvas.tobytes()); nframes[0] += 1
g.frame = frame
g.load(ENTRY); g.run([(6, 0, 0, 0)])
for i, a in enumerate(steps):
    cur[0] = f"step {i + 1}/{len(steps)}: {a}"; do(g, a)
cur[0] = f"hold Z + Up for {4 + extra} frames, then A"
g.run(final_walk(extra) + [(30, 0, 0, 127)])
proc.stdin.close(); proc.wait()
print(out, nframes[0], "frames, clip" if clip[0] else "frames, NO CLIP")
