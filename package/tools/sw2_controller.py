# -*- coding: utf-8 -*-
"""sw2_controller.py - Samurai Warriors 2 (PC): Xbox controller layout, western console style.

Writes the game's own controller config:
    Documents\\KOEI\\SAMURAI WARRIORS 2\\inputmap1.dat  (player 1, J1)
    Documents\\KOEI\\SAMURAI WARRIORS 2\\inputmap2.dat  (player 2, J2)
The first time, the originals are kept as inputmap1_original.dat / inputmap2_original.dat.
Keyboard keys are not changed.

Usage (game closed):
    python sw2_controller.py xbox         -> Xbox controller (or any XInput pad, or a PS pad through Steam Input)
    python sw2_controller.py playstation  -> PlayStation controller (DualShock 4 / DualSense) seen directly by the game
    python sw2_controller.py show       -> show the current config
    python sw2_controller.py restore    -> put the original config back

inputmap*.dat format (900 bytes, 32-bit words): 5-word header, then one 11-word entry per action:
    [action id, ?, ?, 8 (keyboard), ?, ?, key, device, type (0 button / 1 axis), sign (1 = -, 0 = +), number]
    device: 0 = J1, 1 = J2, 0x0A = none; number starts at 0 (B1 = 0, Axis 1 = 0).
"""
import os, sys, struct, shutil

# entry index in the file -> action name (as in the game's key config screen)
ACTIONS = {1: "Forward", 2: "Back", 3: "Left", 4: "Right", 5: "Pause", 7: "Jump",
           8: "Musou attack", 9: "Normal attack", 10: "Charge attack", 11: "Guard",
           12: "Special skill", 13: "Map", 14: "Dodge", 17: "Camera up", 18: "Camera down",
           19: "Camera left", 20: "Camera right"}

# Xbox controller buttons as seen by the game (B1 = 0)
A, B, X, Y, LB, RB, VIEW, MENU, LS, RS, SHARE = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11
BTN, AXIS = 0, 1
PLUS, MINUS = 0, 1

# entry -> (type, sign, number) ; same "western console" layout on both pads:
# bottom face button = Jump (and OK in menus), right = Musou (and Back), left = Normal attack, top = Charge.
XBOX = {
    1: (AXIS, MINUS, 1), 2: (AXIS, PLUS, 1),        # left stick up / down
    3: (AXIS, MINUS, 0), 4: (AXIS, PLUS, 0),        # left stick left / right
    9:  (BTN, PLUS, X),      # normal attack
    10: (BTN, PLUS, Y),      # charge attack
    8:  (BTN, PLUS, B),      # musou
    7:  (BTN, PLUS, A),      # jump
    11: (BTN, PLUS, LB),     # guard
    12: (BTN, PLUS, RB),     # special skill
    13: (BTN, PLUS, VIEW),   # map
    5:  (BTN, PLUS, MENU),   # pause
    14: (AXIS, MINUS, 2),    # dodge: RT (both triggers share Axis 3, RT = minus side)
    17: (AXIS, MINUS, 4), 18: (AXIS, PLUS, 4),      # camera up / down: right stick vertical (Axis 5)
    19: (AXIS, MINUS, 5), 20: (AXIS, PLUS, 5),      # camera left / right: right stick horizontal (Axis 6)
    # Axis 6 is only read by the game with SW2Controller.asi (RightStick=1)
}

# PlayStation pads (DirectInput order of DualShock 4 / DualSense):
# Square B1, Cross B2, Circle B3, Triangle B4, L1 B5, R1 B6, L2 B7, R2 B8, Share/Create B9, Options B10, L3 B11, R3 B12
# axes as read by the game: Axis 1/2 left stick, Axis 3 right stick X (Z), Axis 4 right stick Y (Rz)
SQUARE, CROSS, CIRCLE, TRIANGLE, L1, R1, L2, R2, SHARE_PS, OPTIONS = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
PLAYSTATION = {
    1: (AXIS, MINUS, 1), 2: (AXIS, PLUS, 1),
    3: (AXIS, MINUS, 0), 4: (AXIS, PLUS, 0),
    9:  (BTN, PLUS, SQUARE),     # normal attack
    10: (BTN, PLUS, TRIANGLE),   # charge attack
    8:  (BTN, PLUS, CIRCLE),     # musou
    7:  (BTN, PLUS, CROSS),      # jump
    11: (BTN, PLUS, L1),         # guard
    12: (BTN, PLUS, R1),         # special skill
    13: (BTN, PLUS, SHARE_PS),   # map
    5:  (BTN, PLUS, OPTIONS),    # pause
    14: (BTN, PLUS, R2),         # dodge
    17: (AXIS, MINUS, 3), 18: (AXIS, PLUS, 3),      # camera up / down: right stick vertical (Axis 4)
    19: (AXIS, MINUS, 2), 20: (AXIS, PLUS, 2),      # camera left / right: right stick horizontal (Axis 3)
}
LAYOUTS = {'xbox': XBOX, 'playstation': PLAYSTATION}

