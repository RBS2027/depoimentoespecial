<?php
// RBS: capa dos artigos clicável -> WhatsApp (colar no WPCode como snippet PHP, ativar em todo o site)
add_filter('post_thumbnail_html', function ($html, $post_id) {
    if (!is_singular('post') || !in_the_loop()) return $html;
    $wa = 'https://wa.me/5512997402674?text=' . rawurlencode('Olá! Vim pelo site ' . parse_url(home_url(), PHP_URL_HOST) . ' e quero falar sobre o meu caso.');
    return '<a href="' . esc_url($wa) . '" target="_blank" rel="noopener" aria-label="Falar no WhatsApp com Robison Souza">' . $html . '</a>';
}, 10, 2);
