#!/usr/bin/env python3
# Revisão diária automática — depoimentoespecial.com.br
import glob, re, json, os, sys
err=[]
G=sorted(glob.glob('**/*.html', recursive=True))
G=[p for p in G if not p.startswith('.github')]
# 1) CSS: versão única e chaves balanceadas
css=open('assets/style.css').read()
if css.count('{')!=css.count('}'): err.append('CSS com chaves desbalanceadas')
vs=set()
for p in G: vs.update(re.findall(r'style\.css\?v=(\d+)', open(p,encoding='utf-8').read()))
if len(vs)>1: err.append(f'CSS com versões mistas: {sorted(vs)}')
# 2) endereço e titulação
for p in G:
    t=open(p,encoding='utf-8').read()
    if '01310-905' in t or 'Paulista, 352' in t: err.append(f'ENDEREÇO ANTIGO em {p}')
    if 'Psicólogo Jurídico' in t: err.append(f'titulação vedada em {p}')
# 3) JSON-LD válido
for p in G:
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', open(p,encoding='utf-8').read(), re.S):
        try: json.loads(m.group(1))
        except Exception: err.append(f'JSON-LD inválido em {p}')
# 4) menus idênticos
ESP=['Início','O que é','Assistente Técnico','Depoimento Especial','Consultoria','Blog','Quem Sou','Contato']
for p in G:
    m=re.search(r'<nav class="main"[^>]*>(.*?)</nav>', open(p,encoding='utf-8').read(), re.S)
    if m and re.findall(r'>([^<]+)</a>', m.group(1))!=ESP: err.append(f'menu divergente em {p}')
# 5) links internos e imagens
slugs={re.sub(r'^\d+-','',d.split('/')[-2]) for d in glob.glob('_fila/*/')}
for p in G:
    t=open(p,encoding='utf-8').read()
    for m in re.finditer(r'(?:href|src|content)="(/assets/[^"?#]+)', t):
        if not os.path.exists(m.group(1)[1:]): err.append(f'{p}: arquivo ausente {m.group(1)}')
    for m in re.finditer(r'href="(/blog/([a-z0-9-]+)/)"', t):
        if not (os.path.isdir('blog/'+m.group(2)) or m.group(2) in slugs): err.append(f'{p}: link {m.group(1)}')
# 6) fila alimentada (alerta com 5 dias de antecedência do fim)
import datetime
falta = len(glob.glob('_fila/*/')) - (datetime.date.today() - datetime.date(2026,8,10)).days
if falta <= 5: err.append(f'FILA ACABANDO: restam ~{falta} artigos agendados — produzir novo lote')
# resultado
err=sorted(set(err))
print(f'Revisão diária: {len(G)} páginas verificadas')
if err:
    print(f'\n{len(err)} PROBLEMA(S):')
    for e in err[:30]: print(' -', e)
    resumo = ' | '.join(err[:3]) + (f' | e mais {len(err)-3}...' if len(err)>3 else '')
    print(f"::error title=REVISÃO DO SITE REPROVOU — {len(err)} problema(s)::{resumo}")
    sys.exit(1)
print('Tudo OK ✅')
