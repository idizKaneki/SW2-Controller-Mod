# -*- coding: utf-8 -*-
"""
Fabrique le paquet Nexus "Samurai Warriors 2 - Controller mod".

Le paquet ne contient AUCUN fichier du jeu : module, scripts, patchs d'icones,
installeur, le chargeur ASI (dinput8.dll, Ultimate ASI Loader, licence MIT)
et un Python portable officiel (embeddable).

A placer dans un meme dossier :
  creer_mod_controller.py, INSTALL.bat, UNINSTALL.bat, readme.txt,
  files\\SW2Controller.asi, files\\SW2Controller.ini,
  tools\\sw2_controller.py, tools\\sw2_icons.py,
  tools\\icons_xbox.patch, tools\\icons_playstation.patch

Usage :
  python creer_mod_controller.py PYTHON_EMBED.zip CHEMIN\\dinput8.dll --version 1.0
"""
import argparse
import sys
import zipfile
from pathlib import Path

ICI = Path(__file__).resolve().parent
NOM = "SW2_Controller"
FICHIERS = ["INSTALL.bat", "UNINSTALL.bat", "readme.txt",
            "files/SW2Controller.asi", "files/SW2Controller.ini",
            "tools/sw2_controller.py", "tools/sw2_icons.py",
            "tools/icons_xbox.patch", "tools/icons_playstation.patch"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("python_zip", help="python-3.x.y-embed-amd64.zip (python.org)")
    ap.add_argument("dinput8", help="dinput8.dll (Ultimate ASI Loader, x86, celui du mod 16:9)")
    ap.add_argument("--version", default="1.0")
    a = ap.parse_args()

    pz, dll = Path(a.python_zip), Path(a.dinput8)
    for p in (pz, dll):
        if not p.exists():
            sys.exit("[ERREUR] Introuvable : %s" % p)
    for f in FICHIERS:
        if not (ICI / f).exists():
            sys.exit("[ERREUR] Fichier manquant : %s" % f)
    with zipfile.ZipFile(pz) as z:
        noms = z.namelist()
        if "python.exe" not in noms or not any(n.endswith("._pth") for n in noms):
            sys.exit("[ERREUR] Ce zip n'est pas un Python 'embeddable' Windows.")
        contenu_py = {n: z.read(n) for n in noms if not n.endswith("/")}
    d = dll.read_bytes()
    if d[:2] != b"MZ":
        sys.exit("[ERREUR] dinput8.dll invalide.")

    archive = ICI / ("%s_v%s.zip" % (NOM, a.version))
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in FICHIERS:
            z.write(ICI / f, "%s/%s" % (NOM, f))
        z.writestr("%s/files/dinput8.dll" % NOM, d)
        for n, data in contenu_py.items():
            z.writestr("%s/tools/python/%s" % (NOM, n), data)
    print("Termine : %s (%.1f Mo)" % (archive.name, archive.stat().st_size / 1048576))
    print("Contenu : module, scripts, patchs d'icones, chargeur ASI, Python portable ; aucun fichier du jeu.")


if __name__ == "__main__":
    main()
