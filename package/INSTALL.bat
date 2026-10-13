@echo off
chcp 65001 >nul
setlocal EnableExtensions
title Samurai Warriors 2 - Controller mod : install

set "MOD=%~dp0"
set "MOD=%MOD:~0,-1%"
for %%i in ("%MOD%\..") do set "JEU=%%~fi"
rem archive extracted with an extra folder level (Windows "Extract all"): look one level higher
if not exist "%JEU%\sw2.exe" for %%i in ("%MOD%\..\..") do if exist "%%~fi\sw2.exe" set "JEU=%%~fi"
set "PY=%MOD%\tools\python\python.exe"
set "PYTHONIOENCODING=utf-8"

echo.
echo  ============================================================
echo    Samurai Warriors 2 (PC) - Controller mod / Mod manette
echo  ============================================================
echo.

if not exist "%JEU%\sw2.exe" goto :err_dossier
if not exist "%PY%" goto :err_fichiers
if not exist "%MOD%\tools\sw2_controller.py" goto :err_fichiers
if not exist "%MOD%\files\SW2Controller.asi" goto :err_fichiers
(echo test> "%JEU%\_sw2ctrl_test.tmp") 2>nul || goto :err_droits
del "%JEU%\_sw2ctrl_test.tmp" >nul 2>&1

echo  Game folder / Dossier du jeu : %JEU%
echo  Close the game before going on. / Fermez le jeu avant de continuer.
echo.
echo  Which controller do you play with? / Avec quelle manette jouez-vous ?
echo.
echo    1 = Xbox controller (or any controller seen as an Xbox one)
echo        Manette Xbox (ou toute manette vue comme une manette Xbox)
echo.
echo    2 = PlayStation controller, game launched through Steam (Steam Input)
echo        Manette PlayStation, jeu lancé via Steam (Steam Input)
echo.
echo    3 = PlayStation controller connected directly (no Steam Input)
echo        Manette PlayStation branchée directement (sans Steam Input)
echo.
echo  Not sure with a PlayStation controller? Try 2. If the buttons are wrong
echo  in game, run INSTALL.bat again and choose 3.
echo  Pas sûr avec une manette PlayStation ? Essayez 2. Si les boutons sont faux
echo  en jeu, relancez INSTALL.bat et choisissez 3.
echo.
choice /c 123 /n /m " Your choice / Votre choix (1, 2, 3) : "
if errorlevel 3 (set "LAYOUT=playstation" & set "ICONS=playstation" & goto :go)
if errorlevel 2 (set "LAYOUT=xbox" & set "ICONS=playstation" & goto :go)
set "LAYOUT=xbox" & set "ICONS=xbox"

:go
echo.
echo  [1/3] Game module / Module du jeu
if not exist "%JEU%\dinput8.dll" (
  copy /y "%MOD%\files\dinput8.dll" "%JEU%\dinput8.dll" >nul || goto :echec
  echo dinput8.dll installed by SW2_Controller> "%MOD%\tools\dinput8_installed.txt"
  echo    dinput8.dll ^(Ultimate ASI Loader^) installed / installé
)
copy /y "%MOD%\files\SW2Controller.asi" "%JEU%\SW2Controller.asi" >nul || goto :echec
if not exist "%JEU%\SW2Controller.ini" copy /y "%MOD%\files\SW2Controller.ini" "%JEU%\SW2Controller.ini" >nul
echo    SW2Controller.asi + SW2Controller.ini OK
echo.
echo  [2/3] Button layout / Disposition des boutons (%LAYOUT%)
"%PY%" "%MOD%\tools\sw2_controller.py" %LAYOUT%
if errorlevel 1 goto :echec
echo.
echo  [3/3] Button icons / Icônes des boutons (%ICONS%) - this takes a moment / un instant...
"%PY%" "%MOD%\tools\sw2_icons.py" %ICONS% "%JEU%"
if errorlevel 1 goto :echec
echo %LAYOUT% %ICONS%> "%MOD%\tools\installed.txt"
echo.
echo  Install complete. Enjoy! / Installation terminée. Bon jeu !
echo  If you update or reinstall a text mod (e.g. French translation), run this
echo  INSTALL.bat again afterwards to put the button icons back.
echo  Si vous mettez à jour ou réinstallez un mod de texte (ex. traduction FR),
echo  relancez ensuite INSTALL.bat pour remettre les icônes.
goto :fin

:echec
echo.
echo  Install did not complete, see the message above and readme.txt.
echo  L'installation n'a pas abouti, voir le message ci-dessus et readme.txt.
goto :fin

:err_dossier
echo  [ERROR / ERREUR] sw2.exe not found in / introuvable dans :
echo    %JEU%
echo  The SW2_Controller folder must be inside the game folder, next to sw2.exe.
echo  Le dossier SW2_Controller doit être dans le dossier du jeu, à côté de sw2.exe.
goto :fin

:err_fichiers
echo  [ERROR / ERREUR] Mod files are missing, extract the whole archive again.
echo  Des fichiers du mod sont manquants, ré-extrayez l'archive complète.
goto :fin

:err_droits
echo  [ERROR / ERREUR] Cannot write to the game folder.
echo  Right-click INSTALL.bat, then "Run as administrator".
echo  Impossible d'écrire dans le dossier du jeu.
echo  Clic droit sur INSTALL.bat, puis "Exécuter en tant qu'administrateur".
goto :fin

:fin
echo.
pause
endlocal
