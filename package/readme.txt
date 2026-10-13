SAMURAI WARRIORS 2 (PC) - CONTROLLER MOD
========================================
Version 1.0 - (Français plus bas)

Play Samurai Warriors 2 with an Xbox or PlayStation controller, the way the
console versions play in the West:
- western console button layout (no Steam Input setup needed);
- right stick controls the camera (the PC port could not read it);
- in menus, A / Cross confirms and B / Circle goes back;
- the keyboard keys shown in the menus (Enter, Esc, Tab, arrows...) are
  replaced by Xbox or PlayStation buttons;
- the "Use the gamepad's auto-setting?" question is gone from the button
  settings screen (answering Yes by mistake erased your layout).

Controller 1 and controller 2 get the same layout.


BUTTON LAYOUT
-------------
                    Xbox        PlayStation
Normal attack       X           Square
Charge attack       Y           Triangle
Jump                A           Cross
Musou               B           Circle
Guard               LB          L1
Special skill       RB          R1
Dodge               RT          R2
Map                 View        Share / Create
Pause               Menu        Options
Move                left stick
Camera              right stick


REQUIREMENTS
------------
- Samurai Warriors 2, English PC version (US/EU).
- An Xbox controller, a PlayStation controller, or any controller seen as
  an Xbox controller (e.g. through Steam Input).
- Nothing else: Python and the ASI loader are bundled with the mod.


INSTALL
-------
1. Close the game.
2. Extract the archive into the game folder. You should get a folder named
   SW2_Controller next to sw2.exe.
3. Run SW2_Controller\INSTALL.bat and choose your controller:
     1 = Xbox controller (or any controller seen as an Xbox one)
     2 = PlayStation controller, game launched through Steam (Steam Input)
     3 = PlayStation controller connected directly (no Steam Input)
   With a PlayStation controller, if you are not sure, try 2. If the
   buttons are wrong in game, run INSTALL.bat again and choose 3.
If the game is in "Program Files": right-click INSTALL.bat,
"Run as administrator".

To change controller later, just run INSTALL.bat again.


UNINSTALL
---------
Close the game and run SW2_Controller\UNINSTALL.bat: keyboard icons,
original button layout and game module are put back.


WHAT IS CHANGED
---------------
- SW2Controller.asi + SW2Controller.ini in the game folder (with the
  dinput8.dll ASI loader if it is not there yet). The module patches the
  game in memory at launch; sw2.exe is not modified.
- The game's own controller settings: Documents\KOEI\SAMURAI WARRIORS 2\
  inputmap1.dat and inputmap2.dat. The originals are kept next to them as
  inputmap1_original.dat / inputmap2_original.dat.
- The button icon sheet inside linkdata\LINKDATA_BNS_NA.lnk (same size,
  patched in place; each change is checked first).


COMPATIBILITY
-------------
- Widescreen Fix: works together (both use the same dinput8.dll loader).
- French translation / Japanese voices: works together. If you update or
  reinstall a mod that rewrites linkdata\LINKDATA_BNS_NA.lnk, run this
  INSTALL.bat again afterwards to put the button icons back.


GOOD TO KNOW
------------
- You can still change single buttons in Options > Settings > Controller >
  Button settings.
- SW2Controller.log (game folder) shows what the module applied.
- Each part can be turned off in SW2Controller.ini (1 = on, 0 = off).
- The keyboard still works; its icons are now controller buttons.
- In Sugoroku, the game has no pause (original game behaviour).


CREDITS
-------
Mod and tools: idiz117.
Ultimate ASI Loader (dinput8.dll): ThirteenAG (MIT license).
Python: Python Software Foundation (PSF license).
Button icons: Xbox buttons from the game's own unused Xbox 360 sprites;
other icons drawn for this mod.
Samurai Warriors 2 (c) Koei Tecmo / Omega Force. Unofficial fan project.
Xbox and PlayStation are trademarks of their respective owners.


========================================
FRANÇAIS - MOD MANETTE
========================================

Jouez à Samurai Warriors 2 avec une manette Xbox ou PlayStation, comme sur
les versions console occidentales :
- disposition des boutons des consoles occidentales (sans réglage Steam
  Input) ;
