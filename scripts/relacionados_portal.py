# -*- coding: utf-8 -*-
"""Insere o bloco "Leituras relacionadas" (5 artigos mais parecidos, já publicados) nos artigos
do blog e da fila que ainda não têm. Uso, na raiz do repositório do portal:
    python3 scripts/relacionados_portal.py DOMINIO [--aplicar]
Idempotente: artigo que já tem `rbs-rel-2026` não é alterado."""
import glob, html, math, re, sys, collections, unicodedata

DOM = sys.argv[1]; APLICAR = "--aplicar" in sys.argv
STOP = set("a o e de da do das dos em no na nos nas um uma uns umas para por com sem que se ao aos as os é ser como mais mas ou não nao sua seu suas seus isso este esta esse essa entre sobre quando onde qual quais já ja também tambem pela pelo pelas pelos à às foi são sao tem ter há ha pode podem deve cada só so muito ainda the".split())

def toks(s):
    s = unicodedata.normalize("NFD", html.unescape(s).lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return [w for w in re.findall(r"[a-z]{3,}", s) if w not in STOP]

def carrega(f):
    h = open(f, encoding="utf-8").read()
    m = re.search(r"<article.*?</article>", h, re.S)
    if not m: return None
    art = m.group(0)
    t = re.search(r"<h1[^>]*>(.*?)</h1>", art, re.S)
    if not t: return None
    titulo = re.sub(r"<[^>]+>", "", t.group(1)).strip()
    hs = " ".join(re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<h2[^>]*>(.*?)</h2>", art, re.S))
    corpo = re.sub(r"<[^>]+>", " ", art)
    c = collections.Counter(toks(titulo) * 4 + toks(hs) * 2 + toks(corpo))
    return {"f": f, "h": h, "art": art, "titulo": titulo, "tf": c}

pub = [d for d in (carrega(f) for f in sorted(glob.glob("blog/*/index.html"))) if d]
fila = [d for d in (carrega(f) for f in sorted(glob.glob("_fila/*/index.html"))) if d]
df = collections.Counter()
for d in pub: df.update(d["tf"].keys())
N = len(pub)
def vec(d):
    v = {w: (1 + math.log(n)) * math.log((N + 1) / (df.get(w, 0) + 1)) for w, n in d["tf"].items()}
    nrm = math.sqrt(sum(x * x for x in v.values())) or 1
    return {w: x / nrm for w, x in v.items()}
for d in pub + fila: d["v"] = vec(d)
def slug(f): return f.split("/")[-2]
n = 0
for d in pub + fila:
    if "rede-2027" in d["h"] or "rbs-rel-2026" in d["h"] or 'id="leituras-relacionadas"' in d["h"]: continue
    sims = []
    for o in pub:
        if o["f"] == d["f"] or o["titulo"] == d["titulo"]: continue
        a, b = (d["v"], o["v"]) if len(d["v"]) < len(o["v"]) else (o["v"], d["v"])
        sims.append((sum(x * b.get(w, 0) for w, x in a.items()), o))
    top = [o for s, o in sorted(sims, key=lambda t: -t[0])[:5]]
    if len(top) < 3: continue
    bloco = '<h2 id="leituras-relacionadas">Leituras relacionadas</h2>\n<ul class="rbs-rel-2026">' + "".join(
        '<li><a href="https://%s/blog/%s/">%s</a></li>' % (DOM, slug(o["f"]), html.escape(o["titulo"], quote=False)) for o in top) + "</ul>\n"
    art = d["art"]
    m = re.search(r'<h2[^>]*>\s*Perguntas frequentes', art)
    pos = m.start() if m else art.find('<p class="byline">')
    if pos < 0: continue
    novo = art[:pos] + bloco + art[pos:]
    n += 1
    if APLICAR: open(d["f"], "w", encoding="utf-8").write(d["h"].replace(art, novo))
print(("GRAVADOS" if APLICAR else "SIMULACAO") + ": %d artigos recebem o bloco (publicados %d, fila %d)" % (n, len(pub), len(fila)))
