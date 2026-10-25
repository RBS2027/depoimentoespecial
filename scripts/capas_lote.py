# -*- coding: utf-8 -*-
"""Gera capa própria (hero 1200x450 webp + og 1200x630 jpg) para todo artigo de portal sem capa dedicada."""
import re, glob, os, sys, html, textwrap, collections
from PIL import Image, ImageDraw, ImageFont
SITE, DOM = sys.argv[1], sys.argv[2]
os.chdir(SITE)
st = collections.Counter()
_f = {}
def font(n, s):
    k = (n, s)
    if k not in _f:
        f = ImageFont.truetype(f"/home/claude/fonts/{n}.ttf", s)
        try: f.set_variation_by_axes([600 if n == "fraunces" else 700])
        except Exception: pass
        _f[k] = f
    return _f[k]
LOGO = Image.open("assets/img/logo-h-dark.webp").convert("RGBA")
def capa(title, label, size, out, fmt, q):
    W, Hh = size
    im = Image.new("RGB", size, "#F3EEE7"); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 14], fill="#A66F3E"); d.rectangle([0, Hh-14, W, Hh], fill="#4E4035")
    d.rectangle([0, 14, W, int(Hh*0.22)], fill="#E6D9CA")
    lw = int(W*0.27); lh = int(LOGO.height*lw/LOGO.width); lg = LOGO.resize((lw, lh))
    im.paste(lg, (W-lw-56, int(Hh*0.11)-lh//2+7), lg)
    d.text((60, int(Hh*0.08)), label.upper()[:48], font=font("montserrat", int(Hh*0.045)), fill="#A66F3E")
    fs = int(Hh*0.095); lines = textwrap.wrap(title, width=40)
    while len(lines) > 4 and fs > int(Hh*0.065):
        fs -= 4; lines = textwrap.wrap(title, width=int(40*int(Hh*0.095)/fs))
    if len(lines) <= 2:
        fs = int(Hh*0.125); lines = textwrap.wrap(title, width=30)
    f2 = font("fraunces", fs); y = int(Hh*0.30); step = int(fs*1.22)
    for ln in lines[:5]:
        d.text((60, y), ln, font=f2, fill="#3B3028"); y += step
    d.text((60, Hh-14-int(Hh*0.11)), f"{DOM}  ·  Perito em Psicologia Forense", font=font("montserrat", int(Hh*0.04)), fill="#69594D")
    im.save(out, fmt, quality=q)

HERO = '<a href="https://wa.me/5512997402674?text=Ol%C3%A1!%20Vim%20pelo%20site%20{dom}%20e%20quero%20falar%20sobre%20o%20meu%20caso." target="_blank" rel="noopener" aria-label="Falar no WhatsApp com Robison Souza" title="Fale comigo no WhatsApp"><img class="art-hero" fetchpriority="high" src="/assets/img/blog/{slug}.webp" alt="{alt}" width="1200" height="460" loading="eager"></a>'

for p in sorted(glob.glob("blog/*/index.html") + glob.glob("_fila/*/index.html")):
    s = open(p, encoding="utf-8").read(); o = s
    m = re.search(r"<h1>(.*?)</h1>", s, flags=re.S)
    if not m: continue
    h1 = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    slug = p.split("/")[1] if p.startswith("blog/") else None
    if slug is None:
        mm = re.search(r'<link rel="canonical" href="[^"]*/blog/([^/"]+)/"', s)
        slug = mm.group(1) if mm else re.sub(r"^\d+-", "", p.split("/")[1])
    lab = re.search(r'<span class="eyebrow">(.*?)</span>', s)
    label = html.unescape(re.sub(r"<[^>]+>", "", lab.group(1))).replace("Blog ·", "").strip() if lab else "Artigo técnico"
    dedicated = f'src="/assets/img/blog/{slug}.webp"' in s
    hero_path = f"assets/img/blog/{slug}.webp"; og_path = f"assets/img/og/{slug}.jpg"
    if True:
        capa(h1, label, (1200, 450), hero_path, "WEBP", 82)
        capa(h1, label, (1200, 630), og_path, "JPEG", 72); st["capas"] += 1
    alt = html.escape(h1, quote=True)
    if 'class="art-hero"' in s:
        s = re.sub(r'(<img class="art-hero"[^>]*src=")[^"]*(")', rf'\g<1>/assets/img/blog/{slug}.webp\2', s, count=1)
    else:
        s = re.sub(r'(<p class="byline">.*?</p>)', lambda mm: mm.group(1) + "\n" + HERO.format(dom=DOM, slug=slug, alt=alt), s, count=1, flags=re.S); st["hero-inserido"] += 1
    s = re.sub(r'<link rel="preload" as="image" href="[^"]*"', f'<link rel="preload" as="image" href="/assets/img/blog/{slug}.webp"', s, count=1)
    if 'rel="preload" as="image"' not in s:
        s = s.replace("</head>", f'<link rel="preload" as="image" href="/assets/img/blog/{slug}.webp" fetchpriority="high">\n</head>', 1)
    s = re.sub(r'<meta property="og:image" content="[^"]*"', f'<meta property="og:image" content="https://{DOM}/assets/img/og/{slug}.jpg"', s, count=1)
    s = re.sub(r'"image": \["https://[^"]*"\]', f'"image": ["https://{DOM}/assets/img/og/{slug}.jpg"]', s, count=1)
    if s != o: open(p, "w", encoding="utf-8").write(s); st["html"] += 1
print(SITE, dict(st))
