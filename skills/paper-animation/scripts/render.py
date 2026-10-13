"""PaperAnimation renderer: the newspaper highlight video.

usage: render.py "<phrase>" <W> <H> <FPS> <out.mp4> [--cards-dir DIR] [--sound] [--web]
Each card is a different printed/online page with the phrase highlighted and
pinned to the exact centre of the frame; 23 cards step at 8 cards/s (each card
0.125 s, the last held 0.25 s) = exactly 3.0 s at any frame rate.

Pages are laid out on a canvas whose short side is 1080 units and drawn at
S = short side / 1080, so 4K output is the same design rendered natively sharp.
"""
import sys, os, math, random, subprocess, tempfile, zlib
import numpy as np, cv2, skia
from copy_text import *

KW, PW, PH, FPS, OUT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
CARDS_DIR = sys.argv[sys.argv.index("--cards-dir") + 1] if "--cards-dir" in sys.argv else None
SOUND = "--sound" in sys.argv  # projector rattle under the whole video (sound.py)
WEB = "--web" in sys.argv  # cap the file at about 24 MB for web apps' 30 MB download limit
CARD_T, LAST_T = 0.125, 0.25
S = min(PW, PH) / 1080  # output pixels per layout unit
W, H = round(PW / S), round(PH / S)  # layout canvas; every size below is in these units
FM = skia.FontMgr.RefDefault()
# Open-licence stand-ins (assets/fonts) for any design font the system lacks, e.g. on Windows
# and Linux. macOS has every design font, so there the bundled ones are never used.
BUNDLED = skia.FontMgr.New_Custom_Directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts"))
FALLBACK = {
    "Times New Roman": "Tinos", "Georgia": "Gelasio", "Baskerville": "PA Baskerville", "Charter": "PA Serif",
    "Hoefler Text": "Libre Caslon Text", "PT Serif": "PA Serif", "Iowan Old Style": "PA Serif", "Palatino": "Gelasio",
    "Cochin": "Libre Caslon Text", "Bodoni 72": "Bodoni Moda", "Didot": "PA Didone", "Big Caslon": "Libre Caslon Text",
    "Futura": "Jost", "Avenir Next": "Jost", "Gill Sans": "Jost", "Helvetica Neue": "Arimo", "Arial": "Arimo",
    "Verdana": "Arimo", "American Typewriter": "Courier Prime", "Courier New": "Courier Prime", "Impact": "Anton",
    "Arial Black": "Archivo Black", "DIN Condensed": "Oswald", "Avenir Next Condensed": "Oswald",
}
FORCE_BUNDLED = os.environ.get("PAPER_ANIMATION_BUNDLED_FONTS") == "1"  # preview the Windows/Linux look on a Mac
_tf = {}


def typeface(name, bold=False, italic=False):
    k = (name, bold, italic)
    if k not in _tf:
        st = skia.FontStyle(700 if bold else 400, 5, skia.FontStyle.kItalic_Slant if italic else skia.FontStyle.kUpright_Slant)
        tf = None if FORCE_BUNDLED else FM.matchFamilyStyle(name, st)
        # Linux font managers return a substitute instead of nothing, so check the family name too
        if tf is None or tf.getFamilyName().lower() != name.lower():
            tf = BUNDLED.matchFamilyStyle(FALLBACK[name], st)
        _tf[k] = tf
    return _tf[k]


def kwtext(case):
    title = " ".join(w if any(ch.isupper() for ch in w) else w[:1].upper() + w[1:] for w in KW.split(" "))
    return {"sent": KW, "title": title, "upper": KW.upper()}[case]


class Sty:
    def __init__(s, face, size, bold=False, italic=False, color=(24, 22, 20), lead=1.45, justify=False,
                 align="left", indent=0.0, after=0.6, case="sent", upper=False, track=0.0):
        size *= 1.2
        s.face, s.size, s.bold, s.italic, s.color = face, size, bold, italic, color
        s.lead, s.justify, s.align, s.indent, s.after, s.case, s.upper, s.track = lead, justify, align, indent, after, case, upper, track
        s.font = skia.Font(typeface(face, bold, italic), size)
        s.font.setSubpixel(True)
        s.font.setEdging(skia.Font.Edging.kAntiAlias)
        s.cap = s.font.getMetrics().fCapHeight or size * 0.7

    def rescale(s, f):
        s.size *= f
        s.font = skia.Font(typeface(s.face, s.bold, s.italic), s.size)
        s.font.setSubpixel(True)
        s.font.setEdging(skia.Font.Edging.kAntiAlias)
        s.cap = s.font.getMetrics().fCapHeight or s.size * 0.7

    def w(s, t):
        return s.font.measureText(t) + s.track * s.size * len(t)


