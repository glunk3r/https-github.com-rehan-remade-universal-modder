/* m2033fix: dinput8.dll proxy for the original Metro 2033 (2010, Steam 43110, metro2033.exe 1.0.0.1).
 *
 * The exe on disk is never touched. On the game's first DirectInput8Create call (after SteamStub has
 * decrypted .text) the proxy checks the exe identity and the exact bytes at each site, applies the enabled
 * in-memory patches, then forwards to the system dinput8.dll. Any mismatch skips that patch (vanilla).
 * Mechanism, patch list, verification and rollback: README.md (P1, P4, P5; P2 and P3 were dropped in 0.2).
 * Build: build.ps1 (zig cc, x86-windows-gnu, kernel32 only, no CRT).
 */
#include <windows.h>

typedef HRESULT(WINAPI *DI8Create)(HINSTANCE, DWORD, REFIID, LPVOID *, LPUNKNOWN);

#define GAME_BASE 0x00400000u
#define GAME_SIZE 0x00B64000u
#define GAME_STAMP 0x4C7775B7u

static HMODULE g_self;
static DI8Create g_real;
static volatile LONG g_once;
static WCHAR g_dir[MAX_PATH]; /* folder of this DLL (the game folder), with trailing backslash */
static HANDLE g_log = INVALID_HANDLE_VALUE;

/* -nostdlib: the compiler may still emit calls to these */
void *memcpy(void *d, const void *s, unsigned n) {
    unsigned char *a = d;
    const unsigned char *b = s;
    while (n--) *a++ = *b++;
    return d;
}
void *memset(void *d, int c, unsigned n) {
    unsigned char *a = d;
    while (n--) *a++ = (unsigned char)c;
    return d;
}
unsigned strlen(const char *s) {
    unsigned n = 0;
    while (s[n]) n++;
    return n;
}
static int same(const unsigned char *a, const unsigned char *b, unsigned n) {
    while (n--)
        if (*a++ != *b++) return 0;
    return 1;
}

/* ---- tiny logger (init-time only) ---- */
static void put(const char *s) {
    DWORD n = 0, w;
    if (g_log == INVALID_HANDLE_VALUE) return;
    while (s[n]) n++;
    WriteFile(g_log, s, n, &w, NULL);
}
static void put_hex(unsigned v, int digits) {
    char b[11];
    int i;
    b[0] = '0';
    b[1] = 'x';
    for (i = 0; i < digits; i++) b[2 + i] = "0123456789ABCDEF"[(v >> ((digits - 1 - i) * 4)) & 15];
    b[2 + digits] = 0;
    put(b);
}
static void put_dec(unsigned v) {
    char b[12];
    int i = 11;
    b[i] = 0;
    do b[--i] = (char)('0' + v % 10); while (v /= 10);
    put(b + i);
}
static void put_bytes(const unsigned char *p, unsigned n) {
    unsigned i;
    char b[4];
    for (i = 0; i < n; i++) {
        b[0] = "0123456789ABCDEF"[p[i] >> 4];
        b[1] = "0123456789ABCDEF"[p[i] & 15];
        b[2] = i + 1 < n ? ' ' : 0;
        b[3] = 0;
        put(b);
    }
}
static void path_in_dir(WCHAR *out, const WCHAR *name) {
    int i = 0, j = 0;
    while (g_dir[i] && i < MAX_PATH - 1) out[i] = g_dir[i], i++;
    while (name[j] && i < MAX_PATH - 1) out[i++] = name[j++];
    out[i] = 0;
}
static unsigned ms_since_start(void) {
    FILETIME c, e, k, u, now;
    ULARGE_INTEGER a, b;
    if (!GetProcessTimes(GetCurrentProcess(), &c, &e, &k, &u)) return 0;
    GetSystemTimeAsFileTime(&now);
    a.LowPart = c.dwLowDateTime, a.HighPart = c.dwHighDateTime;
    b.LowPart = now.dwLowDateTime, b.HighPart = now.dwHighDateTime;
    b.QuadPart -= a.QuadPart; /* 100 ns units; startup is far below 429 s, so 32 bits are enough */
    return b.HighPart ? 0xFFFFFFFFu : b.LowPart / 10000; /* 32-bit division: no CRT helper */
}

/* ---- patches ---- */
typedef struct {
    const char *id;
    const WCHAR *key; /* m2033fix.ini [fix] key */
    int def;          /* default when the ini has no value */
    unsigned addr;
    unsigned len;
    unsigned char expect[16];
    unsigned char repl[16];
    int group; /* nonzero: every part with this group is applied, or none of them is */
} Patch;

