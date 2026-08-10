<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="UTF-8"/>
<xsl:template match="/rss/channel">
<html lang="pt-BR"><head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title><xsl:value-of select="title"/></title>
<style>
body{background:#0E2721;color:#F5F4EF;font-family:Georgia,serif;line-height:1.7;margin:0;padding:2rem 1.25rem}
.wrap{max-width:46rem;margin:0 auto}
h1{color:#C9A227;font-family:Arial,sans-serif;font-size:1.6rem}
.aviso{border:1px solid rgba(201,162,39,.4);border-left:3px solid #C9A227;border-radius:10px;padding:.9rem 1.1rem;background:rgba(14,36,48,.5);font-size:.9rem;margin:1.25rem 0 2rem}
.item{border:1px solid rgba(201,162,39,.35);border-left:2px solid #C9A227;border-radius:12px;padding:1.1rem 1.4rem;margin-bottom:1rem;background:rgba(14,36,48,.35)}
.item a{color:#C9A227;text-decoration:none;font-family:Arial,sans-serif;font-weight:bold;font-size:1.05rem}
.data{color:rgba(245,244,239,.7);font-size:.78rem;font-family:Arial,sans-serif;text-transform:uppercase;letter-spacing:.08em}
p{margin:.4rem 0 0}
.voltar{color:#C9A227}
</style></head>
<body><div class="wrap">
<h1><xsl:value-of select="title"/></h1>
<div class="aviso">Este é o <strong>feed RSS</strong> do blog — um formato para receber os artigos automaticamente em aplicativos leitores (Feedly, Inoreader e outros): basta colar o endereço desta página no aplicativo. Para leitura normal, <a class="voltar" href="/blog/">acesse o blog</a>.</div>
<xsl:for-each select="item">
<div class="item">
<span class="data"><xsl:value-of select="substring(pubDate,9,2)"/>/<xsl:value-of select="substring(pubDate,6,2)"/>/<xsl:value-of select="substring(pubDate,1,4)"/></span><br/>
<a><xsl:attribute name="href"><xsl:value-of select="link"/></xsl:attribute><xsl:value-of select="title"/></a>
<p><xsl:value-of select="description"/></p>
</div>
</xsl:for-each>
</div></body></html>
</xsl:template>
</xsl:stylesheet>
