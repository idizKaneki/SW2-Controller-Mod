/* SW2Controller.asi - Samurai Warriors 2 (PC): controller fixes
 * Loaded by Ultimate ASI Loader (dinput8.dll), like SW2Widescreen.asi.
 * - RightStick: the game only reads the number of axes the controller reports
 *   (5 on an Xbox pad, so the right stick X axis, 6th axis, was ignored).
 *   The game now reads all 8 axes -> right stick = J1 Axis 5 (vertical) and Axis 6 (horizontal).
 * - [Icons] RotateRightStick: the "rotate map" prompt shows the right stick icon
 *   (needs the controller icon sheet installed by sw2_icons.py).
 * - NoAutoSetup: opening "Button settings" no longer asks "Use the gamepad's auto-setting?"
 *   (answering Yes by mistake erased the layout); the screen opens as if No was chosen.
 * - MenuConfirmA: in menus the game turns "Musou" into CONFIRM and "Jump" into CANCEL.
 *   These two entries are swapped: Jump (A) confirms, Musou (B) cancels. Battles are unchanged.
 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
typedef unsigned char u8; typedef unsigned int u32;
static char g_ini[260], g_logp[260];
static char g_log[2048]; static int g_loglen;

static void flushlog(void) {
    DWORD w; HANDLE h = CreateFileA(g_logp, 0x40000000, 1, 0, 2, 0x80, 0);
    if (h != (HANDLE)-1) { WriteFile(h, g_log, g_loglen, &w, 0); CloseHandle(h); }
}
static void lg(const char *s) { while (*s && g_loglen < (int)sizeof g_log - 1) g_log[g_loglen++] = *s++; }
static void lgn(int v) { char b[12]; int i = 11; b[i] = 0; if (v == 0) b[--i] = '0'; while (v > 0) { b[--i] = '0' + v % 10; v /= 10; } lg(b + i); }
static void lghex(u32 v) { char b[11]; int i; b[0]='0'; b[1]='x'; for (i = 0; i < 8; i++) b[2+i] = "0123456789ABCDEF"[(v >> (28 - 4*i)) & 15]; b[10]=0; lg(b); }

/* pattern search (0x100 = wildcard) */
static u8 *find(u8 *p, u32 n, const short *pat, int m) {
    u32 i; int j;
    for (i = 0; i + m <= n; i++) {
        for (j = 0; j < m; j++) if (pat[j] != 0x100 && p[i+j] != (u8)pat[j]) break;
        if (j == m) return p + i;
    }
    return 0;
}
static int same(const u8 *p, const short *pat, int m) { int j; for (j = 0; j < m; j++) if (pat[j] != 0x100 && p[j] != (u8)pat[j]) return 0; return 1; }
static void put(u8 *dst, const u8 *src, int n) {
    DWORD old; int i;
    VirtualProtect(dst, n, 0x40, &old);
    for (i = 0; i < n; i++) dst[i] = src[i];
    VirtualProtect(dst, n, old, &old);
    FlushInstructionCache(GetCurrentProcess(), dst, n);
}

/* controller constructor: mov eax,[esp+8] (axis count); push ebp; mov ebp,ecx; ...; mov [ebp+0x160],eax */
static const short P_AX[] = {0x8B,0x44,0x24,0x08,0x55,0x8B,0xE9,0x56,0x8B,0x74,0x24,0x0C,0x57,0xB9,0x41,0x00,0x00,0x00,
                             0x8B,0xFD,0xF3,0xA5,0x8B,0x4C,0x24,0x18,0x89,0x85,0x60,0x01,0x00,0x00};