def tokens(text, sty):
    """Split into words; the keyword (with glued punctuation) is one token with a span."""
    k = kwtext(sty.case)
    if sty.upper:
        text = text.upper()
    out = []
    parts = text.split("{K}") if "{K}" in text else [text]
    if sty.upper:
        parts = text.split("{K}")
    for i, p in enumerate(parts):
        words = p.split(" ")
        if i > 0:  # keyword goes before this part's first fragment (glued punctuation)
            glue = words[0]
            out.append((k + glue, (0, len(k))))
            words = words[1:]
        if i < len(parts) - 1:
            # trailing fragment immediately before {K} (e.g. opening quote) glues to keyword
            pre = words[-1]
            words = words[:-1]
            for wd in words:
                if wd:
                    out.append((wd, None))
            out.append(("\0" + pre, None))  # marker: glue to next
        else:
            for wd in words:
                if wd:
                    out.append((wd, None))
    # merge glue markers
    merged = []
    i = 0
    while i < len(out):
        t, sp = out[i]
        if t.startswith("\0"):
            pre = t[1:]
            nt, nsp = out[i + 1]
            merged.append((pre + nt, (len(pre) + nsp[0], len(pre) + nsp[1])))
            i += 2
        else:
            merged.append((t, sp))
            i += 1
    return merged


def layout_text(text, sty, width):
    """Return ops (relative to block top), height, kw rect or None."""
    toks = tokens(text, sty)
    sp = sty.w(" ")
    lines, cur, cw = [], [], 0.0
    first = True
    for t, s in toks:
        tw = sty.w(t)
        avail = width - (sty.indent * sty.size if first and not lines else 0)
        add = tw + (sp if cur else 0)
        if cur and cw + add > avail:
            lines.append(cur)
            cur, cw = [], 0.0
            add = tw
        cur.append((t, s, tw))
        cw += add
    if cur:
        lines.append(cur)
    ops, kw = [], None
    lh = sty.size * sty.lead
    y = 0.0
    for li, ln in enumerate(lines):
        base = y + sty.size * 0.95
        x0 = sty.indent * sty.size if li == 0 else 0.0
        avail = width - x0
        tot = sum(tw for _, _, tw in ln)
        gap = sp
        if sty.justify and li < len(lines) - 1 and len(ln) > 1:
            gap = (avail - tot) / (len(ln) - 1)
        lw = tot + gap * (len(ln) - 1)
        if sty.align == "center":
            x0 += (avail - lw) / 2
        elif sty.align == "right":
            x0 += avail - lw
        x = x0
        for t, s, tw in ln:
            ops.append(("text", x, base, t, sty))
            if s:
                a = x + sty.w(t[: s[0]])
                b = x + sty.w(t[: s[1]])
                kw = (a, b, base, sty)
            x += tw + gap
        y += lh
    return ops, y + sty.size * sty.after, kw


class Block:
    def __init__(s, kind, **kw):
        s.kind, s.kw = kind, kw

    def layout(s, width):
        k, a = s.kind, s.kw
        if k == "text":
            return layout_text(a["text"], a["sty"], width)
        if k == "rule":
            t, pad = a.get("t", 2), a.get("pad", 20)
            return [("rule", 0, pad, width, pad, t, a.get("color", (24, 22, 20)))], pad * 2 + t, None
        if k == "space":
            return [], a["h"], None
        if k == "image":
            h = width * a["ratio"]
            return [("image", 0, 0, width, h, a["seed"], a.get("tone", "print"))], h + a.get("pad", 24), None
        if k == "bar":  # filled band, e.g. web nav
            h = a["h"]
            ops = [("rect", -a.get("bleed", 0), 0, width + 2 * a.get("bleed", 0), h, a["color"])]
            for (t, x, sty) in a.get("items", []):
                ops.append(("text", x, h / 2 + sty.cap / 2, t, sty))
            return ops, h + a.get("pad", 30), None
        raise ValueError(k)


# ----------------------------------------------------------------- card designs
_pools = {}


