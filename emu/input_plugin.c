/* Minimal mupen64plus input plugin: controller 1 state is whatever the
 * harness writes into harness_buttons (BUTTONS union, 32 bits). */
#include <string.h>
#include "m64p_types.h"
#include "m64p_plugin.h"

#define EXPORT __attribute__((visibility("default")))

EXPORT volatile unsigned int harness_buttons = 0;
EXPORT volatile int harness_polls = 0;

EXPORT m64p_error CALL PluginStartup(m64p_dynlib_handle h, void *ctx, void (*dbg)(void *, int, const char *)) { return M64ERR_SUCCESS; }
EXPORT m64p_error CALL PluginShutdown(void) { return M64ERR_SUCCESS; }
EXPORT m64p_error CALL PluginGetVersion(m64p_plugin_type *t, int *v, int *api, const char **name, int *caps) {
    if (t) *t = M64PLUGIN_INPUT; if (v) *v = 0x020000; if (api) *api = 0x020100;
    if (name) *name = "harness input"; if (caps) *caps = 0; return M64ERR_SUCCESS;
}
EXPORT void CALL InitiateControllers(CONTROL_INFO ci) {
    for (int i = 0; i < 4; i++) { ci.Controls[i].Present = i == 0; ci.Controls[i].RawData = 0; ci.Controls[i].Plugin = PLUGIN_NONE; }
}
EXPORT void CALL GetKeys(int c, BUTTONS *k) { if (c == 0) { k->Value = harness_buttons; harness_polls++; } else k->Value = 0; }
EXPORT void CALL ControllerCommand(int c, unsigned char *cmd) {}
EXPORT void CALL ReadController(int c, unsigned char *cmd) {}
EXPORT int CALL RomOpen(void) { return 1; }
EXPORT void CALL RomClosed(void) {}
EXPORT void CALL SDL_KeyDown(int m, int k) {}
EXPORT void CALL SDL_KeyUp(int m, int k) {}
EXPORT void CALL RenderCallback(void) {}
