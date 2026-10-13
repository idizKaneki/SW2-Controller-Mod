"""icons_build.py - builds the controller-icon version of the key icon atlas
(BNS entry 43, first texture: 1024x256 DXT5) from the game's own atlas.

    python icons_build.py 00043.bin out_dir

Writes out_dir/icons_xbox.dds-less raw block (icons_xbox.bin) + preview PNGs.
Keyboard key sprites are replaced by the matching Xbox buttons, taken from the
Xbox 360 sprites Koei left in the same atlas (A B X Y, LB RB, d-pad), plus
View / Menu buttons drawn here in the same style.
"""
import sys, os, io, struct, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1024, 256

def load(path):
    d = open(path, 'rb').read()
    g = 64                                       # first GT1G block of entry 43
    assert d[g:g + 4] == b'GT1G'
    tab = struct.unpack_from('<I', d, g + 12)[0]
    o = g + tab + struct.unpack_from('<I', d, g + tab)[0]
    assert d[o + 1] == 8 and d[o + 2] == 0x8A, 'unexpected texture'
    p = o + 8
    return Image.frombytes('RGBA', (W, H), d[p:p + W * H], 'bcn', 3), p, d[p:p + W * H]

def encode(im):
    b = io.BytesIO(); im.save(b, 'DDS', pixel_format='DXT5'); raw = b.getvalue()[128:]
    assert len(raw) == W * H
    return raw

# game sprites (x0, y0, x1, y1)
SPR = {
    'B': (364, 69, 398, 103), 'A': (400, 69, 434, 103), 'Y': (436, 69, 470, 103), 'X': (472, 69, 506, 103),
    'DPAD': (508, 69, 542, 103), 'DPAD_LR': (544, 69, 578, 103), 'DPAD_UD': (580, 69, 614, 103),
    'RB': (0, 90, 36, 118), 'LB': (154, 129, 190, 157),
}
# key slots (x0, y0, x1, y1) -> replacement
SLOTS_XBOX = [
    ((225, 34, 257, 66), 'B'),        # Esc   -> B (back)
    ((293, 34, 325, 66), 'Y'),        # Tab   -> Y
    ((293, 68, 325, 100), 'A'),       # Enter -> A (OK)
    ((259, 34, 291, 66), 'RS_ALL'),   # F12      -> right stick (used for "rotate map", see SW2Controller.asi)
    ((327, 34, 359, 66), 'LS_LR'),    # <->      -> left stick, left/right
    ((225, 68, 257, 100), 'LS_ALL'),  # 4-way    -> left stick
    ((259, 68, 291, 100), 'LS_UD'),   # up/down  -> left stick, up/down
    ((225, 0, 289, 34), 'LB'),        # End
    ((353, 0, 417, 34), 'VIEW'),      # Home
    ((417, 0, 481, 34), 'RB'),        # PgDn
    ((545, 0, 609, 34), 'MENU'),      # Space
    ((609, 0, 673, 34), 'X'),         # Left Shift
]

def ball(sym, size=34, S=8):
    """grey glossy round button (style of the game's Xbox 360 sprites) with a white symbol"""
    n = size * S; im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = n / 2; r = n / 2 - 1.5 * S
    d.ellipse([c - r, c - r, c + r, c + r], fill=(20, 20, 22, 255))
    r2 = r - 2.2 * S
    yy, xx = np.mgrid[0:n, 0:n]
    dist = np.hypot(xx - c + r2 * 0.25, yy - c + r2 * 0.35) / (r2 * 1.5)
    shade = np.clip(1 - dist, 0, 1)
    base = (95 + 120 * shade).astype(np.uint8)
    inner = np.hypot(xx - c, yy - c) <= r2
    arr = np.asarray(im).copy()
    arr[inner, 0] = base[inner]; arr[inner, 1] = base[inner]; arr[inner, 2] = (base[inner] * 1.04).clip(0, 255).astype(np.uint8)
    arr[inner, 3] = 255
    im = Image.fromarray(arr); d = ImageDraw.Draw(im)
    g = Image.new('L', (n, n), 0); gd = ImageDraw.Draw(g)
    u = n / 34
    if sym == 'VIEW':      # two overlapping windows
        gd.rectangle([c - 6.5 * u, c - 6 * u, c + 3 * u, c + 2.5 * u], outline=255, width=int(1.9 * u))
        gd.rectangle([c - 3 * u, c - 2.5 * u, c + 6.5 * u, c + 6 * u], fill=255)
    elif sym == 'MENU':    # three lines
        for k in (-4.2, 0, 4.2):
            gd.rounded_rectangle([c - 6.5 * u, c + (k - 1.1) * u, c + 6.5 * u, c + (k + 1.1) * u], radius=1 * u, fill=255)
    edge = g.filter(ImageFilter.MaxFilter(int(2.2 * u) | 1))
    dark = Image.new('RGBA', (n, n), (25, 25, 28, 255)); white = Image.new('RGBA', (n, n), (250, 250, 250, 255))
    im.paste(dark, (0, 0), edge); im.paste(white, (0, 0), g)
    return im.resize((size, size), Image.LANCZOS)