def pick(name, lst):
    """Draw without repeats within one video (keyword copy must not recur)."""
    if not _pools.get(name):
        _pools[name] = random.Random(name + KW).sample(lst, len(lst))
    return _pools[name].pop()


def rnd_para(r, n=None):
    return " ".join(r.sample(FILLER, n or r.randint(2, 4)))


def kw_para(r):
    s = pick("sent", KW_SENT)
    f, n = r.sample(FILLER, 4), r.randint(0, 2)
    return " ".join(f[:n] + [s] + f[n:n + r.randint(1, 2)])


def card(kind, r):
    """Return dict: bg, kwblock, filler(r)->Block list, colw, gutter, rot, dof, colrule."""
    c = dict(kind=kind, rot=0.0, dof=0.0, colrule=True, ink=(24, 22, 20))
    serifs = ["Times New Roman", "Georgia", "Baskerville", "Charter", "Hoefler Text", "PT Serif", "Iowan Old Style", "Palatino", "Cochin"]
    heads = ["Times New Roman", "Georgia", "Baskerville", "Charter", "PT Serif", "Bodoni 72", "Big Caslon", "Hoefler Text"]

    if kind in ("news_body", "news_head", "news_dense"):
        face = r.choice(serifs)
        hf = r.choice(heads)
        size = {"news_body": r.uniform(46, 60), "news_head": r.uniform(38, 48), "news_dense": r.uniform(30, 38)}[kind]
        body = Sty(face, size, lead=r.uniform(1.38, 1.6), justify=True, indent=r.choice([0, 0.8, 1.2]), after=r.uniform(0.4, 0.9))
        hsz = size * r.uniform(1.35, 1.7) if kind != "news_head" else r.uniform(78, 104)
        head = lambda t, sz=None: Sty(hf, sz or hsz, bold=r.random() < 0.85, lead=1.15, after=0.45, case="title")
        c["bg"] = "news"
        c["colw"] = r.uniform(1.05, 1.5) * W if W < H else r.uniform(0.38, 0.5) * W
        c["gutter"] = size * 1.4
        if kind == "news_head":
            c["kwblock"] = [Block("text", text=pick("heads", KW_HEADS), sty=head(None))]
        else:
            c["kwblock"] = [Block("text", text=kw_para(r), sty=body)]

        def filler(r):
            if r.random() < 0.2:
                return [Block("text", text=r.choice(FILLER_HEADS), sty=head(None, size * r.uniform(1.3, 1.7)))]
            return [Block("text", text=rnd_para(r), sty=body)]
        c["filler"] = filler
        c["rot"] = r.choice([0, 0, 0, r.uniform(-2.2, 2.2)])
        c["dof"] = r.choice([0, 0, r.uniform(2, 4.5)])

    elif kind == "magazine":
        face = r.choice(["Didot", "Bodoni 72", "Baskerville", "Big Caslon"])
        sans = r.choice(["Futura", "Avenir Next", "Gill Sans", "Helvetica Neue"])
        accent = r.choice([(196, 40, 46), (20, 90, 170), (20, 20, 20), (210, 80, 30)])
        q = Sty(face, r.uniform(78, 100), italic=r.random() < 0.6, lead=1.18, align="left", after=0.4)
        body = Sty(r.choice(["Baskerville", "Georgia", "Charter", "Hoefler Text"]), r.uniform(38, 46), lead=1.55, justify=False, after=0.8)
        kick = Sty(sans, 30, bold=True, color=accent, after=0.6, upper=True, track=0.12)
        c["bg"] = "mag"
        c["colrule"] = False
        c["colw"] = r.uniform(0.85, 1.0) * W if W < H else r.uniform(0.45, 0.55) * W
        c["gutter"] = 90
        c["kwblock"] = [Block("rule", t=5, pad=18, color=accent), Block("text", text=pick("quotes", KW_QUOTES), sty=q),
                        Block("text", text="— " + r.choice(NAMES), sty=Sty(sans, 30, color=accent, after=0.6)),
                        Block("rule", t=5, pad=18, color=accent)]
        def filler(r):
            if r.random() < 0.15:
                return [Block("text", text=r.choice(KICKERS), sty=kick)]
            return [Block("text", text=rnd_para(r, 2), sty=body)]
        c["filler"] = filler
        c["rot"] = r.uniform(-1.5, 1.5)

    elif kind == "mag_head":
        face = r.choice(["Didot", "Bodoni 72"])
        sans = r.choice(["Futura", "Avenir Next", "Gill Sans"])
        accent = r.choice([(196, 40, 46), (20, 90, 170), (230, 90, 30)])
        hd = Sty(face, r.uniform(112, 140), bold=r.random() < 0.5, lead=1.08, after=0.35, case="title")
        dek = Sty(sans, 40, color=(70, 66, 62), lead=1.4, after=0.9)
        body = Sty("Baskerville", 40, lead=1.55, after=0.8)
        c["bg"] = "mag"
        c["colrule"] = False
        c["colw"] = r.uniform(0.9, 1.0) * W if W < H else 0.6 * W
        c["gutter"] = 90
        c["kwblock"] = [Block("text", text=r.choice(KICKERS), sty=Sty(sans, 32, bold=True, color=accent, upper=True, track=0.14, after=0.8)),
                        Block("text", text=pick("heads", KW_HEADS), sty=hd),
                        Block("text", text=r.choice(FILLER), sty=dek)]
        c["filler"] = lambda r: ([Block("text", text=r.choice(KICKERS), sty=Sty(sans, 32, bold=True, color=accent, upper=True, track=0.14, after=0.8))]
                                 if r.random() < 0.15 else [Block("text", text=rnd_para(r, 2), sty=body)])

    elif kind in ("web_body", "web_head", "web_dark"):
        dark = kind == "web_dark"
        fg = (232, 232, 230) if dark else (22, 22, 24)
        sub = (150, 150, 155) if dark else (110, 110, 115)
        sans = r.choice(["Helvetica Neue", "Avenir Next", "Arial", "Verdana"] if kind != "web_head" else ["Helvetica Neue", "Avenir Next", "Futura"])
        serif = r.choice(["Georgia", "Charter", "PT Serif"])
        bodyface = r.choice([sans, serif])
        body = Sty(bodyface, r.uniform(44, 52), color=fg, lead=1.6, after=1.0)
        hd = Sty(sans if r.random() < 0.6 else serif, r.uniform(84, 104), bold=True, color=fg, lead=1.12, after=0.45, case="title")
        accent = r.choice([(0, 102, 204), (210, 40, 40), (16, 140, 90)])
        site = r.choice(SITES)
        bar_bg = (28, 28, 30) if dark else r.choice([(255, 255, 255), (18, 18, 20), accent])
        bar_fg = (255, 255, 255) if bar_bg != (255, 255, 255) else (18, 18, 20)
        navf = Sty(sans, 30, bold=False, color=bar_fg)
        items = [(site, 40, Sty(serif if r.random() < 0.5 else sans, 52, bold=True, color=bar_fg))]
        x = 40 + items[0][2].w(site) + 70
        for nm in ["World", "Business", "Tech", "Culture", "Opinion", "Science"]:
            items.append((nm, x, navf))
            x += navf.w(nm) + 44
        c["bg"] = "webdark" if dark else "web"
        c["ink"] = fg
        c["colrule"] = False
        c["colw"] = r.uniform(0.86, 0.92) * W if W < H else 0.5 * W
        c["gutter"] = 110
        meta = Sty(sans, 30, color=sub, after=1.1)
        kick = Sty(sans, 30, bold=True, color=accent, upper=True, track=0.06, after=0.7)
        if kind == "web_head":
            c["kwblock"] = [Block("text", text=r.choice(KICKERS), sty=kick), Block("text", text=pick("heads", KW_HEADS), sty=hd),
                            Block("text", text="By %s  ·  %d min read" % (r.choice(NAMES), r.randint(3, 9)), sty=meta)]
        else:
            c["kwblock"] = [Block("text", text=kw_para(r), sty=body)]
        tz = Sty(sans, 40, bold=True, color=fg, lead=1.3, after=0.5)

        def filler(r):
            x = r.random()
            if x < 0.25:
                return [Block("text", text=r.choice(TEASERS), sty=tz), Block("rule", t=2, pad=26, color=(60, 60, 64) if dark else (215, 215, 218))]
            return [Block("text", text=rnd_para(r, 2), sty=body)]
        c["filler"] = filler
        c["nav"] = Block("bar", h=120, color=bar_bg, items=items, bleed=3000, pad=60)

    elif kind == "memo":
        face = r.choice(["American Typewriter", "Courier New"])
        body = Sty(face, r.uniform(42, 50), lead=1.7, after=1.0, color=(30, 30, 40))
        c["bg"] = "memo"
        c["colrule"] = False
        c["colw"] = 0.92 * W if W < H else 0.55 * W
        c["gutter"] = 200
        c["kwblock"] = [Block("text", text=kw_para(r), sty=body)]
        c["filler"] = lambda r: [Block("text", text=rnd_para(r, 2), sty=body)]
        c["rot"] = r.uniform(-1.8, 1.8)

    elif kind == "tabloid":
        face = r.choice(["Impact", "Arial Black", "DIN Condensed", "Avenir Next Condensed"])
        big = Sty(face, r.uniform(190, 250) if W < H else r.uniform(210, 260), bold=True, lead=1.0, after=0.25, case="upper", upper=True, align="center")
        sub = Sty("Times New Roman", 56, bold=True, italic=True, lead=1.2, align="center", after=0.8)
        body = Sty("Times New Roman", 40, lead=1.45, justify=True, after=0.7)
        c["bg"] = "news"
        c["colw"] = 0.98 * W if W < H else 0.62 * W
        c["gutter"] = 60
        c["kwblock"] = [Block("text", text=KW_TABLOID[TAB.pop(0)], sty=big),
                        Block("text", text=r.choice(FILLER_HEADS), sty=sub)]
        c["filler"] = lambda r: ([Block("rule", t=6, pad=16)] if r.random() < 0.2 else [Block("text", text=rnd_para(r, 2), sty=body)])
        c["rot"] = r.uniform(-1.2, 1.2)
    return c