/* push ebp; mov ebp,ecx; push 8; pop eax; nop -> 8 axes */
static const u8 C_AX[] = {0x55,0x8B,0xE9,0x6A,0x08,0x58,0x90};
/* menus: cmp ebx,0Dh; ja ...; jmp [ebx*4+table] (action -> menu button) */
static const short P_SW[] = {0x83,0xFB,0x0D,0x0F,0x87,0x100,0x100,0x100,0x100,0xFF,0x24,0x9D};
static const short P_SAUT[]  = {0xBE,0x06,0x00,0x00,0x00};   /* mov esi,6: CANCEL */
static const short P_MUSOU[] = {0xBE,0x07,0x00,0x00,0x00};   /* mov esi,7: CONFIRM */
/* "Button settings": call IsGamepadConnected ; test eax,eax ; jz skip_prompt ; mov edx,[prompt] ; push 1 ; push edx ; push 4 */
static const short P_AUTO[] = {0xE8,0x100,0x100,0x100,0x100,0x85,0xC0,0x0F,0x84,0x30,0xFF,0xFF,0xFF,0x8B,0x15,0x100,0x100,0x100,0x100,0x6A,0x01,0x52,0x6A,0x04};
static const u8 C_AUTO[] = {0x31,0xC0,0x90,0x90,0x90};      /* xor eax,eax -> "no gamepad": no prompt */

/* Icons: the "rotate map" prompt F0 'O' F0 'P' draws the keyboard camera keys.
 * The F12 sprite (code F0 'J' F0 'K') holds the right stick icon in the controller icon sheet:
 *   "rotate map" -> F0 J F0 K (right stick), and the old F12 prompts (config screen) -> plain text "F12 ".
 * Test=1/2 writes a test line in place of the rotate prompt instead (to find icon codes). */
static void icons(u8 *base) {
    static const u8 test1[] = "C\xf0" "C D\xf0" "D E\xf0" "E F\xf0" "F G\xf0" "G Q\xf0" "QR S\xf0" "S U\xf0" "U";
    static const u8 test2[] = "b\xf0" "b c\xf0" "c d\xf0" "d e\xf0" "e V\xf0" "V W\xf0" "W Y\xf0" "Y Z\xf0" "Z";
    int t, rs, pass, nr = 0, nf = 0, k;
    u32 pe = *(u32*)(base + 0x3C); int ns = *(unsigned short*)(base + pe + 6);
    u8 *sec0 = base + pe + 24 + *(unsigned short*)(base + pe + 20), *sec;
    t = (int)GetPrivateProfileIntA("Icons", "Test", 0, g_ini);
    rs = (int)GetPrivateProfileIntA("Icons", "RotateRightStick", 1, g_ini);
    if (!t && !rs) return;
    for (pass = 0; pass < 2; pass++)                    /* pass 0: F12 -> text, pass 1: rotate -> F12 sprite */
    for (k = 0, sec = sec0; k < ns; k++, sec += 40) {
        u8 *p = base + *(u32*)(sec + 12), *e = p + *(u32*)(sec + 8);
        if (sec[0] != '.' || (sec[1] != 'r' && sec[1] != 'd')) continue;   /* .rdata / .data */
        for (; p + 4 < e; p++) {
            DWORD old; u32 len, i;
            if (p[0] != 0xF0 || p[2] != 0xF0) continue;
            if (pass == 0 && !(p[1] == 'J' && p[3] == 'K')) continue;
            if (pass == 1 && !(p[1] == 'O' && p[3] == 'P')) continue;
            if (pass == 0 && t) continue;
            len = 0; while (p + len < e && p[len]) len++;
            VirtualProtect(p, len + 1, 0x04, &old);
            if (pass == 0) { p[0] = 'F'; p[1] = '1'; p[2] = '2'; p[3] = ' '; nf++; }
            else if (t) {
                const u8 *test = t == 2 ? test2 : test1;
                for (i = 0; i < len && test[i]; i++) p[i] = test[i];
                p[i] = 0; nr++;
            } else { p[1] = 'J'; p[3] = 'K'; nr++; }
            VirtualProtect(p, len + 1, old, &old);
        }
    }
    if (t) { lg("Icons: test line written in "); lgn(nr); lg(" text(s)\r\n"); }
    else { lg("Icons: rotate prompt -> right stick in "); lgn(nr); lg(" text(s), F12 prompt -> text in "); lgn(nf); lg("\r\n"); }
}

