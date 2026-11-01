#!/usr/bin/env bash
# One-time environment setup for headless emulation (Debian/Ubuntu container).
set -euo pipefail
apt-get update -q
apt-get install -y -q mupen64plus-ui-console mupen64plus-data mupen64plus-video-rice \
  mupen64plus-video-glide64mk2 mupen64plus-rsp-hle mupen64plus-audio-sdl mupen64plus-input-sdl \
  xvfb zstd lua5.4 libegl1 libgl1-mesa-dri libglx-mesa0
pip install capstone || true
here="$(cd "$(dirname "$0")" && pwd)"
gcc -shared -fPIC -O2 -o "$here/scriptinput/scriptinput.so" "$here/scriptinput/scriptinput.c"
mkdir -p ~/.local/share/mupen64plus/screenshot
if ! pgrep -x Xvfb >/dev/null; then
  rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
  (Xvfb :99 -screen 0 640x480x24 >/dev/null 2>&1 &)
fi
echo "Done. Run emulator tools with: DISPLAY=:99 SDL_AUDIODRIVER=dummy python3 tools/..."