NWORDS = 225  # 900 bytes

# Default config written by the game (keyboard keys + its own gamepad auto-setting), used when the
# player never opened the controller settings (no inputmap file yet).
TEMPLATE = {1: """AQAAAAAAAAAUAAAAAAAAAAoAAAAAAAAAAWp4dwAAAAAIAAAAAADOnwAAAAARAAAAAAAAAAEAdQABAAAAAQAAAAEAAAABanh3AAAAAAgAAAAAAM6fAAAAAB8AAAAAAAAAAQB1AAAAAAABAAAAAgAAAAFqeHcAAAAACAAAAAAAzp8AAAAAHgAAAAAAAAABAHUAAQAAAAAAAAADAAAAAWp4dwAAAAAIAAAAAADOnwAAAAAgAAAAAAAAAAEAdQAAAAAAAAAAAAQAAAABanh3AAAAAAgAAAAAAM6fAAAAAAEAAAAAAAAAAAB1AAAAAAALAAAABQAAAAEAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAoAAAAAAAAAAAAAAAAAAAAGAAAAAWp4dwAAAAAIAAAAAADOnwAAAAAyAAAAAAAAAAAAdQAAAAAAAgAAAAcAAAABanh3AAAAAAgAAAAAAM6fAAAAACYAAAAAAAAAAAB1AAAAAAADAAAACAAAAAFqeHcAAAAACAAAAAAAzp8AAAAAJAAAAAAAAAAAAHUAAAAAAAAAAAAJAAAAAWp4dwAAAAAIAAAAAADOnwAAAAAXAAAAAAAAAAAAdQAAAAAAAQAAAAoAAAABanh3AAAAAAgAAAAAAM6fAAAAACoAAAAAAAAAAAB1AAAAAAAEAAAACwAAAAFqeHcAAAAACAAAAAAAzp8AAAAAGAAAAAAAAAAAAHUAAAAAAAUAAAAMAAAAAWp4dwAAAAAIAAAAAADOnwAAAAAzAAAAAAAAAAAAdQAAAAAABgAAAA0AAAABanh3AAAAAAgAAAAAAM6fAAAAADQAAAAAAAAAAAB1AAAAAAAHAAAADgAAAAEAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAPAAAAAQAAAAAAAAAKAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAABAAAAABanh3AAAAAAgAAAAAAM6fAAAAABQAAAAAAAAAAQB1AAEAAAADAAAAEQAAAAFqeHcAAAAACAAAAAAAzp8AAAAAIgAAAAAAAAABAHUAAAAAAAMAAAASAAAAAWp4dwAAAAAIAAAAAADOnwAAAAAhAAAAAAAAAAEAdQABAAAAAgAAABMAAAABanh3AAAAAAgAAAAAAM6fAAAAACMAAAAAAAAAAQB1AAAAAAACAAAA""",
            2: """AAAAAAoAAAAUAAAAAAAAAAoAAAAAAAAAAQAAAAAAAAAIAAAAAADOnwAAAADIAAAACgAAAAAAdQDU2moAQAAAAAEAAAABAAAAAAAAAAgAAAAAAM6fAAAAANAAAAAKAAAAAAB1ANTaagBAAAAAAgAAAAEAAAAAAAAACAAAAAAAzp8AAAAAywAAAAoAAAAAAHUA1NpqAEAAAAADAAAAAQAAAAAAAAAIAAAAAADOnwAAAADNAAAACgAAAAAAdQDU2moAQAAAAAQAAAABAAAAAAAAAAgAAAAAAM6fAAAAAEMAAAAKAAAAAAB1ANTaagBAAAAABQAAAAEAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAoAAAAAAAAAAAAAAAAAAAAGAAAAAQAAAAAAAAAIAAAAAADOnwAAAABQAAAACgAAAAAAdQDU2moAQAAAAAcAAAABAAAAAAAAAAgAAAAAAM6fAAAAAE0AAAAKAAAAAAB1ANTaagBAAAAACAAAAAEAAAAAAAAACAAAAAAAzp8AAAAASwAAAAoAAAAAAHUA1NpqAEAAAAAJAAAAAQAAAAAAAAAIAAAAAADOnwAAAABIAAAACgAAAAAAdQDU2moAQAAAAAoAAAABAAAAAAAAAAgAAAAAAM6fAAAAAJ0AAAAKAAAAAAB1ANTaagBAAAAACwAAAAEAAAAAAAAACAAAAAAAzp8AAAAASQAAAAoAAAAAAHUA1NpqAEAAAAAMAAAAAQAAAAAAAAAIAAAAAADOnwAAAAC1AAAACgAAAAAAdQDU2moAQAAAAA0AAAABAAAAAAAAAAgAAAAAAM6fAAAAADcAAAAKAAAAAAB1ANTaagBAAAAADgAAAAEAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAoAAAAAAAAAAAAAAAAAAAAPAAAAAQAAAAAAAAAKAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAABAAAAABAAAAAAAAAAgAAAAAAM6fAAAAAMcAAAAKAAAAAAB1ANTaagBAAAAAEQAAAAEAAAAAAAAACAAAAAAAzp8AAAAAzwAAAAoAAAAAAHUA1NpqAEAAAAASAAAAAQAAAAAAAAAIAAAAAADOnwAAAADTAAAACgAAAAAAdQDU2moAQAAAABMAAAABAAAAAAAAAAgAAAAAAM6fAAAAANEAAAAKAAAAAAB1ANTaagBAAAAA"""}

