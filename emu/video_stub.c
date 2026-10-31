/* Stub mupen64plus video plugin: draws nothing, but completes every display
 * list by raising the DP interrupt so the game keeps running headless. */
#include "m64p_types.h"
#include "m64p_plugin.h"
#define EXPORT __attribute__((visibility("default")))
static GFX_INFO gi;
EXPORT m64p_error CALL PluginStartup(m64p_dynlib_handle h, void *c, void (*d)(void *, int, const char *)) { return M64ERR_SUCCESS; }
EXPORT m64p_error CALL PluginShutdown(void) { return M64ERR_SUCCESS; }
EXPORT m64p_error CALL PluginGetVersion(m64p_plugin_type *t, int *v, int *api, const char **n, int *caps) {
    if (t) *t = M64PLUGIN_GFX; if (v) *v = 0x020000; if (api) *api = 0x020200; if (n) *n = "stub video"; if (caps) *caps = 0; return M64ERR_SUCCESS; }
EXPORT void CALL ChangeWindow(void) {}
EXPORT int CALL InitiateGFX(GFX_INFO g) { gi = g; return 1; }
EXPORT void CALL MoveScreen(int x, int y) {}
static void dp_done(void) { *gi.MI_INTR_REG |= 0x20; gi.CheckInterrupts(); }
EXPORT void CALL ProcessDList(void) { dp_done(); }
EXPORT void CALL ProcessRDPList(void) { *gi.DPC_CURRENT_REG = *gi.DPC_END_REG; dp_done(); }
EXPORT void CALL RomClosed(void) {}
EXPORT int CALL RomOpen(void) { return 1; }
EXPORT void CALL ShowCFB(void) {}
EXPORT void CALL UpdateScreen(void) {}
EXPORT void CALL ViStatusChanged(void) {}
EXPORT void CALL ViWidthChanged(void) {}
EXPORT void CALL ReadScreen2(void *d, int *w, int *h, int f) { if (w) *w = 0; if (h) *h = 0; }
EXPORT void CALL SetRenderingCallback(void (*cb)(int)) {}
EXPORT void CALL ResizeVideoOutput(int w, int h) {}
EXPORT void CALL FBRead(unsigned int a) {}
EXPORT void CALL FBWrite(unsigned int a, unsigned int s) {}
EXPORT void CALL FBGetFrameBufferInfo(void *p) {}
