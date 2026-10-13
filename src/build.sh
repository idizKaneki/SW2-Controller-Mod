#!/bin/sh
# Builds SW2Controller.asi (32-bit Windows DLL) with LLVM (clang + lld), from Linux or Windows.
# No C runtime and no Windows SDK needed: kernel32 imports come from k32.def.
set -e
cd "$(dirname "$0")"
llvm-dlltool -m i386 -d k32.def -l k32.lib -k
clang --target=i686-pc-windows-msvc -O2 -ffreestanding -fno-builtin -c sw2controller.c -o sw2controller.obj
lld-link /dll /entry:DllMain@12 /nodefaultlib /subsystem:windows /out:SW2Controller.asi sw2controller.obj k32.lib
echo "OK: SW2Controller.asi"
