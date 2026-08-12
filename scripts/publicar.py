# -*- coding: utf-8 -*-
"""Publica o próximo artigo da _fila no /blog, atualiza a lista e o sitemap."""
import os, json, shutil, glob
import sys as _sys
def _erro_claro(tipo, valor, tb):
    causa = f"{tipo.__name__}: {valor}"
    dica = ""
    s = str(valor)
    if "meta.json" in s: dica = " — uma pasta da _fila está sem o meta.json; recrie o arquivo ou remova a pasta."
    elif "posts.json" in s: dica = " — blog/posts.json ausente ou corrompido."
    elif "index.html" in s: dica = " — index.html ausente na pasta indicada."
    print(f"::error title=ROBÔ DE PUBLICAÇÃO FALHOU — artigo do dia NÃO saiu::{causa}{dica} O site continua no ar; só a publicação de hoje travou.")
    _sys.__excepthook__(tipo, valor, tb)
_sys.excepthook = _erro_claro
from datetime import datetime, timezone, timedelta

DOM = "https://depoimentoespecial.com.br"
BASE = ["/", "/o-que-e-depoimento-especial/", "/assistente-tecnico/", "/escuta-especializada/", "/glossario/",
        "/analise-de-entrevista-forense/", "/consultoria/", "/politica-de-privacidade/", "/perguntas-frequentes/",
        "/preciso-de-assistente-tecnico/", "/livro/", "/blog/", "/quem-sou/", "/contato/"]
MESES = ["janeiro","fevereiro","março","abril","maio","junho","julho",
         "agosto","setembro","outubro","novembro","dezembro"]

fila = sorted(glob.glob("_fila/*/"))
if not fila:
    print("Fila vazia — nada a publicar.")
    raise SystemExit(0)

agora = datetime.now(timezone(timedelta(hours=-3)))  # América/São_Paulo
data_ext = f"{agora.day} de {MESES[agora.month-1]} de {agora.year}"
data_iso = agora.strftime("%Y-%m-%d")

posts_prev = json.load(open("blog/posts.json", encoding="utf-8"))
ja = {p["slug"] for p in posts_prev}
src = None
for cand in fila:
    m = json.load(open(cand+"meta.json", encoding="utf-8"))
    if m["slug"] in ja:
        shutil.rmtree(cand)  # já publicado: limpa e segue
        continue
    src, meta, slug = cand, m, m["slug"]
    break
if src is None:
    print("Fila sem itens inéditos — nada a publicar.")
    raise SystemExit(0)

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

itens = "".join(f"""
  <item>
    <title>{p['h1']}</title>
    <link>https://depoimentoespecial.com.br/blog/{p['slug']}/</link>
    <guid>https://depoimentoespecial.com.br/blog/{p['slug']}/</guid>
    <pubDate>{p['iso']}T07:00:00-03:00</pubDate>
    <description>{p['desc']}</description>
  </item>""" for p in posts)
open("blog/feed.xml","w",encoding="utf-8").write(f"""<?xml version='1.0' encoding='UTF-8'?>\n<?xml-stylesheet type="text/xsl" href="/blog/feed.xsl"?>
<rss version='2.0'><channel>
  <title>Blog Depoimento Especial — Robison Souza</title>
  <link>https://depoimentoespecial.com.br/blog/</link>
  <description>Artigos técnicos diários sobre depoimento especial, entrevista forense e a Lei 13.431/2017.</description>
  <language>pt-BR</language>{itens}
</channel></rss>""")

with open("sitemap.xml","w",encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in BASE:
        f.write(f"  <url><loc>{DOM}{u}</loc><lastmod>{data_iso}</lastmod></url>\n")
    for p in posts:
        f.write(f"  <url><loc>{DOM}/blog/{p['slug']}/</loc><lastmod>{p['iso']}</lastmod></url>\n")
    f.write("</urlset>\n")

print("Publicado:", slug, "em", data_ext, "| restam na fila:", len(fila)-1)

# ---- Revisao automatica pos-publicacao (instalada em 11/08/2026) ----
# Roda a bateria de verificacoes do site apos publicar o artigo do dia.
# Se a revisao reprovar: garante o commit/push da publicacao e sinaliza a falha
# (o job termina com erro e o GitHub envia e-mail automatico ao proprietario).
import subprocess, sys
_r = subprocess.run([sys.executable, "scripts/revisao.py"])
if _r.returncode != 0:
    subprocess.run(["git", "config", "user.name", "robo-publicador"])
    subprocess.run(["git", "config", "user.email", "actions@github.com"])
    subprocess.run(["git", "add", "-A"])
    subprocess.run(["git", "commit", "-m", "Publicacao diaria automatica (revisao reprovou o site)"], check=False)
    subprocess.run(["git", "push"], check=False)
    sys.exit(1)