# ----------------------------------------------------------------- layout + draw
def stack(blocks, width):
    ops, y, kw = [], 0.0, None
    for b in blocks:
        o, h, k = b.layout(width)
        ops += [shift(op, 0, y) for op in o]
        if k:
            kw = (k[0], k[1], k[2] + y, k[3])
        y += h
    return ops, y, kw


def shift(op, dx, dy):
    t = op[0]
    if t == "text":
        return (t, op[1] + dx, op[2] + dy) + op[3:]
    if t in ("rule",):
        return (t, op[1] + dx, op[2] + dy, op[3] + dx, op[4] + dy) + op[5:]
    if t in ("image", "rect"):
        return (t, op[1] + dx, op[2] + dy) + op[3:]
    raise ValueError(t)


def build_page(c, r):
    cw = c["colw"]
    # long phrases: shrink the phrase's style so the highlight always fits the frame
    lim = 0.86 * min(W, cw)
    for b in c["kwblock"]:
        if b.kind == "text" and "{K}" in b.kw["text"]:
            st = b.kw["sty"]
            kw_w = st.w(kwtext(st.case))
            if kw_w > lim:
                st.rescale(lim / kw_w)
    reach = 0.62 * math.hypot(W, H) + 200  # page area needed around the keyword
    # main column: filler above, keyword block, filler below
    kops, kh, kw = stack(c["kwblock"], cw)
    kcy = (kw[2] - kw[3].cap / 2)
    above, ah = [], 0.0
    while ah < reach - kcy:
        bl = c["filler"](r)
        ah += stack(bl, cw)[1]
        above = bl + above
    if "nav" in c:
        above = [c["nav"]] + above[-r.randint(1, 3):]
    below, bh = [], 0.0
    while bh < reach:
        bl = c["filler"](r)
        bh += stack(bl, cw)[1]
        below += bl
    ops, total, kw = stack(above + c["kwblock"] + below, cw)
    kcx, kcy = (kw[0] + kw[1]) / 2, kw[2] - kw[3].cap / 2
    # neighbour columns to cover the frame horizontally
    g = c["gutter"]
    xs = []
    x = -cw - g
    while x + cw > kcx - reach:
        xs.append(x)
        x -= cw + g
    x = cw + g
    while x < kcx + reach:
        xs.append(x)
        x += cw + g
    top = 0.0
    if "nav" in c:
        top = stack([c["nav"]], cw)[1]
    for x in xs:
        bl, h = [], 0.0
        start = top - r.uniform(0, 300)
        while h < total - start:
            nb = c["filler"](r)
            h += stack(nb, cw)[1]
            bl += nb
        o, _, _ = stack(bl, cw)
        ops += [shift(op, x, start) for op in o]
        if c["colrule"]:
            ops.append(("rule", x + cw + g / 2 if x < 0 else x - g / 2, -2000, x + cw + g / 2 if x < 0 else x - g / 2, total + 2000, 2, c["ink"]))
    return ops, kw, (kcx, kcy)


