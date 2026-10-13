# -*- coding: utf-8 -*-
"""sw2_icons.py - Samurai Warriors 2 (PC): controller button icons in menus.

Replaces the keyboard key icons (Enter, Esc, Tab, arrows...) shown in the menus
with controller buttons. Run it from the game folder (or its linkdata folder),
game closed:

    python sw2_icons.py xbox        -> Xbox buttons
    python sw2_icons.py playstation -> PlayStation buttons
    python sw2_icons.py keyboard    -> back to the original keyboard icons
    python sw2_icons.py status      -> show what is installed
(an optional last argument gives the game folder)

Every copy of the icon sheet found in LINKDATA_BNS_NA.lnk / LINKDATA_DNS_NA.lnk
is patched in place (same size). Each change is checked against the original
first: anything unexpected is left untouched.
"""
import sys, os, struct, hashlib

W, H = 1024, 256
SIZE = W * H                      # DXT5 bytes of the icon sheet
CHUNK = 64 * 1024 * 1024
HERE = os.path.dirname(os.path.abspath(__file__))
STYLES = {'xbox': 'icons_xbox.patch', 'playstation': 'icons_playstation.patch', 'xbox (old test version)': 'icons_xbox_old.patch',
          'xbox (old test version 2)': 'icons_xbox_old2.patch',
          'xbox (old test version 3)': 'icons_xbox_old3.patch'}

def load_patch(name):
    d = open(os.path.join(HERE, name), 'rb').read()
    assert d[:4] == b'SW2I', 'bad patch file ' + name
    md5_old, md5_new = d[4:20], d[20:36]
    n = struct.unpack_from('<I', d, 36)[0]; blocks = []
    for i in range(n):
        o = 40 + 36 * i
        b = struct.unpack_from('<I', d, o)[0]
        blocks.append((b * 16, d[o + 4:o + 20], d[o + 20:o + 36]))
    return md5_old, md5_new, blocks

def linkdata(game=None):
    dirs = [os.path.join(game, 'linkdata')] if game else ['linkdata', '.', os.path.join('..', 'linkdata')]
    for d in dirs:
        if os.path.isfile(os.path.join(d, 'LINKDATA_BNS_NA.lnk')):
            return d
    sys.exit("ERROR: LINKDATA_BNS_NA.lnk not found. Run this from the game folder.")

def sheets(f, size):
    """offsets of every 1024x256 DXT5 texture inside GT1G blocks of the archive"""
    pos = 0; prev = b''
    while pos < size:
        f.seek(pos); bloc = f.read(CHUNK)
        if not bloc: break
        data = prev + bloc; base = pos - len(prev); i = 0
        while True:
            i = data.find(b'GT1G', i)
            if i < 0: break
            off = base + i; i += 4
            back = f.tell(); f.seek(off); h = f.read(20)
            ok = len(h) == 20 and all(48 <= c <= 57 for c in h[4:8])
            if ok:
                tot, tab, nb = struct.unpack_from('<3I', h, 8)
                ok = 0 < nb < 64 and 0x10 <= tab < 0x10000
            if ok:
                f.seek(off + tab); offs = f.read(4 * nb)
                for k in range(nb):
                    o = struct.unpack_from('<I', offs, 4 * k)[0]
                    f.seek(off + tab + o); t = f.read(4)
                    if len(t) == 4 and t[1] == 8 and t[2] == 0x8A:
                        yield off + tab + o + 8
            f.seek(back)
        prev = data[-3:]; pos += len(bloc)

def main():
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else ''
    if cmd not in ('xbox', 'playstation', 'keyboard', 'status'):
        sys.exit(__doc__)
    game = sys.argv[2] if len(sys.argv) > 2 else None
    patches = {k: load_patch(v) for k, v in STYLES.items() if os.path.isfile(os.path.join(HERE, v))}
    if cmd in ('xbox', 'playstation') and cmd not in patches:
        sys.exit('ERROR: icons_%s.patch is missing (keep it next to this script).' % cmd)
    known = {}                                   # md5 -> style name
    for k, (m_old, m_new, _) in patches.items():
        known[m_old] = 'keyboard'; known[m_new] = k
    d = linkdata(game); total = done = 0
    for arch in ('LINKDATA_BNS_NA.lnk', 'LINKDATA_DNS_NA.lnk'):
        p = os.path.join(d, arch)
        if not os.path.isfile(p): continue
        print('scanning', arch, '...', flush=True)
        size = os.path.getsize(p)
        with open(p, 'rb' if cmd == 'status' else 'r+b') as f:
            for pos in list(sheets(f, size)):
                f.seek(pos); px = f.read(SIZE)
                state = known.get(hashlib.md5(px).digest())
                if state is None: continue           # another 1024x256 texture
                total += 1
                if cmd == 'status':
                    print('  icon sheet at', pos, ':', state); continue
                if state == cmd:
                    print('  icon sheet at', pos, ': already', cmd); continue
                px = bytearray(px)
                if state != 'keyboard':                # go back to the original first
                    for o, old, new in patches[state][2]: px[o:o + 16] = old
                if cmd != 'keyboard':
                    for o, old, new in patches[cmd][2]: px[o:o + 16] = new
                f.seek(pos); f.write(px); done += 1
                print('  icon sheet at', pos, ':', state, '->', cmd)
    if not total:
        sys.exit('ERROR: icon sheet not found (unknown game version?). Nothing changed.')
    if cmd != 'status':
        print('Done: %d icon sheet(s) changed.' % done)

if __name__ == '__main__':
    main()