# PlayStation (PS2 style): same key slots, EU layout (Cross = confirm, Circle = back)
SLOTS_PS = [
    ((225, 34, 257, 66), 'PS_CIRCLE'),   # Esc   -> Circle (back)
    ((293, 34, 325, 66), 'PS_TRIANGLE'), # Tab   -> Triangle
    ((293, 68, 325, 100), 'PS_CROSS'),   # Enter -> Cross (OK)
    ((259, 34, 291, 66), 'RS_ALL'),
    ((327, 34, 359, 66), 'LS_LR'),
    ((225, 68, 257, 100), 'LS_ALL'),
    ((259, 68, 291, 100), 'LS_UD'),
    ((225, 0, 289, 34), 'PS_L1'),        # End
    ((353, 0, 417, 34), 'PS_SELECT'),    # Home
    ((417, 0, 481, 34), 'PS_R1'),        # PgDn
    ((545, 0, 609, 34), 'PS_START'),     # Space
    ((609, 0, 673, 34), 'PS_SQUARE'),    # Left Shift
]

def gloss(n, c, r, base_lo, base_hi, S):
    """glossy round body (dark rim + lit dome), returns RGBA array"""
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([c - r, c - r, c + r, c + r], fill=(12, 12, 14, 255))
    r2 = r - 2.0 * S
    yy, xx = np.mgrid[0:n, 0:n]
    shade = np.clip(1 - np.hypot(xx - c + r2 * 0.3, yy - c + r2 * 0.4) / (r2 * 1.6), 0, 1)
    inner = np.hypot(xx - c, yy - c) <= r2
    arr = np.asarray(im).copy()
    for ch in range(3):
        v = (base_lo[ch] + (base_hi[ch] - base_lo[ch]) * shade).clip(0, 255).astype(np.uint8)
        arr[inner, ch] = v[inner]
    arr[inner, 3] = 255
    # small specular highlight at the top
    hl = np.clip(1 - np.hypot((xx - c) / (r2 * 0.62), (yy - c + r2 * 0.52) / (r2 * 0.32)), 0, 1) * inner
    for ch in range(3):
        arr[..., ch] = (arr[..., ch] + (255 - arr[..., ch]) * hl * 0.45).astype(np.uint8)
    return arr

PS_COL = {'PS_CROSS': (125, 175, 255), 'PS_CIRCLE': (255, 105, 105),
          'PS_SQUARE': (255, 140, 225), 'PS_TRIANGLE': (80, 235, 175)}

