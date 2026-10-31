# Headless MM (JP 1.0) harness

* `m64.py` – lockstep ctypes frontend for mupen64plus-core (frame callback = one game frame).
  `save()` runs one frame with the held input, then snapshots; the held input is
  stored next to the state (`.inp`) because the controller is read after the snapshot.
  Inputs take effect one frame after they are set.
* `input_plugin.c`, `video_stub.c` – minimal plugins (the stub video plugin just raises
  the DP interrupt so the game keeps running without rendering).
* `kzload.py` – boots the kz-lite ROM and loads a `.kzs` state by writing it into kz's heap.
* `game.py`, `colgeo.py` – Link/camera addresses and static collision dump.

Build (see session notes): SDL2 (no video/audio), mupen64plus-core with
`VULKAN=0 OSD=0 NETPLAY=0 DEBUGGER=0 GL_CFLAGS= GL_LDLIBS=`, savestates written with
gzip level 0, mupen64plus-rsp-hle, and the two plugins here:
`gcc -O2 -shared -fPIC -I<core>/src/api -o harness-input.so input_plugin.c`.
