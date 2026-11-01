/* Minimal mupen64plus input plugin whose controller-1 state is set from the frontend
 * (ctypes) via script_set_buttons(). Build:
 *   gcc -shared -fPIC -O2 -o scriptinput.so scriptinput.c
 */
#include <stdint.h>
#include <string.h>
#define EXPORT __attribute__((visibility("default")))
typedef struct { int Present, RawData, Plugin; } CONTROL;
typedef struct { CONTROL *Controls; } CONTROL_INFO;
static uint32_t g_buttons;
EXPORT void script_set_buttons(uint32_t b) { g_buttons = b; }
EXPORT int PluginStartup(void *h, void *c, void *d) { return 0; }
EXPORT int PluginShutdown(void) { return 0; }
EXPORT int PluginGetVersion(int *type, int *ver, int *api, const char **name, int *caps) {
    if (type) *type = 4; if (ver) *ver = 0x010000; if (api) *api = 0x020100;
    if (name) *name = "scriptinput"; if (caps) *caps = 0; return 0; }
EXPORT void InitiateControllers(CONTROL_INFO info) {
    for (int i = 0; i < 4; i++) { info.Controls[i].Present = (i == 0); info.Controls[i].RawData = 0; info.Controls[i].Plugin = 1; } }
EXPORT void GetKeys(int ctl, uint32_t *keys) { *keys = ctl == 0 ? g_buttons : 0; }
EXPORT void ControllerCommand(int c, unsigned char *cmd) {}
EXPORT void ReadController(int c, unsigned char *cmd) {}
EXPORT int RomOpen(void) { return 1; }
EXPORT void RomClosed(void) {}
EXPORT void SDL_KeyDown(int k, int s) {}
EXPORT void SDL_KeyUp(int k, int s) {}
EXPORT void RenderCallback(void) {}