def psbutton(key, size=34, S=8):
    """PS2-style face button: black glossy ball with the coloured symbol"""
    n = size * S; c = n / 2; u = n / 34
    im = Image.fromarray(gloss(n, c, n / 2 - 1.5 * S, (30, 30, 34), (105, 105, 115), S))
    g = Image.new('L', (n, n), 0); gd = ImageDraw.Draw(g); w = int(3.3 * u)
    if key == 'PS_CROSS':
        k = 7.6 * u
        gd.line([c - k, c - k, c + k, c + k], fill=255, width=w); gd.line([c - k, c + k, c + k, c - k], fill=255, width=w)
    elif key == 'PS_CIRCLE':
        k = 8.4 * u; gd.ellipse([c - k, c - k, c + k, c + k], outline=255, width=w)
    elif key == 'PS_SQUARE':
        k = 7.3 * u; gd.rectangle([c - k, c - k, c + k, c + k], outline=255, width=w)
    elif key == 'PS_TRIANGLE':
        k = 9.6 * u; h = k * 0.866; cy = c + 1.4 * u
        gd.polygon([(c, cy - k), (c - h, cy + k * 0.5), (c + h, cy + k * 0.5)], outline=255, width=w)
    edge = g.filter(ImageFilter.MaxFilter(int(1.4 * u) | 1))
    im.paste(Image.new('RGBA', (n, n), (8, 8, 10, 255)), (0, 0), edge)
    im.paste(Image.new('RGBA', (n, n), PS_COL[key] + (255,)), (0, 0), g)
    return im.resize((size, size), Image.LANCZOS)

def psshoulder(text, size=(46, 28), S=8):
    """L1 / R1: light grey rounded shoulder button with dark text (like the game's LB/RB sprites)"""
    from PIL import ImageFont
    W_, H_ = size[0] * S, size[1] * S; u = S
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([1 * u, 1 * u, W_ - 1 * u, H_ - 1 * u], radius=9 * u, fill=(15, 15, 18, 255))
    d.rounded_rectangle([3 * u, 3 * u, W_ - 3 * u, H_ - 3 * u], radius=7 * u, fill=(205, 205, 210, 255))
    d.rounded_rectangle([3 * u, 3 * u, W_ - 3 * u, H_ * 0.5], radius=7 * u, fill=(238, 238, 242, 255))
    f = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', int(17 * u))
    d.text((W_ / 2, H_ / 2 + 1 * u), text, font=f, anchor='mm', fill=(20, 20, 24, 255))
    return im.resize(size, Image.LANCZOS)

def psmeta(key, size=34, S=8):
    """SELECT / START (PS2): grey glossy ball with a white bar / play triangle"""
    n = size * S; c = n / 2; u = n / 34
    im = Image.fromarray(gloss(n, c, n / 2 - 1.5 * S, (70, 70, 76), (190, 190, 198), S))
    g = Image.new('L', (n, n), 0); gd = ImageDraw.Draw(g)
    if key == 'PS_SELECT':
        gd.rounded_rectangle([c - 7.5 * u, c - 2.4 * u, c + 7.5 * u, c + 2.4 * u], radius=2 * u, fill=255)
    else:
        gd.polygon([(c - 4.5 * u, c - 7 * u), (c - 4.5 * u, c + 7 * u), (c + 7.5 * u, c)], fill=255)
    edge = g.filter(ImageFilter.MaxFilter(int(2.2 * u) | 1))
    im.paste(Image.new('RGBA', (n, n), (25, 25, 28, 255)), (0, 0), edge)
    im.paste(Image.new('RGBA', (n, n), (250, 250, 250, 255)), (0, 0), g)
    return im.resize((size, size), Image.LANCZOS)

