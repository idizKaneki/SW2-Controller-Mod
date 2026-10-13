@echo off
chcp 65001 >nul
setlocal EnableExtensions
title Samurai Warriors 2 - Controller mod : uninstall

set "MOD=%~dp0"
set "MOD=%MOD:~0,-1%"
for %%i in ("%MOD%\..") do set "JEU=%%~fi"
rem archive extracted with an extra folder level (Windows "Extract all"): look one level higher
if not exist "%JEU%\sw2.exe" for %%i in ("%MOD%\..\..") do if exist "%%~fi\sw2.exe" set "JEU=%%~fi"
set "PY=%MOD%\tools\python\python.exe"
set "PYTHONIOENCODING=utf-8"

echo.
echo  ============================================================
echo    Samurai Warriors 2 (PC) - Controller mod : uninstall
echo    Mod manette : désinstallation
echo  ============================================================
echo.
if not exist "%JEU%\sw2.exe" goto :err_dossier
if not exist "%PY%" goto :err_fichiers
echo  Close the game before going on. / Fermez le jeu avant de continuer.
pause
echo.
echo  [1/3] Keyboard icons / Icônes clavier
"%PY%" "%MOD%\tools\sw2_icons.py" keyboard "%JEU%"
echo.
echo  [2/3] Original button layout / Disposition d'origine
"%PY%" "%MOD%\tools\sw2_controller.py" restore
echo.
echo  [3/3] Game module / Module du jeu
del /q "%JEU%\SW2Controller.asi" "%JEU%\SW2Controller.ini" "%JEU%\SW2Controller.log" >nul 2>&1
if exist "%MOD%\tools\dinput8_installed.txt" (
  if not exist "%JEU%\*.asi" del /q "%JEU%\dinput8.dll" >nul 2>&1
  del /q "%MOD%\tools\dinput8_installed.txt" >nul 2>&1
)
del /q "%MOD%\tools\installed.txt" >nul 2>&1
echo.
echo  Controller mod removed. / Mod manette retiré.
goto :fin

:err_dossier
echo  [ERROR / ERREUR] sw2.exe not found in / introuvable dans : %JEU%
goto :fin

:err_fichiers
echo  [ERROR / ERREUR] Mod files are missing / Des fichiers du mod sont manquants.
goto :fin

:fin
echo.
pause
endlocal