static DWORD WINAPI worker(LPVOID arg) {
    u8 *base = (u8*)GetModuleHandleA(0);
    u32 pe = *(u32*)(base + 0x3C);
    u8 *sec = base + pe + 24 + *(unsigned short*)(base + pe + 20);
    u8 *text = base + *(u32*)(sec + 12); u32 tsz = *(u32*)(sec + 8);
    int doax = (int)GetPrivateProfileIntA("Controller", "RightStick", 1, g_ini);
    int domenu = (int)GetPrivateProfileIntA("Controller", "MenuConfirmA", 1, g_ini);
    int doauto = (int)GetPrivateProfileIntA("Controller", "NoAutoSetup", 1, g_ini);
    u8 *kau = (u8*)0x475094, *pau = 0;
    int kau_ok;
    u8 *kax = (u8*)0x59EC30, *ksw = (u8*)0x5AF100;   /* known addresses (sw2.exe US/EU) */
    int kax_ok = text <= kax && kax + 32 <= text + tsz, ksw_ok = text <= ksw && ksw + 16 <= text + tsz;
    u8 *pax = 0, *psw = 0; u32 t0 = GetTickCount(), it = 0;
    kau_ok = text <= kau && kau + 24 <= text + tsz;
    (void)arg;
    lg("SW2Controller 1.0.1\r\n");
    icons(base);
    SetThreadPriority(GetCurrentThread(), 15);
    for (;;) {
        if (doax && !pax) {
            if (kax_ok && same(kax, P_AX, 32)) pax = kax;
            else if ((it & 255) == 0) pax = find(text, tsz, P_AX, 32);
            if (pax) { put(pax, C_AX, 7); lg("Right stick (8 axes): OK at "); lghex((u32)pax);
                       lg(" ("); lgn((int)(GetTickCount() - t0)); lg(" ms)\r\n");
                       { u32 *v = (u32*)0xF3CAD4; if (kax_ok && v[0] && v[1] > v[0]) { lg("  WARNING: controllers already initialised ("); lgn((int)((v[1]-v[0])/8)); lg(")\r\n"); } } }
        }
        if (domenu && !psw) {
            if (ksw_ok && same(ksw, P_SW, 12)) psw = ksw;
            else if ((it & 255) == 0) psw = find(text, tsz, P_SW, 12);
            if (psw) {
                u32 *tab = *(u32**)(psw + 12);
                u8 *a6 = (u8*)tab[6], *a7 = (u8*)tab[7];
                if (same(a6, P_SAUT, 5) && same(a7, P_MUSOU, 5)) {
                    u32 sw[2]; sw[0] = (u32)a7; sw[1] = (u32)a6;
                    put((u8*)&tab[6], (const u8*)sw, 8);
                    lg("Menus (A confirms, B cancels): OK at "); lghex((u32)tab); lg("\r\n");
                } else lg("Menus: table already patched or unexpected, nothing done\r\n");
            }
        }
        if (doauto && !pau) {
            if (kau_ok && same(kau, P_AUTO, 24)) pau = kau;
            else if ((it & 255) == 0) pau = find(text, tsz, P_AUTO, 24);
            if (pau) { put(pau, C_AUTO, 5); lg("Button settings: auto-setting prompt removed at "); lghex((u32)pau); lg("\r\n"); }
        }
        if ((pax || !doax) && (psw || !domenu) && (pau || !doauto)) break;
        if (GetTickCount() - t0 > 60000) break;
        it++;
        Sleep(0);
    }
    SetThreadPriority(GetCurrentThread(), 0);
    if (doax && !pax) lg("ERROR: axis code not found\r\n");
    if (domenu && !psw) lg("ERROR: menu table not found\r\n");
    if (doauto && !pau) lg("ERROR: auto-setting prompt not found\r\n");
    if (!doax) lg("Right stick: disabled\r\n");
    if (!domenu) lg("Menus: disabled\r\n");
    flushlog();
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID res) {
    (void)res;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(inst);
        int i, n, k;
        const char *a = "SW2Controller.ini", *b = "SW2Controller.log";
        n = (int)GetModuleFileNameA(inst, g_ini, 240);
        for (i = n; i > 0 && g_ini[i-1] != '\\' && g_ini[i-1] != '/'; i--) ;
        for (k = 0; k < i; k++) g_logp[k] = g_ini[k];
        for (k = 0; a[k]; k++) g_ini[i+k] = a[k]; g_ini[i+k] = 0;
        for (k = 0; b[k]; k++) g_logp[i+k] = b[k]; g_logp[i+k] = 0;
        CreateThread(0, 0, worker, 0, 0, 0);
    }
    return 1;
}
