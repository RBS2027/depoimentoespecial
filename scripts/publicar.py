# -*- coding: utf-8 -*-
"""Publica o próximo artigo da _fila no /blog, atualiza a lista e o sitemap."""
import os, json, shutil, glob
from datetime import datetime, timezone, timedelta

DOM = "https://depoimentoespecial.com.br"
BASE = ["/", "/o-que-e-depoimento-especial/", "/assistente-tecnico/",
        "/analise-de-entrevista-forense/", "/blog/", "/quem-sou/", "/contato/"]
MESES = ["janeiro","fevereiro","março","abril","maio","junho","julho",
         "agosto","setembro","outubro","novembro","dezembro"]

fila = sorted(glob.glob("_fila/*/"))
if not fila:
    print("Fila vazia — nada a publicar.")
    raise SystemExit(0)

agora = datetime.now(timezone(timedelta(hours=-3)))  # América/São_Paulo
data_ext = f"{agora.day} de {MESES[agora.month-1]} de {agora.year}"
data_iso = agora.strftime("%Y-%m-%d")

src = fila[0]
meta = json.load(open(src+"meta.json", encoding="utf-8"))
slug = meta["slug"]

html = open(src+"index.html", encoding="utf-8").read()
html = html.replace("{{DATA}}", data_ext).replace("{{DATA_ISO}}", data_iso)
dst = f"blog/{slug}"
os.makedirs(dst, exist_ok=True)
open(dst+"/index.html","w",encoding="utf-8").write(html)
shutil.rmtree(src)

posts = json.load(open("blog/posts.json", encoding="utf-8"))
posts.insert(0, {"slug":slug, "h1":meta["h1"], "desc":meta["desc"],
                 "data":data_ext, "iso":data_iso})
json.dump(posts, open("blog/posts.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

itens = "\n".join(
    f'<div class="post-item"><span class="data">{p["data"]}</span>'
    f'<h3><a href="/blog/{p["slug"]}/">{p["h1"]}</a></h3>'
    f'<p>{p["desc"]}</p></div>' for p in posts)
idx = open("blog/index.html", encoding="utf-8").read()
ini, fim = idx.index("<!--POSTS-->"), idx.index("<!--/POSTS-->")
idx = idx[:ini] + "<!--POSTS-->\n" + itens + "\n" + idx[fim:]
open("blog/index.html","w",encoding="utf-8").write(idx)

with open("sitemap.xml","w",encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in BASE:
        f.write(f"  <url><loc>{DOM}{u}</loc></url>\n")
    for p in posts:
        f.write(f"  <url><loc>{DOM}/blog/{p['slug']}/</loc><lastmod>{p['iso']}</lastmod></url>\n")
    f.write("</urlset>\n")

print("Publicado:", slug, "em", data_ext, "| restam na fila:", len(fila)-1)