- le stick droit contrôle la caméra (le portage PC ne savait pas le lire) ;
- dans les menus, A / Croix valide et B / Rond revient en arrière ;
- les touches clavier affichées dans les menus (Entrée, Échap, Tab,
  flèches...) sont remplacées par les boutons Xbox ou PlayStation ;
- la question « Utiliser le réglage automatique de la manette ? » disparaît
  de l'écran de configuration des touches (un Oui par erreur effaçait votre
  disposition).

La manette 1 et la manette 2 reçoivent la même disposition.


DISPOSITION DES BOUTONS
-----------------------
                    Xbox        PlayStation
Attaque normale     X           Carré
Attaque chargée     Y           Triangle
Saut                A           Croix
Musou               B           Rond
Garde               LB          L1
Posture spéciale    RB          R1
Esquive             RT          R2
Carte               View        Share / Create
Pause               Menu        Options
Déplacement         stick gauche
Caméra              stick droit


CE QU'IL FAUT
-------------
- Samurai Warriors 2, version PC anglaise (US/EU).
- Une manette Xbox, une manette PlayStation, ou toute manette vue comme une
  manette Xbox (par exemple via Steam Input).
- Rien d'autre : Python et le chargeur ASI sont inclus dans le mod.


INSTALLATION
------------
1. Fermez le jeu.
2. Extrayez l'archive dans le dossier du jeu. Vous devez obtenir un dossier
   SW2_Controller à côté de sw2.exe.
3. Lancez SW2_Controller\INSTALL.bat et choisissez votre manette :
     1 = manette Xbox (ou toute manette vue comme une manette Xbox)
     2 = manette PlayStation, jeu lancé via Steam (Steam Input)
     3 = manette PlayStation branchée directement (sans Steam Input)
   Avec une manette PlayStation, en cas de doute, essayez 2. Si les boutons
   sont faux en jeu, relancez INSTALL.bat et choisissez 3.
Si le jeu est dans « Program Files » : clic droit sur INSTALL.bat,
« Exécuter en tant qu'administrateur ».

Pour changer de manette plus tard, relancez simplement INSTALL.bat.


DÉSINSTALLATION
---------------
Fermez le jeu et lancez SW2_Controller\UNINSTALL.bat : icônes clavier,
disposition d'origine et module du jeu sont remis en place.


CE QUI EST MODIFIÉ
------------------
- SW2Controller.asi + SW2Controller.ini dans le dossier du jeu (avec le
  chargeur ASI dinput8.dll s'il n'y est pas déjà). Le module corrige le jeu
  en mémoire au lancement ; sw2.exe n'est pas modifié.
- Les réglages manette du jeu : Documents\KOEI\SAMURAI WARRIORS 2\
  inputmap1.dat et inputmap2.dat. Les originaux sont gardés à côté
  (inputmap1_original.dat / inputmap2_original.dat).
- La planche d'icônes des boutons dans linkdata\LINKDATA_BNS_NA.lnk (même
  taille, modifiée sur place ; chaque changement est vérifié avant).


COMPATIBILITÉ
-------------
- Correctif écran large : fonctionne ensemble (même chargeur dinput8.dll).
- Traduction française / VO japonaise : fonctionnent ensemble. Si vous
  mettez à jour ou réinstallez un mod qui réécrit
  linkdata\LINKDATA_BNS_NA.lnk, relancez ensuite ce INSTALL.bat pour
  remettre les icônes.


BON À SAVOIR
------------
- Vous pouvez toujours changer un bouton dans Options > Paramètres >
  Manette > Config. touches.
- SW2Controller.log (dossier du jeu) indique ce que le module a appliqué.
- Chaque partie peut être désactivée dans SW2Controller.ini (1 = actif,
  0 = désactivé).
- Le clavier fonctionne toujours ; ses icônes sont désormais celles de la
  manette.
- En Sugoroku, le jeu n'a pas de pause (comportement d'origine).


CRÉDITS
-------
Mod et outils : idiz117.
Ultimate ASI Loader (dinput8.dll) : ThirteenAG (licence MIT).
Python : Python Software Foundation (licence PSF).
Icônes : boutons Xbox tirés des sprites Xbox 360 inutilisés du jeu ;
autres icônes dessinées pour ce mod.
Samurai Warriors 2 (c) Koei Tecmo / Omega Force. Projet de fans non officiel.
Xbox et PlayStation sont des marques de leurs propriétaires respectifs.