def photo(seed, w, h, tone):
    rr = np.random.default_rng(seed)
    sw, sh = max(4, int(w / 40)), max(4, int(h / 40))
    n = cv2.resize(rr.random((sh, sw)).astype(np.float32), (int(w), int(h)), interpolation=cv2.INTER_CUBIC)
    n = cv2.GaussianBlur(n, (0, 0), w / 30)
    n = (n - n.min()) / (np.ptp(n) + 1e-6)
    yy = np.linspace(0, 1, int(h))[:, None]
    g = 0.25 + 0.55 * n * (0.6 + 0.4 * yy)
    if tone == "color":
        tint = np.array([rr.uniform(0.6, 1), rr.uniform(0.6, 1), rr.uniform(0.6, 1)])
        rgb = np.clip(g[..., None] * tint[None, None] * 1.1, 0, 1)
    else:
        rgb = np.repeat(g[..., None], 3, 2)
    a = np.ones(g.shape + (1,))
    return (np.concatenate([rgb, a], 2) * 255).astype(np.uint8)


def draw(ops, kw, kc, rot, ink_default):
    s_ink = skia.Surface(PW, PH)
    s_hl = skia.Surface(PW, PH)
    for s in (s_ink, s_hl):
        cv = s.getCanvas()
        cv.clear(skia.Color4f(0, 0, 0, 0))
        cv.scale(S, S)
        cv.translate(W / 2, H / 2)
        cv.rotate(rot)
        cv.translate(-kc[0], -kc[1])
    ci = s_ink.getCanvas()
    p = skia.Paint(AntiAlias=True)
    for op in ops:
        t = op[0]
        if t == "text":
            _, x, y, txt, sty = op
            p.setColor(skia.Color(*sty.color))
            if sty.track:
                for ch in txt:
                    ci.drawString(ch, x, y, sty.font, p)
                    x += sty.w(ch)
            else:
                ci.drawString(txt, x, y, sty.font, p)
        elif t == "rule":
            _, x0, y0, x1, y1, th, col = op
            p.setColor(skia.Color(*col))
            p.setStrokeWidth(th)
            ci.drawLine(x0, y0, x1, y1, p)
        elif t == "rect":
            _, x, y, w, h, col = op
            p.setColor(skia.Color(*col))
            ci.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)
        elif t == "image":
            _, x, y, w, h, seed, tone = op
            img = skia.Image.fromarray(photo(seed, w, h, tone))
            ci.drawImageRect(img, skia.Rect.MakeXYWH(x, y, w, h))
    # highlight: marker box with slightly uneven corners
    a, b, base, sty = kw
    sz = sty.size
    top = base - sty.cap - 0.2 * sz
    bot = base + (0.26 if any(ch in "pgjqy" for ch in KW) and sty.case != "upper" else 0.17) * sz
    padx = 0.12 * sz
    j = lambda: random.uniform(-0.03, 0.03) * (bot - top)
    path = skia.Path()
    path.moveTo(a - padx + j(), top + j())
    path.lineTo(b + padx + j(), top + j())
    path.lineTo(b + padx + j(), bot + j())
    path.lineTo(a - padx + j(), bot + j())
    path.close()
    hp = skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255))
    s_hl.getCanvas().drawPath(path, hp)
    ink = s_ink.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
    hl = s_hl.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
    return ink.astype(np.float32) / 255, hl[..., 3].astype(np.float32) / 255