static const Patch g_patches[] = {
    /* P1: text-language switch at 0x85B090: drop "mov [0xA14F88],0 ; call 0x40C060" so the charmap global is
       replaced in one store at 0x85B0C2 and the old table stays valid for concurrent readers (leaks once). */
    {"P1 lang_switch_race", L"lang_switch_race", 1, 0x0085B0A8, 15,
     {0xC7, 0x05, 0x88, 0x4F, 0xA1, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE8, 0xA9, 0x0F, 0xBB, 0xFF},
     {0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90}, 0},
    /* P2 (exit-time charmap free, never proven) and P3 (save mouse_inertion, convenience) were dropped in 0.2;
       README.md says what they did and why they went. */
    /* P4: 0x7A1F17 lists display modes with IDXGIOutput::GetDisplayModeList(fmt, DXGI_ENUM_MODES_SCALING)
       into a stack buffer of 512 DXGI_MODE_DESC (28 B). Raise it to 1024, byte for byte as the GOG build does:
       frame size for _alloca_probe, the buffer for the call, the capacity, the buffer for the copy loop.
       Nothing else in the function touches the buffer. All four parts or none. */
    {"P4 display_modes_1024 frame", L"display_modes_1024", 1, 0x007A1F1A, 5,
     {0xB8, 0x40, 0x38, 0x00, 0x00}, {0xB8, 0x80, 0x70, 0x00, 0x00}, 4},
    {"P4 display_modes_1024 buf", L"display_modes_1024", 1, 0x007A1F3F, 6,
     {0x8D, 0x95, 0xC0, 0xC7, 0xFF, 0xFF}, {0x8D, 0x95, 0x80, 0x8F, 0xFF, 0xFF}, 4},
    {"P4 display_modes_1024 count", L"display_modes_1024", 1, 0x007A1F4F, 7,
     {0xC7, 0x45, 0xFC, 0x00, 0x02, 0x00, 0x00}, {0xC7, 0x45, 0xFC, 0x00, 0x04, 0x00, 0x00}, 4},
    {"P4 display_modes_1024 copy", L"display_modes_1024", 1, 0x007A1F77, 6,
     {0x8D, 0x8D, 0xC0, 0xC7, 0xFF, 0xFF}, {0x8D, 0x8D, 0x80, 0x8F, 0xFF, 0xFF}, 4},
};

/* every part of the group still holds either its original or its patched bytes */
static int group_ok(int group) {
    unsigned i;
    for (i = 0; i < sizeof g_patches / sizeof g_patches[0]; i++) {
        const Patch *p = &g_patches[i];
        const unsigned char *at = (const unsigned char *)p->addr;
        if (p->group == group && !same(at, p->expect, p->len) && !same(at, p->repl, p->len)) return 0;
    }
    return 1;
}

static int game_is_expected(void) {
    const unsigned char *base = (const unsigned char *)GetModuleHandleW(NULL);
    const IMAGE_DOS_HEADER *dos = (const IMAGE_DOS_HEADER *)base;
    const IMAGE_NT_HEADERS32 *nt;
    put("exe base ");
    put_hex((unsigned)base, 8);
    if ((unsigned)base != GAME_BASE || dos->e_magic != IMAGE_DOS_SIGNATURE) {
        put(" -> unexpected, no patches\r\n");
        return 0;
    }
    nt = (const IMAGE_NT_HEADERS32 *)(base + dos->e_lfanew);
    put(" size ");
    put_hex(nt->OptionalHeader.SizeOfImage, 8);
    put(" stamp ");
    put_hex(nt->FileHeader.TimeDateStamp, 8);
    if (nt->Signature != IMAGE_NT_SIGNATURE || nt->OptionalHeader.SizeOfImage != GAME_SIZE ||
        nt->FileHeader.TimeDateStamp != GAME_STAMP) {
        put(" -> not metro2033.exe 1.0.0.1 (Steam), no patches\r\n");
        return 0;
    }
    put(" -> ok\r\n");
    return 1;
}

/* ---- P5: Present's SyncInterval from r_vsync (README.md). The two per-frame call sites jump to stubs in this
   DLL that push r_vsync ? 1 : 0 instead of the constant 0. (A stub in the exe's .text padding, as in the GOG build,
   also passed the tests; it is not used.) ---- */
#define SITE_A 0x007A1733u /* push ebx; push ebx; push edi; call ecx  (back at 0x7A1738) */
#define SITE_B 0x007A1D71u /* push ebx; push ebp; call [eax+0x20]     (back at 0x7A1D76; Flags pushed at 0x7A1D70) */

