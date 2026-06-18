#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_burger.py — syncs burger/side-drawer nav from anymetric.ai to ru.anymetric.ai
Idempotent (skips files already containing MARKER), CRLF-preserving, glob-all-html.
Run from: C:\projects\anymetric-ru\
"""

import glob
import os
import re

MARKER = "<!-- AM-BURGER-2026 -->"
DIR = os.path.dirname(os.path.abspath(__file__))

# ── Burger CSS ────────────────────────────────────────────────────────────────
BURGER_CSS = (
    "/* ═══ SITE-NAV / SIDE DRAWER " + MARKER + " ═══ */\n"
    ":root{--accent-glow:rgba(255,185,76,.12);}\n"
    "nav.site-nav{display:flex;align-items:center;justify-content:space-between;height:64px;padding:0 48px;}\n"
    ".nav-right{display:flex;align-items:center;gap:20px;}\n"
    ".burger{display:flex;align-items:center;justify-content:center;min-width:38px;min-height:38px;"
    "width:38px;height:38px;background:none;border:none;cursor:pointer;padding:4px;flex-shrink:0;"
    "color:var(--text-mid);}\n"
    ".burger svg{display:block;pointer-events:none;}\n"
    ".burger svg rect{transition:transform .25s ease,opacity .2s ease;transform-box:fill-box;transform-origin:center;}\n"
    ".burger.open svg rect:nth-child(1){transform:translateY(5px) rotate(45deg);}\n"
    ".burger.open svg rect:nth-child(2){opacity:0;transform:scaleX(0);}\n"
    ".burger.open svg rect:nth-child(3){transform:translateY(-5px) rotate(-45deg);}\n"
    ".drawer-overlay{position:fixed;inset:0;z-index:300;background:rgba(0,0,0,.5);opacity:0;"
    "pointer-events:none;transition:opacity .3s ease;}\n"
    ".drawer-overlay.open{opacity:1;pointer-events:auto;}\n"
    ".drawer{position:fixed;top:0;right:0;bottom:0;z-index:301;width:280px;background:var(--navy-mid);"
    "border-left:1px solid var(--hairline);display:flex;flex-direction:column;transform:translateX(100%);"
    "transition:transform .3s ease;padding:80px 0 40px;}\n"
    ".drawer.open{transform:translateX(0);}\n"
    ".drawer-nav{display:flex;flex-direction:column;flex:1;}\n"
    ".drawer-item{font-size:12px;font-weight:600;letter-spacing:.15em;text-transform:uppercase;"
    "color:var(--text-muted);text-decoration:none;padding:18px 32px;border-bottom:1px solid var(--hairline);"
    "transition:color .2s,background .2s;}\n"
    ".drawer-item:hover{color:var(--accent);background:var(--accent-glow);}\n"
    ".drawer-cta{padding:32px;}\n"
    ".drawer-cta a{display:block;text-align:center;padding:14px 20px;background:var(--accent);"
    "color:var(--on-accent);font-weight:700;font-size:11px;letter-spacing:.14em;text-transform:uppercase;"
    "text-decoration:none;transition:background .2s;}\n"
    ".drawer-cta a:hover{background:var(--accent-dim);}\n"
    "@media(max-width:900px){nav.site-nav{padding:0 20px !important;}}\n"
    "@media(max-width:480px){nav.site-nav{padding:0 16px !important;}}\n"
    "@media(max-width:900px),(hover:none) and (pointer:coarse){.burger{display:flex !important;}}"
)

# ── Burger button ─────────────────────────────────────────────────────────────
BURGER_BTN = (
    '    <button class="burger" id="burger" aria-label="Открыть'
    ' меню" aria-expanded="false">\n'
    '      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">'
    '<rect fill="currentColor" x="3" y="6" width="18" height="2" rx="1"/>'
    '<rect fill="currentColor" x="3" y="11" width="18" height="2" rx="1"/>'
    '<rect fill="currentColor" x="3" y="16" width="18" height="2" rx="1"/>'
    '</svg>\n'
    '    </button>'
)

# ── Drawer HTML ───────────────────────────────────────────────────────────────
DRAWER_HTML = (
    '<!-- DRAWER OVERLAY -->\n'
    '<div class="drawer-overlay" id="drawerOverlay"></div>\n'
    '\n'
    '<!-- DRAWER -->\n'
    '<aside class="drawer" id="drawer" aria-hidden="true">\n'
    '  <nav class="drawer-nav">\n'
    '    <a class="drawer-item" href="/">Главная</a>\n'
    '    <a class="drawer-item" href="/#services">Услуги</a>\n'
    '    <a class="drawer-item" href="/results">Результаты</a>\n'
    '    <a class="drawer-item" href="/geo-aeo-optimization">GEO / AEO</a>\n'
    '    <a class="drawer-item" href="/on-premise-ai">On-Premise ИИ</a>\n'
    '    <a class="drawer-item" href="/white-label">White Label</a>\n'
    '  </nav>\n'
    '  <div class="drawer-cta">\n'
    '    <a href="/#audit">БЕСПЛАТНЫЙ '
    'АУДИТ →</a>\n'
    '  </div>\n'
    '</aside>'
)

# ── Burger JS ─────────────────────────────────────────────────────────────────
BURGER_JS = (
    "// Burger / side drawer\n"
    "const burger=document.getElementById('burger');\n"
    "const drawer=document.getElementById('drawer');\n"
    "const overlay=document.getElementById('drawerOverlay');\n"
    "function openDrawer(){"
    "drawer.classList.add('open');overlay.classList.add('open');burger.classList.add('open');"
    "burger.setAttribute('aria-expanded','true');drawer.setAttribute('aria-hidden','false');"
    "document.body.style.overflow='hidden';}\n"
    "function closeDrawer(){"
    "drawer.classList.remove('open');overlay.classList.remove('open');burger.classList.remove('open');"
    "burger.setAttribute('aria-expanded','false');drawer.setAttribute('aria-hidden','true');"
    "document.body.style.overflow='';}\n"
    "burger.addEventListener('click',()=>drawer.classList.contains('open')?closeDrawer():openDrawer());\n"
    "overlay.addEventListener('click',closeDrawer);\n"
    "document.addEventListener('keydown',e=>{if(e.key==='Escape')closeDrawer();});\n"
    "window.addEventListener('scroll',()=>{if(drawer.classList.contains('open'))closeDrawer();},"
    "{passive:true});\n"
    "document.querySelectorAll('.drawer-item').forEach(a=>{a.addEventListener('click',closeDrawer);});"
)


def patch_css(content):
    # index.html: multi-line block with MOBILE NAV comment (variable number of box-drawing chars)
    m_comment = re.search(r'/\* ═+\n   MOBILE NAV', content)
    if m_comment:
        idx_start = m_comment.start()
        end_tag = '.nav-drawer .drawer-cta { margin-top:24px; text-align:center; font-size:12px; }'
        idx_end = content.find(end_tag, idx_start)
        if idx_end != -1:
            return content[:idx_start] + BURGER_CSS + content[idx_end + len(end_tag):]

    # Subpages: condensed single-line block
    m = re.search(
        r'\.nav-hamburger\{display:none;[\s\S]*?\.nav-drawer a:hover\{color:var\(--accent\);\}',
        content
    )
    if m:
        return content[:m.start()] + BURGER_CSS + content[m.end():]

    return content


def patch_media(content):
    content = re.sub(r'\s*\.nav-ul\s*\{\s*display:none\s*!important;\s*\}', '', content)
    content = re.sub(r'\s*\.lang\s*\{\s*display:none\s*!important;\s*\}', '', content)
    content = re.sub(r'\s*\.nav-r\s*>\s*\.btn-p\s*\{[^}]+\}', '', content)
    content = re.sub(r'\s*\.nav-hamburger\s*\{[^}]+\}', '', content)
    content = re.sub(r'\s*\.nav-back\s*\{[^}]+\}', '', content)
    return content


def patch_nav_html(content):
    # Match optional <!-- NAV --> + <nav>...</nav> + optional comment + nav-drawer div
    m = re.search(
        r'(?:<!-- NAV -->\n)?<nav>\s*<div class="nav-in">[\s\S]*?</nav>\s*'
        r'(?:\n<!-- [^\n]+ -->\n)?<div[^>]*id="navDrawer"[^>]*>[\s\S]*?</div>',
        content
    )
    if not m:
        return content

    old_block = m.group(0)

    # Extract lang-sw (page-specific hrefs)
    ls = re.search(r'<details class="lang-sw" id="langSw"[\s\S]*?</details>', old_block)
    lang_sw = ls.group(0) if ls else ''

    # Extract logo <a> block
    logo = re.search(r'<a class="nav-logo" href="/"[\s\S]*?</a>', old_block)
    logo_block = logo.group(0) if logo else (
        '<a class="nav-logo" href="/"><span class="nav-wordmark">anymetric</span></a>'
    )

    new_nav = (
        '<!-- NAV -->\n'
        '<nav class="site-nav">\n'
        f'  {logo_block}\n'
        '  <div class="nav-right">\n'
        f'    {lang_sw}\n'
        + BURGER_BTN + '\n'
        '  </div>\n'
        '</nav>\n'
        '\n'
        + DRAWER_HTML
    )

    return content[:m.start()] + new_nav + content[m.end():]


def patch_js(content):
    # Match both: with "// Mobile nav hamburger\n" prefix (index.html) and without (subpages)
    m = re.search(
        r'(?:// Mobile nav hamburger\n)?const ham=document\.getElementById[\s\S]*?'
        r"window\.addEventListener\('scroll',\(\)=>\{if\(drawer\.classList\.contains\('open'\)\)"
        r"closeDrawer\(\);\},\{passive:true\}\);",
        content
    )
    if m:
        return content[:m.start()] + BURGER_JS + content[m.end():]
    return content


def patch_file(path):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        raw = f.read()

    if MARKER in raw:
        print(f'  SKIP  (already patched): {os.path.basename(path)}')
        return 'skip'

    crlf = '\r\n' in raw
    content = raw.replace('\r\n', '\n')

    content = patch_css(content)
    content = patch_media(content)
    content = patch_nav_html(content)
    content = patch_js(content)

    if crlf:
        content = content.replace('\n', '\r\n')

    if content == raw:
        print(f'  NOOP  (no patterns matched): {os.path.basename(path)}')
        return 'noop'

    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

    print(f'  PATCH (done): {os.path.basename(path)}')
    return 'patch'


if __name__ == '__main__':
    html_files = sorted(glob.glob(os.path.join(DIR, '*.html')))
    print(f'Found {len(html_files)} HTML files:')
    for f in html_files:
        print(f'  {os.path.basename(f)}')
    print()

    counts = {'patch': 0, 'skip': 0, 'noop': 0}
    for fpath in html_files:
        result = patch_file(fpath)
        counts[result] += 1

    print(f'\nSummary: {counts["patch"]} patched, {counts["skip"]} skipped, {counts["noop"]} noop.')