def stick(letter, arrows, size=32, S=8):
    """thumbstick seen from above (Xbox style) with the stick letter and white direction arrows around it"""
    from PIL import ImageFont
    n = size * S; c = n / 2; u = n / 32
    R = 13.0 if arrows else 15.5
    im = Image.new('RGBA', (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def tri(dx, dy):
        tip = (c + dx * 16.2 * u, c + dy * 16.2 * u); b = R - 0.6
        p1 = (c + dx * b * u - dy * 4.0 * u, c + dy * b * u - dx * 4.0 * u)
        p2 = (c + dx * b * u + dy * 4.0 * u, c + dy * b * u + dx * 4.0 * u)
        d.polygon([tip, p1, p2], fill=(250, 250, 250, 255), outline=(15, 15, 15, 255), width=int(1.1 * u))
    for a in arrows:
        tri(*{'u': (0, -1), 'd': (0, 1), 'l': (-1, 0), 'r': (1, 0)}[a])
    d.ellipse([c - R * u, c - R * u, c + R * u, c + R * u], fill=(18, 18, 20, 255))
    yy, xx = np.mgrid[0:n, 0:n]
    r = np.hypot(xx - c, yy - c) / u
    shade = np.clip(1 - np.hypot(xx - c + 3 * u, yy - c + 4 * u) / (18 * u), 0, 1)
    arr = np.asarray(im).copy()
    rim = (r <= R - 1.3) & (r > R - 3.8); cap = r <= R - 3.8
    g1 = (75 + 75 * shade).astype(np.uint8); g2 = (45 + 65 * shade).astype(np.uint8)
    for ch in range(3):
        arr[rim, ch] = g1[rim]; arr[cap, ch] = g2[cap]
    arr[rim | cap, 3] = 255
    im = Image.fromarray(arr); d = ImageDraw.Draw(im)
    f = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', int(R * 0.95 * u))
    d.text((c, c + 0.5 * u), letter, font=f, anchor='mm', fill=(245, 245, 245, 255),
           stroke_width=int(1.1 * u), stroke_fill=(15, 15, 15, 255))
    return im.resize((size, size), Image.LANCZOS)

def build(atlas, slots):
    out = atlas.copy()
    src = {k: atlas.crop(v) for k, v in SPR.items()}
    src['VIEW'] = ball('VIEW'); src['MENU'] = ball('MENU')
    src['LS_LR'] = stick('L', 'lr'); src['LS_UD'] = stick('L', 'ud'); src['LS_ALL'] = stick('L', 'udlr')
    src['RS_ALL'] = stick('R', 'udlr')
    for k in PS_COL: src[k] = psbutton(k)
    src['PS_L1'] = psshoulder('L1'); src['PS_R1'] = psshoulder('R1')
    src['PS_SELECT'] = psmeta('PS_SELECT'); src['PS_START'] = psmeta('PS_START')
    for (x0, y0, x1, y1), key in slots:
        out.paste(Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0)), (x0, y0))
        s = src[key]
        h = y1 - y0; k = min(1.0, h / s.height, (x1 - x0) / s.width)
        if k < 1: s = s.resize((round(s.width * k), round(s.height * k)), Image.LANCZOS)
        out.alpha_composite(s, (x0 + (x1 - x0 - s.width) // 2, y0 + (h - s.height) // 2))
    return out

def preview(im, path, box=(150, 0, 680, 130), s=2):
    c = im.crop(box); bg = Image.new('RGBA', c.size, (60, 60, 60, 255)); bg.alpha_composite(c)
    bg.resize((c.width * s, c.height * s), Image.NEAREST).save(path)

def make_patch(atlas, orig, im):
    """DXT5 patch: re-encode, keep original blocks wherever the picture did not change"""
    enc = encode(im)
    a0 = np.asarray(atlas); a1 = np.asarray(im)
    raw = bytearray(orig); changed = []
    for by in range(H // 4):
        for bx in range(W // 4):
            if not np.array_equal(a0[by*4:by*4+4, bx*4:bx*4+4], a1[by*4:by*4+4, bx*4:bx*4+4]):
                k = (by * (W // 4) + bx) * 16
                raw[k:k + 16] = enc[k:k + 16]; changed.append(k // 16)
    raw = bytes(raw)
    # patch file: 'SW2I' + md5(original) + md5(new) + count + (block, old16, new16)*
    pat = b'SW2I' + hashlib.md5(orig).digest() + hashlib.md5(raw).digest() + struct.pack('<I', len(changed))
    for b in changed: pat += struct.pack('<I', b) + orig[b*16:b*16+16] + raw[b*16:b*16+16]
    return pat, raw

if __name__ == '__main__':
    src, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    atlas, pos, orig = load(src)
    print('original md5', hashlib.md5(orig).hexdigest())
    preview(atlas, os.path.join(out_dir, 'preview_keyboard.png'))
    for name, slots in (('xbox', SLOTS_XBOX), ('playstation', SLOTS_PS)):
        pat, raw = make_patch(atlas, orig, build(atlas, slots))
        open(os.path.join(out_dir, 'icons_%s.patch' % name), 'wb').write(pat)
        print(name, 'md5', hashlib.md5(raw).hexdigest(), 'patch bytes', len(pat))
        preview(Image.frombytes('RGBA', (W, H), raw, 'bcn', 3), os.path.join(out_dir, 'preview_%s.png' % name))