/* the stubs return through these, so they stay right if this DLL is rebased */
__attribute__((used)) unsigned g_p5_back_a = SITE_A + 5;
__attribute__((used)) unsigned g_p5_back_b = SITE_B + 5;
void p5_stub_a(void);
void p5_stub_b(void);
__asm__(".text\n"
        ".p2align 4\n"
        ".globl _p5_stub_a\n"
        "_p5_stub_a:\n"
        "    pushl %ebx\n"          /* Flags, as before (0) */
        "    movl 0x9F2820, %eax\n" /* eax is dead here: it held the vtable ecx came from */
        "    shrl $4, %eax\n"
        "    andl $1, %eax\n"
        "    pushl %eax\n" /* SyncInterval = r_vsync ? 1 : 0 */
        "    pushl %edi\n" /* the swap chain */
        "    call *%ecx\n" /* IDXGISwapChain::Present, stdcall: pops 12 bytes, HRESULT in eax */
        "    jmp *_g_p5_back_a\n"
        ".p2align 4\n"
        ".globl _p5_stub_b\n"
        "_p5_stub_b:\n"
        "    movl 0x9F2820, %ecx\n" /* ecx is dead here: eax holds the vtable for the call */
        "    shrl $4, %ecx\n"
        "    andl $1, %ecx\n"
        "    pushl %ecx\n"
        "    pushl %ebp\n"
        "    call *0x20(%eax)\n"
        "    jmp *_g_p5_back_b\n");

/* the code that registers r_vsync must say: name "r_vsync", value word 0x9F2820, mask 0x10. It is plain .text,
   so this holds before the game builds the cvar object (lazily, later than our first call). */
static int p5_cvar_ok(void) {
    static const unsigned char name_reg[] = {0xC7, 0x05, 0xC4, 0x86, 0xA4, 0x00, 0x48, 0x67, 0x97, 0x00};
    static const unsigned char word_reg[] = {0xC7, 0x05, 0xD0, 0x86, 0xA4, 0x00, 0x20, 0x28, 0x9F, 0x00};
    static const unsigned char mask_reg[] = {0xC7, 0x05, 0xD4, 0x86, 0xA4, 0x00, 0x10, 0x00, 0x00, 0x00};
    static const char name[] = "r_vsync";
    return same((const unsigned char *)0x0093A778, name_reg, sizeof name_reg) &&
           same((const unsigned char *)0x0093A7A9, word_reg, sizeof word_reg) &&
           same((const unsigned char *)0x0093A7B3, mask_reg, sizeof mask_reg) &&
           same((const unsigned char *)0x00976748, (const unsigned char *)name, sizeof name);
}

static int unprotect(unsigned addr, unsigned len, DWORD *old) {
    return VirtualProtect((void *)addr, len, PAGE_EXECUTE_READWRITE, old);
}
static void reprotect(unsigned addr, unsigned len, DWORD old) {
    VirtualProtect((void *)addr, len, old, &old);
    FlushInstructionCache(GetCurrentProcess(), (void *)addr, len);
}

/* 5-byte site -> "jmp to": the site sits inside one aligned qword, which is swapped with one cmpxchg8b, so a
   thread can never see half an instruction (none runs this code yet anyway: Present starts ~2 s later). */
static int put_jmp(unsigned site, unsigned to) {
    unsigned q = site & ~7u, k = site - q, rel = to - (site + 5), i;
    union { LONGLONG v; unsigned char b[8]; } was, now;
    DWORD old;
    if (k > 3) return 0;
    was.v = *(volatile LONGLONG *)q;
    now = was;
    now.b[k] = 0xE9;
    for (i = 0; i < 4; i++) now.b[k + 1 + i] = (unsigned char)(rel >> (8 * i));
    if (!unprotect(q, 8, &old)) return 0;
    i = InterlockedCompareExchange64((volatile LONGLONG *)q, now.v, was.v) == was.v;
    reprotect(q, 8, old);
    return (int)i;
}