def up(a):
    """Layout-resolution field -> output resolution."""
    return a if (W, H) == (PW, PH) else cv2.resize(a, (PW, PH), interpolation=cv2.INTER_LINEAR)


def lowfreq(rng, cells, sigma_frac=0.0):
    n = rng.random((cells, max(2, int(cells * W / H)))).astype(np.float32)
    return cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)


def paper(kind, rng):
    if kind == "web":
        return np.ones((H, W, 3), np.float32) * np.array([1.0, 1.0, 0.995]), 0.0
    if kind == "webdark":
        return np.ones((H, W, 3), np.float32) * np.array([0.075, 0.075, 0.085]), 0.0
    base = {"news": [0.905, 0.885, 0.84], "mag": [0.965, 0.955, 0.94], "memo": [0.94, 0.925, 0.88]}[kind]
    base = np.array(base, np.float32) * rng.uniform(0.97, 1.02)
    mott = (lowfreq(rng, 6) - 0.5) * 0.05 + (lowfreq(rng, 40) - 0.5) * 0.025
    fib = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 0.8) * (0.03 if kind == "news" else 0.015)
    lum = 1 + mott + fib
    return np.clip(base[None, None] * lum[..., None], 0, 1), 1.0


def lighting(kind, rng):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    if kind in ("web", "webdark"):
        return np.ones((H, W), np.float32)
    ang = rng.uniform(0, 2 * math.pi)
    d = ((xx - W / 2) * math.cos(ang) + (yy - H / 2) * math.sin(ang)) / max(W, H)
    L = 1 + d * rng.uniform(0.06, 0.14)
    rr = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    L *= 1 - rng.uniform(0.08, 0.16) * np.clip(rr / 1.414, 0, 1) ** 2
    # creases: fold shading + thin ridge highlight/shadow
    n = {"news": rng.integers(3, 8), "mag": rng.integers(0, 2), "memo": rng.integers(1, 4)}[kind]
    for _ in range(n):
        px, py = rng.uniform(0, W), rng.uniform(0, H)
        th = rng.uniform(0, math.pi)
        dist = (xx - px) * math.sin(th) - (yy - py) * math.cos(th)
        amp = rng.uniform(0.01, 0.035)
        L *= 1 + amp * np.tanh(dist / rng.uniform(20, 120)) + 0.05 * np.exp(-(dist / 1.6) ** 2) - 0.06 * np.exp(-((dist - 3) / 2.2) ** 2)
    if kind == "mag":  # soft gloss sheen
        th = rng.uniform(0, math.pi)
        dist = (xx - W * rng.uniform(0.2, 0.8)) * math.sin(th) - (yy - H * 0.5) * math.cos(th)
        L += 0.05 * np.exp(-(dist / (0.18 * max(W, H))) ** 2)
    return L


