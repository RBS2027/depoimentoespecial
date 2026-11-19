#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Páginas-guia por tema (/temas/ e /temas/<tema>/) e o link "Tema deste artigo" em cada artigo do /blog.
Roda dentro de publicar.py, depois do sitemap; é idempotente. Usa /blog/ como modelo de página."""
import re, os, html, glob, json, datetime
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(REPO)
DOM = re.search(r'<link rel="canonical" href="https://([^/]+)/', open('index.html', encoding='utf-8').read()).group(1)
HOJE = datetime.date.today().isoformat()
MARCA = {'robisonsouza.com.br': 'Robison Souza', 'peritoempsicologiaforense.com.br': 'Perito Forense', 'depoimentoespecial.com.br': 'Depoimento Especial', 'estudopsicossocial.com.br': 'Estudo Psicossocial'}.get(DOM, 'Robison Souza')
def tit(x):
    return x + ' | ' + MARCA if len(x + ' | ' + MARCA) <= 65 else x
VICIOS = r'laudo|parecer|v[ií]cio|impugna|nulidade|vi[eé]s|jarg[aã]o|terminologia|cita[cç][aã]o incorreta|conclus[aã]o gen[eé]rica|extrapola|instrumento inadequado|data retroativa|compara[cç][aã]o indevida|baseado apenas|desfavor[aá]vel|contestar|contradi[cç]|cust[oó]dia|sintomas'
if 'depoimento' in DOM:
    ASSUNTO = 'depoimento especial'
    TEMAS = [
     ('por-estado', 'Atuação por estado', r'^assistente t[eé]cnico em depoimento especial (em|na|no) |atua[cç][aã]o nacional', 'Páginas sobre a assistência técnica em depoimento especial em cada estado, com a norma local de cada Tribunal de Justiça.'),
     ('quesitos', 'Quesitos', r'quesito', 'Artigos sobre como formular quesitos em depoimento especial e os erros que comprometem a análise técnica.'),
     ('laudos-e-vicios', 'Vícios, nulidades e impugnação', VICIOS, 'Artigos sobre os vícios técnicos que aparecem no depoimento especial e nos documentos que o analisam, e como levá-los ao processo.'),
     ('memoria-e-relato', 'Memória, relato e sugestão', r'mem[oó]ria|relato|retrata|revela[cç][aã]o|sugestiv|coaching|sil[eê]ncio|grava[cç][aã]o caseira|lealdade', 'Artigos sobre memória infantil, falsas memórias, perguntas sugestivas, retratação e as condições de produção do relato.'),
     ('vara-de-familia', 'Depoimento especial na vara de família', r'guarda|fam[ií]lia|ado[cç][aã]o|paternidade|visitas|tutela|curatela|interdi[cç][aã]o|sobrenome|emancipa|netos|multiparent|aliena[cç][aã]o|acordo|reten[cç][aã]o|consentimento|genitor', 'Artigos sobre o depoimento especial em ações de família: guarda, convivência, adoção, tutela e curatela.'),
     ('processo-penal-e-prova', 'Processo penal e prova', r'penal|crim|habeas|prova|investiga|testemunha|oitiva|juiz|audi[eê]ncia', 'Artigos sobre o depoimento especial no processo penal: audiência, prova, nova oitiva e revisão criminal.'),
    ]
    RESTO = ('lei-e-protocolo', 'Lei, protocolo e prática', None, 'Artigos sobre a Lei 13.431/2017, os protocolos de entrevista forense e a prática do depoimento especial.')
else:
    ASSUNTO = 'estudo psicossocial'
    TEMAS = [
     ('por-estado', 'Atuação por estado', r'^assistente t[eé]cnico em estudo psicossocial (em|na|no) |atua[cç][aã]o nacional', 'Páginas sobre a assistência técnica em estudo psicossocial em cada estado, com a estrutura local de cada Tribunal de Justiça.'),
     ('quesitos', 'Quesitos', r'quesito', 'Artigos sobre como formular quesitos no estudo psicossocial e os erros que comprometem a avaliação.'),
     ('laudo-e-impugnacao', 'Laudo, vícios e impugnação', VICIOS + r'|contra-?laudo', 'Artigos sobre os vícios técnicos do relatório psicossocial, o contralaudo e os prazos para contestar.'),
     ('guarda-e-convivencia', 'Guarda e convivência', r'guarda|conviv[eê]ncia|visita|filho|genitor|av[oó]s|irm[aã]os|mudan[cç]a de cidade|companheiro|aliena[cç][aã]o|lealdade|abandono|medida protetiva|falsas acusa', 'Artigos sobre guarda, convivência, alienação parental e os conflitos de família avaliados no estudo psicossocial.'),
     ('outras-acoes', 'Adoção, tutela e outras ações', r'ado[cç][aã]o|tutela|curatela|alimentos|sucess[oó]rio|possess[oó]ria|emancipa|sobrenome|paternidade|socioeducativa|imputabilidade|crimin|crimes|c[ií]vel|acordo|consentimento|reten[cç][aã]o', 'Artigos sobre o estudo psicossocial fora da disputa de guarda: adoção, tutela, curatela, alimentos e outras ações.'),
    ]
    RESTO = ('como-funciona', 'Como funciona o estudo psicossocial', None, 'Artigos sobre o que o estudo psicossocial avalia, as etapas, os prazos, a visita domiciliar e como se preparar.')
def artigos():
    A = []
    for f in glob.glob('blog/*/index.html'):
        t = open(f, encoding='utf-8').read()
        if re.search(r'<meta name="robots" content="noindex', t): continue
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S); d = re.search(r'<meta name="description" content="([^"]*)"', t)
        dt = re.search(r'"datePublished"\s*:\s*"([^"]*)"', t)
        if not h1: continue
        A.append({'f': f, 'url': '/' + f[:-10], 'h1': html.unescape(re.sub(r'<[^>]+>', '', h1.group(1)).strip()), 'desc': html.unescape(d.group(1)) if d else '', 'data': dt.group(1) if dt else ''})
    return A
def classifica(A):
    G = {s: [] for s, *_ in TEMAS + [RESTO]}
    for a in A:
        for s, n, pat, _ in TEMAS:
            if re.search(pat, a['h1'], re.I): G[s].append(a); break
        else: G[RESTO[0]].append(a)
    for s, *_ in TEMAS:
        if 0 < len(G[s]) < 4: G[RESTO[0]] += G[s]; G[s] = []
    return {s: sorted(v, key=lambda a: (a['data'], a['h1']), reverse=True) for s, v in G.items() if v}
def pagina(modelo, slug, titulo, h1, desc, corpo, trilha):
    url = f'https://{DOM}/{slug}/'; t = modelo; e = html.escape
    t = re.sub(r'<title>.*?</title>', f'<title>{e(titulo)}</title>', t, count=1, flags=re.S)
    for sel in ('name="description"', 'property="og:description"', 'name="twitter:description"'): t = re.sub(r'(<meta %s content=")[^"]*(")' % sel, lambda m: m.group(1) + e(desc) + m.group(2), t, count=1)
    for sel in ('property="og:title"', 'name="twitter:title"'): t = re.sub(r'(<meta %s content=")[^"]*(")' % sel, lambda m: m.group(1) + e(titulo) + m.group(2), t, count=1)
    t = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), t, count=1)
    t = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), t, count=1)
    t = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\s*', '', t)
    lds = [json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": h1, "description": desc, "url": url, "inLanguage": "pt-BR", "dateModified": HOJE}, ensure_ascii=False),
           json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": f'https://{DOM}{u}'} for i, (n, u) in enumerate(trilha)]}, ensure_ascii=False)]
    t = re.sub(r'<script type="application/ld\+json"[^>]*>.*?</script>\s*', '', t, flags=re.S)
    t = t.replace('</head>', ''.join(f'<script type="application/ld+json">{x}</script>\n' for x in lds) + '</head>', 1)
    m = re.search(r'<article(?: class="prose larga")?>', t); i = m.start(); j = t.find('</article>', i); assert 0 < i < j
    rot = '<span class="eyebrow">Guia por tema</span>' if 'prose' in m.group(0) else '<p class="breadcrumb">Guia por tema</p>'
    t = t[:i] + m.group(0) + '\n' + rot + '\n<h1>' + e(h1) + '</h1>\n' + corpo + '\n' + t[j:]
    t = re.sub(r'<script>(?:(?!</script>).)*busca-blog(?:(?!</script>).)*</script>\s*', '', t, flags=re.S)
    os.makedirs(slug, exist_ok=True); open(f'{slug}/index.html', 'w', encoding='utf-8').write(t)
if 'depoimento' in DOM:
    TERMOS = [(r'quesitos', 'quesitos'), (r'falsas memórias', 'memoria-e-relato'), (r'perguntas sugestivas', 'memoria-e-relato'), (r'nulidades?', 'laudos-e-vicios'),
              (r'revisão criminal', 'processo-penal-e-prova'), (r'disputas? de guarda', 'vara-de-familia'), (r'Protocolo NICHD', 'lei-e-protocolo')]
else:
    TERMOS = [(r'quesitos', 'quesitos'), (r'contralaudo', 'laudo-e-impugnacao'), (r'impugnação', 'laudo-e-impugnacao'), (r'guarda compartilhada', 'guarda-e-convivencia'),
              (r'adoção', 'outras-acoes'), (r'visita domiciliar', 'como-funciona')]
def links_no_texto(G, termos, abre):
    """Liga, no corpo de cada artigo, a 1ª menção a outro tema à página-guia dele (máx. 2 por artigo). Idempotente."""
    n = 0
    for s, itens in G.items():
        for a in itens:
            t = open(a['f'], encoding='utf-8').read(); t0 = t
            t = re.sub(r'<a class="tema-lk" href="[^"]*">(.*?)</a>', r'\1', t, flags=re.S)
            i = t.find(abre); j = t.find('<p class="rede27-tema">')
            if i < 0 or j < i:
                if t != t0: open(a['f'], 'w', encoding='utf-8').write(t)
                continue
            corpo = t[i:j]; feitos = set()
            def troca_p(m):
                p = m.group(0)
                if len(feitos) >= 2 or '<a ' in p or re.search(r'seu processo tem|seu e-mail|100% online|WhatsApp|marque uma consulta|entre em contato|artigo t[eé]cnico por dia', p, re.I): return p
                partes = re.split(r'(<[^>]+>)', p)
                for k, seg in enumerate(partes):
                    if seg.startswith('<') or len(feitos) >= 2: continue
                    for pat, alvo in termos:
                        if alvo == s or alvo in feitos or alvo not in G: continue
                        mm = re.search(r'(?<![\wÀ-ÿ-])(' + pat + r')(?![\wÀ-ÿ-])', seg, re.I)
                        if mm:
                            seg = seg[:mm.start()] + f'<a class="tema-lk" href="/temas/{alvo}/">' + mm.group(1) + '</a>' + seg[mm.end():]
                            feitos.add(alvo); break
                    partes[k] = seg
                    if '<a class="tema-lk"' in seg: break
                return ''.join(partes)
            corpo = re.sub(r'<p>(?:(?!</p>).)*</p>', troca_p, corpo, flags=re.S)
            t = t[:i] + corpo + t[j:]
            if t != t0: open(a['f'], 'w', encoding='utf-8').write(t)
            n += len(feitos)
    return n
def main():
    modelo = open('blog/index.html', encoding='utf-8').read()
    A = artigos(); G = classifica(A); NOME = {s: (n, intro) for s, n, _, intro in TEMAS + [RESTO]}
    e = html.escape
    for s, itens in G.items():
        n, intro = NOME[s]
        cards = '\n'.join(f'<div class="post-item"><h3><a href="{a["url"]}">{e(a["h1"])}</a></h3><p>{e(a["desc"])}</p></div>' for a in itens)
        outros = ' · '.join(f'<a href="/temas/{x}/">{e(NOME[x][0])}</a>' for x in G if x != s)
        corpo = (f'<p>{e(intro)} São {len(itens)} artigos, do mais recente para o mais antigo.</p>\n{cards}\n'
                 f'<h2 id="outros-temas">Outros temas</h2>\n<p>{outros} · <a href="/temas/">todos os temas</a> · <a href="/blog/">blog completo</a></p>')
        pagina(modelo, f'temas/{s}', tit(f'{n}: {len(itens)} artigos'), f'{n}: todos os artigos', (f'{len(itens)} artigos reunidos em uma só página. {intro}'[:152].rsplit(' ', 1)[0]).rstrip('.,:;') + '.', corpo, [('Início', '/'), ('Temas', '/temas/'), (n, f'/temas/{s}/')])
    lista = '\n'.join(f'<div class="post-item tema-item"><h3><a href="/temas/{s}/">{e(NOME[s][0])}</a></h3><p>{len(v)} artigos. {e(NOME[s][1])}</p></div>' for s, v in G.items())
    pagina(modelo, 'temas', tit('Artigos organizados por tema'), 'Todos os artigos, organizados por tema', f'Os {len(A)} artigos deste site sobre {ASSUNTO}, reunidos em {len(G)} temas para facilitar a leitura.',
           f'<p>Este site reúne {len(A)} artigos técnicos sobre {ASSUNTO}. Para facilitar a leitura, eles estão agrupados em {len(G)} temas. Escolha o que tem relação com o seu processo.</p>\n{lista}\n<p><a href="/blog/">Ver o blog completo, por data</a></p>', [('Início', '/'), ('Temas', '/temas/')])
    n_art = 0
    for s, itens in G.items():
        marca = f'<p class="rede27-tema">Tema deste artigo: <a href="/temas/{s}/">{e(NOME[s][0])} — ver todos os artigos</a></p>'
        for a in itens:
            t = open(a['f'], encoding='utf-8').read(); t0 = t
            t = re.sub(r'<p class="rede27-tema">.*?</p>', '', t, flags=re.S)
            k = t.find('<h2 class="rede27-h"')
            if k < 0: continue
            t = t[:k] + marca + t[k:]
            if t != t0: open(a['f'], 'w', encoding='utf-8').write(t); n_art += 1
    n_lk = links_no_texto(G, TERMOS, '<article class="prose">')
    sm = open('sitemap.xml', encoding='utf-8').read()
    for u in ['temas'] + [f'temas/{s}' for s in G]:
        loc = f'https://{DOM}/{u}/'
        if loc not in sm: sm = sm.replace('</urlset>', f'<url><loc>{loc}</loc><lastmod>{HOJE}</lastmod></url>\n</urlset>')
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
    print('temas:', {s: len(v) for s, v in G.items()}, '| artigos com link de tema atualizado:', n_art, '| links no texto:', n_lk)
if __name__ == '__main__': main()
