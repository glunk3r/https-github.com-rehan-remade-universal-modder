/* m2033fix: dinput8.dll proxy for the original Metro 2033 (2010, Steam 43110, metro2033.exe 1.0.0.1).
 *
 * The exe on disk is never touched. On the game's first DirectInput8Create call (after SteamStub has
 * decrypted .text) the proxy checks the exe identity and the exact bytes at each site, applies the enabled
 * in-memory patches, then forwards to the system dinput8.dll. Any mismatch skips that patch (vanilla).
 * Mechanism, patch list, verification and rollback: README.md.
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
    int code; /* 1 = .text (needs VirtualProtect), 0 = .data */
} Patch;

static const Patch g_patches[] = {
    /* P1: text-language switch at 0x85B090: drop "mov [0xA14F88],0 ; call 0x40C060" so the charmap global is
       replaced in one store at 0x85B0C2 and the old table stays valid for concurrent readers (leaks once). */
    {"P1 lang_switch_race", L"lang_switch_race", 1, 0x0085B0A8, 15,
     {0xC7, 0x05, 0x88, 0x4F, 0xA1, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE8, 0xA9, 0x0F, 0xBB, 0xFF},
     {0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90}, 1},
    /* P2: shutdown free of the charmap at 0x84F6C0 (unproven, off by default). */
    {"P2 exit_charmap_free", L"exit_charmap_free", 0, 0x0084F6CB, 15,
     {0xC7, 0x05, 0x88, 0x4F, 0xA1, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE8, 0x86, 0xC9, 0xBB, 0xFF},
     {0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90}, 1},
    /* P3: cvar object mouse_inertion @0x9F3710, flags 0x00000101 -> 0x01000101 (saved to user.cfg). */
    {"P3 save_mouse_inertion", L"save_mouse_inertion", 1, 0x009F371B, 1, {0x00}, {0x01}, 0},
};

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

static int p3_object_ok(void) {
    /* the cvar object must still be {vtable 0x9640A8 (float cvar), name -> "mouse_inertion"} */
    const unsigned *obj = (const unsigned *)0x009F3710;
    static const char name[] = "mouse_inertion";
    return obj[0] == 0x009640A8 && same((const unsigned char *)obj[1], (const unsigned char *)name, sizeof name);
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
    if (!same(at, p->expect, p->len) || (p->addr == 0x009F371B && !p3_object_ok())) {
        put(": SKIP, bytes differ: found ");
        put_bytes(at, p->len);
        put("\r\n");
        return;
    }
    if (p->code && !VirtualProtect(at, p->len, PAGE_EXECUTE_READWRITE, &old)) {
        put(": SKIP, VirtualProtect failed ");
        put_hex(GetLastError(), 8);
        put("\r\n");
        return;
    }
    memcpy(at, p->repl, p->len);
    if (p->code) {
        VirtualProtect(at, p->len, old, &old);
        FlushInstructionCache(GetCurrentProcess(), at, p->len);
    }
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
    put("m2033fix 0.1  first DirectInput8Create: tid ");
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

    if (game_is_expected())
        for (i = 0; i < sizeof g_patches / sizeof g_patches[0]; i++) apply_patch(&g_patches[i], ini);

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