def render_card(kind, seed):
    r = random.Random(seed)
    random.seed(seed)
    rng = np.random.default_rng(seed)
    c = card(kind, r)
    ops, kw, kc = build_page(c, r)
    ink, hla = draw(ops, kw, kc, c["rot"], c["ink"])
    bg, texture = paper(c["bg"], rng)
    bg = up(bg)
    web = c["bg"] in ("web", "webdark")
    # marker: stroke streaks along the box + slight transparency
    hl_col = np.array([1.0, 0.89, 0.30] if web else [0.98, 0.86, 0.36], np.float32)
    if not web:
        streak = cv2.resize(rng.random((max(2, H // 6), 6)).astype(np.float32), (PW, PH), interpolation=cv2.INTER_LINEAR)
        hla = hla * (0.86 + 0.12 * streak)
        hla = cv2.GaussianBlur(hla, (0, 0), 0.8 * S)
    out = bg * (1 - hla[..., None]) + hl_col * hla[..., None]
    if c["bg"] == "webdark":
        out = bg * (1 - hla[..., None]) + hl_col * hla[..., None]
    rgb, a = ink[..., :3], ink[..., 3]
    if not web:
        m = 0.8 + 0.2 * np.clip(lowfreq(rng, 220) * 0.6 + rng.random((H, W)).astype(np.float32) * 0.4, 0, 1)
        if c["bg"] == "memo":
            m = 0.62 + 0.38 * lowfreq(rng, 160)
        m = up(m)
        rgb, a = rgb * m[..., None], a * m
        rgb = cv2.GaussianBlur(rgb, (0, 0), 0.6 * S)
        a = cv2.GaussianBlur(a, (0, 0), 0.6 * S)
    # keyword text on dark web pages reads black on the yellow marker
    if c["bg"] == "webdark":
        on = hla > 0.5
        rgb = np.where(on[..., None], (a[..., None] * np.array([0.05, 0.05, 0.05])).astype(np.float32), rgb)
    out = out * (1 - a[..., None]) + rgb
    out *= up(lighting(c["bg"], rng))[..., None]
    if not web:
        # photographic grade: lift blacks a touch, warm highlights
        out = 0.035 + out * 0.95
    if c["dof"]:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        th = math.radians(c["rot"])
        dy = (-(xx - W / 2) * math.sin(th) + (yy - H / 2) * math.cos(th)) / (H / 2)
        mask = up(np.clip((np.abs(dy) - 0.12) / 0.7, 0, 1) ** 1.5)
        bl = cv2.GaussianBlur(out, (0, 0), c["dof"] * S)
        out = out * (1 - mask[..., None]) + bl * mask[..., None]
    return np.clip(out, 0, 1)


TAB = random.Random(KW).sample(range(len(KW_TABLOID)), 2)
SEQ = ["news_body", "news_body", "news_head", "web_body", "news_body", "magazine", "news_dense", "news_head",
       "web_head", "memo", "news_body", "mag_head", "web_dark", "news_head", "news_dense", "web_body",
       "magazine", "news_body", "web_head", "news_dense", "news_head", "tabloid", "tabloid"]


BT709 = np.array([[0.2126, 0.7152, 0.0722], [-0.1146, -0.3854, 0.5], [0.5, -0.4542, -0.0458]], np.float32)


def to_yuv709(rgb):
    """RGB uint8 -> (limited-range luma as float32, packed 4:2:0 chroma planes as bytes)."""
    yuv = cv2.transform(rgb.astype(np.float32), BT709)
    y = 16 + yuv[..., 0] * (219 / 255)
    c = cv2.resize(yuv[..., 1:], (PW // 2, PH // 2), interpolation=cv2.INTER_AREA) * (224 / 255) + 128
    c = np.clip(c + 0.5, 0, 255).astype(np.uint8)
    return y, c[..., 0].tobytes() + c[..., 1].tobytes()


def encoder(ff):
    """Apple's hardware H.264 encoder when it can run constant-quality mode (about 10x faster at 4K and
    slightly higher PSNR than x264 here), otherwise x264. Web mode is a fixed 60 Mb/s: 3 s at 4K60 is
    about 24 MB and still visually transparent (44 dB PSNR against the full-size encode)."""
    if WEB:
        return ["-c:v", "libx264", "-preset", "veryfast", "-b:v", "60M", "-maxrate", "60M", "-bufsize", "60M"]
    vt = ["-c:v", "h264_videotoolbox", "-q:v", "80"]
    ok = subprocess.run([ff, "-v", "error", "-f", "lavfi", "-i", "color=s=640x360:d=0.2", *vt, "-f", "null", "-"],
                        capture_output=True).returncode == 0
    return vt if ok else ["-c:v", "libx264", "-preset", "fast", "-crf", "14"]


def main():
    base_seed = zlib.crc32(KW.encode()) % 100000
    cards = []
    for i, kind in enumerate(SEQ):
        img = (render_card(kind, base_seed + i * 17) * 255 + 0.5).astype(np.uint8)
        cards.append(img)
        if CARDS_DIR:
            os.makedirs(CARDS_DIR, exist_ok=True)
            cv2.imwrite(os.path.join(CARDS_DIR, "%02d_%s.png" % (i, kind)), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        print("card", i, kind, flush=True)
    starts = [i * CARD_T for i in range(len(cards))] + [(len(cards) - 1) * CARD_T + LAST_T]
    bounds = [int(t * FPS + 0.5) for t in starts]
    audio = []
    if SOUND:
        from sound import write_rattle
        wav = os.path.join(tempfile.mkdtemp(), "rattle.wav")
        write_rattle(wav, bounds[-1] / FPS, base_seed)
        audio = ["-i", wav]
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709",
           "-s", f"{PW}x{PH}", "-r", str(FPS), "-i", "-", *audio,
           *encoder(ff), "-profile:v", "high",
           "-bsf:v", "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1",
           *(["-c:a", "aac", "-b:a", "256k"] if audio else []),
           "-movflags", "+faststart", OUT]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    grng = np.random.default_rng(7)
    # film grain: sigma 0.022 at 1080, blur scaled with S and amplitude matched so it reads the same at 4K.
    # The grain is grey, so in BT.709 it moves only luma: each card is converted to YUV once and
    # each frame only adds fresh grain to Y.
    probe = lambda sig: cv2.GaussianBlur(np.random.default_rng(0).standard_normal((512, 512), np.float32), (0, 0), sig).std()
    amp = 0.022 * 219 * probe(0.7) / probe(0.7 * S)
    for i, img in enumerate(cards):
        y, uv = to_yuv709(img)
        for f in range(bounds[i + 1] - bounds[i]):
            g = cv2.GaussianBlur(grng.standard_normal((PH, PW), np.float32), (0, 0), 0.7 * S)
            pr.stdin.write(np.clip(y + g * amp + 0.5, 16, 235).astype(np.uint8).tobytes() + uv)
    pr.stdin.close()
    sys.exit(pr.wait())


main()
