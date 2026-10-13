@echo off
rem Builds SW2Controller.asi with LLVM for Windows (https://github.com/llvm/llvm-project/releases), clang/lld-link in PATH.
cd /d "%~dp0"
llvm-dlltool -m i386 -d k32.def -l k32.lib -k || goto :err
clang --target=i686-pc-windows-msvc -O2 -ffreestanding -fno-builtin -c sw2controller.c -o sw2controller.obj || goto :err
lld-link /dll /entry:DllMain@12 /nodefaultlib /subsystem:windows /out:SW2Controller.asi sw2controller.obj k32.lib || goto :err
echo OK: SW2Controller.asi
exit /b 0
:err
echo Build failed.
exit /b 1
