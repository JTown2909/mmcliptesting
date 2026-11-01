"""Top-down video of a setup: per-frame Link position/facing/camera from the emulator, drawn over
the room's wall polygons, with the current input step labelled. Usage: pathvideo.py out.mp4 "steps" extra title"""
import sys, math, subprocess, re; sys.path.insert(0, "."); sys.path.insert(0, "../emu")
from verify import *
from colgeo import static_polys
from PIL import Image, ImageDraw, ImageFont
out, steps, extra, title = sys.argv[1], [a.strip() for a in sys.argv[2].split("|")], int(sys.argv[3]), sys.argv[4]
g = G(ROM); g.load(ENTRY)
walls = [p for p in static_polys(g) if abs(p["n"][1]) < 0.5 and min(v[1] for v in p["v"]) < 60 and max(v[1] for v in p["v"]) >= 0]
frames = []  # (x, z, facing, cam, label)
cur = ["start"]
orig_frame = g.frame
def rec_frame(b=0, x=0, y=0, n=1):
    for _ in range(n):
        orig_frame(b, x, y)
        px, py, pz, f = g.pos()
        frames.append((px, pz, f, g.cam(), cur[0]))
g.frame = rec_frame
g.run([(6, 0, 0, 0)])
for i, a in enumerate(steps):
    cur[0] = f"{i + 1}/{len(steps)}  {a}"
    do(g, a)
cur[0] = f"hold Z + Up {4 + extra} frames, then A"
g.run(final_walk(extra) + [(20, 0, 0, 127)])
clipped = any(z > 845 and x > -240 for x, z, *_ in frames)
# view: x in [-420, 90], z in [100, 980]; screen x grows with -x so Link's "right" (−x) is on the right
W, H, S = 720, 960, 1.05
def P(x, z): return ((80 - x) * S + 40, H - ((z - 110) * S + 20))
font = ImageFont.load_default()
proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                         "-r", "20", "-i", "-", "-pix_fmt", "yuv420p", "-vcodec", "libx264", out], stdin=subprocess.PIPE)
base = Image.new("RGB", (W, H), (24, 26, 32)); d = ImageDraw.Draw(base)
for p in walls:
    pts = sorted({(v[0], v[2]) for v in p["v"]})
    d.line([P(*pts[0]), P(*pts[-1])], fill=(150, 150, 160), width=3)
d.ellipse([*(c - 5 for c in P(-240, 840)), *(c + 5 for c in P(-240, 840))], outline=(255, 80, 80), width=2)
trail = []
for k, (x, z, f, c, lab) in enumerate(frames):
    im = base.copy(); dr = ImageDraw.Draw(im)
    trail.append(P(x, z))
    if len(trail) > 1: dr.line(trail, fill=(90, 170, 255), width=2)
    px, pz = P(x, z)
    dr.ellipse([px - 7, pz - 7, px + 7, pz + 7], fill=(120, 220, 120))
    fa = f / 65536 * 2 * math.pi; ca = c / 65536 * 2 * math.pi
    dr.line([(px, pz), P(x + 22 * math.sin(fa), z + 22 * math.cos(fa))], fill=(255, 255, 255), width=3)
    dr.line([(px, pz), P(x - 30 * math.sin(ca), z - 30 * math.cos(ca))], fill=(255, 200, 60), width=1)
    dr.text((12, 10), title, fill=(255, 255, 255), font=font)
    dr.text((12, 28), lab, fill=(255, 230, 120), font=font)
    dr.text((12, 46), f"frame {k:4d}  x={x:.4f} z={z:.4f}  facing={f:04X} cam={c:04X}", fill=(200, 200, 200), font=font)
    dr.text((12, H - 40), "white = facing, yellow = camera side, red circle = clip corner. Screen right = Link's right at entry (−x).", fill=(160, 160, 160), font=font)
    if clipped and z > 845 and x > -240: dr.text((W // 2 - 20, 60), "CLIP", fill=(255, 80, 80), font=font)
    proc.stdin.write(im.tobytes())
for _ in range(20): proc.stdin.write(im.tobytes())
proc.stdin.close(); proc.wait()
print(out, "frames", len(frames), "clip", clipped)