def documents():
    """the user's Documents folder, as the game finds it (also works when it is moved to OneDrive)"""
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(260)
        if ctypes.windll.shell32.SHGetFolderPathW(0, 5, 0, 0, buf) == 0 and buf.value:
            return buf.value
    except Exception:
        pass
    return os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Documents")

def folder():
    home = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    cands = [documents(), os.path.join(home, "Documents"), os.path.join(home, "OneDrive", "Documents")]
    for base in cands:
        d = os.path.join(base, "KOEI", "SAMURAI WARRIORS 2")
        if os.path.isfile(os.path.join(d, "inputmap1.dat")):
            return d
    return os.path.join(cands[0], "KOEI", "SAMURAI WARRIORS 2")

def load(path):
    data = open(path, "rb").read()
    if len(data) != NWORDS * 4:
        sys.exit("ERROR: %s is not 900 bytes, unknown format." % path)
    w = list(struct.unpack("<%dI" % NWORDS, data))
    for i in range(1, 20):
        if w[11 * i + 5] != i:
            sys.exit("ERROR: unexpected format in %s (entry %d)." % (path, i))
    return w

def name(w, i):
    o = 11 * i
    dev, typ, sign, num = w[o + 1], w[o + 2] & 0xFF, w[o + 3], w[o + 4]
    if dev >= 0x0A or num >= 0x40:
        return "None"
    if typ == AXIS:
        return "J%d Axis %d %s" % (dev + 1, num + 1, "-" if sign == MINUS else "+")
    return "J%d B%d" % (dev + 1, num + 1)

def show(w):
    for i in sorted(ACTIONS):
        print("  %-15s %s" % (ACTIONS[i], name(w, i)))

def apply(w, layout, dev):
    for i, (typ, sign, num) in layout.items():
        o = 11 * i
        w[o + 1] = dev                            # 0 = J1, 1 = J2
        w[o + 2] = (w[o + 2] & 0xFFFFFF00) | typ
        w[o + 3] = sign
        w[o + 4] = num
    return w

def main():
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "xbox"
    if cmd not in ("show", "restore") and cmd not in LAYOUTS:
        sys.exit(__doc__)
    import base64
    d = folder()
    for n in (1, 2):
        f = os.path.join(d, "inputmap%d.dat" % n)
        backup = os.path.join(d, "inputmap%d_original.dat" % n)
        if not os.path.isfile(f):
            if cmd in ("show", "restore"):
                print("Controller %d: inputmap%d.dat missing, skipped." % (n, n)); continue
            os.makedirs(d, exist_ok=True)
            open(f, "wb").write(base64.b64decode(TEMPLATE[n]))
            print("Controller %d: no config yet, game default created" % n)
        print("== Controller %d ==" % n)
        if cmd == "show":
            show(load(f)); continue
        if cmd == "restore":
            if not os.path.isfile(backup):
                print("  No original copy."); continue
            shutil.copyfile(backup, f); print("  Original config restored."); show(load(f)); continue
        w = load(f)
        if not os.path.isfile(backup):
            shutil.copyfile(f, backup); print("  Original saved as inputmap%d_original.dat" % n)
        open(f, "wb").write(struct.pack("<%dI" % NWORDS, *apply(w, LAYOUTS[cmd], n - 1)))
        show(load(f))

if __name__ == "__main__":
    main()