static void apply_p5(const WCHAR *ini) {
    static const unsigned char site_a[] = {0x8B, 0x48, 0x20, 0x53, 0x53, 0x57, 0xFF, 0xD1}; /* qword 0x7A1730 */
    static const unsigned char site_b[] = {0x53, 0x53, 0x55, 0xFF, 0x50, 0x20, 0x5F, 0x5E}; /* qword 0x7A1D70 */
    unsigned to_a = (unsigned)&p5_stub_a, to_b = (unsigned)&p5_stub_b;
    put("P5 vsync_follow_cvar");
    if (!GetPrivateProfileIntW(L"fix", L"vsync_follow_cvar", 1, ini)) {
        put(": disabled in ini\r\n");
        return;
    }
    if (!p5_cvar_ok()) {
        put(": SKIP, r_vsync registration differs\r\n");
        return;
    }
    if (!same((const unsigned char *)(SITE_A - 3), site_a, 8) || !same((const unsigned char *)(SITE_B - 1), site_b, 8)) {
        put(": SKIP, bytes differ: A ");
        put_bytes((const unsigned char *)(SITE_A - 3), 8);
        put(" B ");
        put_bytes((const unsigned char *)(SITE_B - 1), 8);
        put("\r\n");
        return;
    }
    put("\r\n    A @");
    put_hex(SITE_A, 8);
    put(" -> ");
    put_hex(to_a, 8);
    put(put_jmp(SITE_A, to_a) ? ": OK " : ": FAILED ");
    put_bytes((const unsigned char *)(SITE_A - 3), 8);
    put("\r\n    B @");
    put_hex(SITE_B, 8);
    put(" -> ");
    put_hex(to_b, 8);
    put(put_jmp(SITE_B, to_b) ? ": OK " : ": FAILED ");
    put_bytes((const unsigned char *)(SITE_B - 1), 8);
    put("\r\n");
}

static void apply_patch(const Patch *p, const WCHAR *ini) {
    unsigned char *at = (unsigned char *)p->addr;
    DWORD old;
    int on = (int)GetPrivateProfileIntW(L"fix", p->key, p->def, ini);
    put(p->id);
    put(" @");
    put_hex(p->addr, 8);
    if (!on) {
        put(": disabled in ini\r\n");
        return;
    }
    if (same(at, p->repl, p->len)) {
        put(": already applied\r\n");
        return;
    }
    if (p->group && !group_ok(p->group)) {
        put(": SKIP, another part of this group differs\r\n");
        return;
    }
    if (!same(at, p->expect, p->len)) {
        put(": SKIP, bytes differ: found ");
        put_bytes(at, p->len);
        put("\r\n");
        return;
    }
    if (!unprotect(p->addr, p->len, &old)) {
        put(": SKIP, VirtualProtect failed ");
        put_hex(GetLastError(), 8);
        put("\r\n");
        return;
    }
    memcpy(at, p->repl, p->len);
    reprotect(p->addr, p->len, old);
    put(": OK ");
    put_bytes(p->expect, p->len);
    put(" -> ");
    put_bytes(at, p->len);
    put("\r\n");
}

static void init_once(void) {
    WCHAR ini[MAX_PATH], log[MAX_PATH], sys[MAX_PATH];
    unsigned i, n;
    path_in_dir(ini, L"m2033fix.ini");
    path_in_dir(log, L"m2033fix.log");
    if (GetPrivateProfileIntW(L"log", L"enabled", 1, ini))
        g_log = CreateFileW(log, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    put("m2033fix 0.2-pre (P4, P5)  first DirectInput8Create: tid ");
    put_dec(GetCurrentThreadId());
    put(", ");
    put_dec(ms_since_start());
    put(" ms after process start\r\n");

    n = GetSystemDirectoryW(sys, MAX_PATH - 16);
    if (n && n < MAX_PATH - 16) {
        static const WCHAR tail[] = L"\\dinput8.dll";
        for (i = 0; tail[i]; i++) sys[n + i] = tail[i];
        sys[n + i] = 0;
        g_real = (DI8Create)GetProcAddress(LoadLibraryW(sys), "DirectInput8Create");
    }
    put(g_real ? "system dinput8: ok\r\n" : "system dinput8: FAILED, input will not work\r\n");

    if (game_is_expected()) {
        for (i = 0; i < sizeof g_patches / sizeof g_patches[0]; i++) apply_patch(&g_patches[i], ini);
        apply_p5(ini);
    }

    if (g_log != INVALID_HANDLE_VALUE) {
        CloseHandle(g_log);
        g_log = INVALID_HANDLE_VALUE;
    }
}

/* exported (undecorated) through dinput8.def */
HRESULT WINAPI DirectInput8Create(HINSTANCE hinst, DWORD ver, REFIID riid, LPVOID *out, LPUNKNOWN outer) {
    if (InterlockedCompareExchange(&g_once, 1, 0) == 0) {
        init_once();
        g_once = 2;
    } else {
        while (g_once != 2) Sleep(0); /* another thread is initialising; wait for g_real */
    }
    if (!g_real) return E_FAIL;
    return g_real(hinst, ver, riid, out, outer);
}

BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID reserved) {
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        /* nothing else here: loader lock is held and the game's .text is still encrypted */
        int i;
        g_self = h;
        DisableThreadLibraryCalls(h);
        i = (int)GetModuleFileNameW(h, g_dir, MAX_PATH);
        while (i > 0 && g_dir[i - 1] != L'\\') i--;
        g_dir[i] = 0;
    }
    return TRUE;
}
