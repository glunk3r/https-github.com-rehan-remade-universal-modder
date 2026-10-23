# Build m2033fix (a dinput8.dll proxy) with zig: 32-bit, kernel32 only, no CRT.
# usage: powershell -ExecutionPolicy Bypass -File build.ps1      -> build\dinput8.dll
param([string]$Out = "$PSScriptRoot\build")
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force $Out | Out-Null
Push-Location $Out
try {
    # compile with the Windows headers, then link without the CRT (-nostdlib also drops the headers)
    zig cc -target x86-windows-gnu -O2 -Wall -c -o m2033fix.o "$PSScriptRoot\src\m2033fix.c"
    if ($LASTEXITCODE) { throw 'compile failed' }
    zig cc -target x86-windows-gnu -O2 -shared -nostdlib '-Wl,--entry=DllMain@12' -o dinput8.dll m2033fix.o "$PSScriptRoot\src\dinput8.def" -lkernel32
    if ($LASTEXITCODE) { throw 'link failed' }
    Get-Item dinput8.dll | Select-Object FullName, Length
} finally { Pop-Location }
