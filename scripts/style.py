"""Original Warp styling transforms, applied to Noctua only on the installing machine."""

from pathlib import Path
import json, shutil, re
PARTS = ['chrome', 'spaces', 'agents', 'tabs', 'pane', 'status', 'files', 'changes']

def replace(text, old, new, count=None):
    if old not in text:
        raise ValueError(f'Missing expected source: {old[:120]}')
    return text.replace(old, new) if count is None else text.replace(old, new, count)

def apply(HOME, assets):
    for part in PARTS:
        path = HOME / 'mods' / f'warp-{part}' / 'main.js'
        text = path.read_text()
        for other in PARTS:
            text = text.replace(f'mods/noctua-{other}', f'mods/warp-{other}')
            text = text.replace(f'mod: "noctua-{other}"', f'mod: "warp-{other}"')
        text = text.replace('const MONO = "Geist Mono";', 'const MONO = "Roboto";')
        text = text.replace('const bright = (t) => (settings()?.dark === false ? t.foreground : t.ansi15);', 'const bright = (t) => t.foreground;')
        text = text.replace('.text_size(13.5)', '.text_size(12)').replace('.text_size(12.8)', '.text_size(12)')
        text = text.replace('.text_size(12.5)', '.text_size(12)').replace('.text_size(11.5)', '.text_size(10)')
        text = text.replace('.text_size(13)', '.text_size(12)')
        text = text.replace('.size_full()', '.size_full().font_family("Roboto").font_weight(400).line_height(1.2)')
        text = '// Warp Gruvbox personal styling; original Noctua interactions retained.\n' + text
        if part == 'chrome':
            text = text.replace('shared("sidebar.width") ?? 300', 'shared("sidebar.width") ?? 248')
            text = text.replace('size: 30, icon: 18', 'size: 24, icon: 16')
            text = text.replace('.text_size(12).text_color(t.muted).child(machine)', '.text_size(10).text_color(t.muted).child(machine)')
            text = text.replace('.h(38)', '.h(36)').replace('.h(28).flex_none().justify_center()', '.h(32).flex_none().justify_center()')
            text = text.replace('.pl(mac ? 76 : 14).pr(6).gap(9)', '.pl(mac ? 76 : 12).pr(8).gap(8)')
            text = text.replace('.font_semibold().text_color(bright(t)).child("Herdr")', '.font_weight(500).text_color(bright(t)).child("Herdr")')
            text = text.replace('.h(24).px(9).gap(8)', '.h(24).px(6).gap(6)')
            text = text.replace('.bg(t.canvas).border(1).border_color(t.input).rounded(R)', '.bg(t.chrome).rounded(R)')
            text = text.replace('.hover((s) => s.text_color(t.muted))', '.hover((s) => s.bg(t.hover).text_color(t.foreground))')
            text = text.replace('`${ICONS}/search.svg`).size(13)', '`${ICONS}/search.svg`).size(12)')
            text = text.replace('.h(28).flex_none().px(8).pb(4).gap(2)', '.h(32).flex_none().px(8).py(4).gap(4)')
        if part == 'spaces':
            text = replace(text, 'import { View, div, svg }', 'import { View, div, svg, image }')
            start = text.index('function avatar(')
            end = text.index('\n// The pin on an avatar', start)
            text = text[:start] + 'function avatar(t, name, color, size, under, st, pin = null, program = null) {\n  const glyph = program?.agent && program?.icon\n    ? (program.tint ? svg(program.icon).size(16).text_color(t.foreground) : image(program.icon).size(16))\n    : svg(`${ICONS}/warp-terminal.svg`).size(size * 2 / 3).text_color(t.muted);\n  return h_flex().relative().size(size).flex_none().rounded_full()\n    .bg(mix(t.ansi15, 0.10, under)).items_center().justify_center()\n    .child(glyph)\n    .when(Boolean(st) && st !== "idle", el => el.child(h_flex().absolute().right(-2).bottom(-2)\n      .size(12).rounded_full().bg(under).items_center().justify_center().child(dot(t, st, 8, 9))))\n    .when(Boolean(pin), el => el.child(pin));\n}\n' + text[end:]
            text = replace(text, 'const H = { card: 61,', 'const H = { card: 48,')
            text = replace(text, '.h(57).px(10).gap(12).items_center()', '.h(44).px(8).py(8).gap(8).items_start()')
            text = replace(text, 'avatar(t, w.name, color, 28, under, w.status, pinned || hovered ? pin : null)', 'avatar(t, w.name, color, 24, under, w.status, pinned || hovered ? pin : null,\n        ps.find(p => p.tab === ((w.tabs ?? []).find(c => c.active) ?? w.tabs?.[0])?.id && p.program?.agent)?.program)')
            a = text.index('      .child(v_flex().flex_1().min_w(0).gap(3)', text.index('  card(head,'))
            b = text.index('\n    return div().h(61)', a)
            text = text[:a] + '      .child(v_flex().flex_1().min_w(0).gap(1)\n        .child(h_flex().h(14.4).gap(4).items_center()\n          .child(div().flex_1().min_w(0).truncate().text_size(12).font_weight(400)\n            .text_color(t.foreground).tooltip(title || w.name).child(title || w.name))\n          .when(Boolean(since), el => el.child(div().flex_none().text_size(10)\n            .text_color(t[STATES[since.st].tone]).child(since.text))))\n        .child(h_flex().h(12).gap(4).items_center()\n          .child(div().flex_1().min_w(0).truncate().text_size(10).text_color(t.muted).tooltip(w.name).child(w.name))\n          .when(Boolean(branch), el => el.child(this.branchTag(t, color, branch, 80)))\n          .children([this.changesLink(w, head.g, t)].filter(Boolean))\n          .when(trees.length > 0, el => el.child(this.wtButton(head, trees, open, t)))));\n' + text[b:]
            text = replace(text, 'return div().h(61).px(8).pb(4)', 'return div().h(48).px(8).pb(4)')
            text = text.replace('.size(12).flex_none().text_color(lighten(color, 0.12))', '.size(10).flex_none().text_color(t.muted)')
            text = text.replace('.font_family(MONO).text_size(11)', '.font_family(MONO).text_size(10)')
            text = text.replace('.h(20).flex_none().px(6).gap(5)', '.h(16).flex_none().px(4).gap(3)')
            text = text.replace('.pl(50).pr(10)', '.pl(48).pr(8)')
            text = text.replace('colorOf(w.id, t), 28,', 'colorOf(w.id, t), 24,')
        if part == 'agents':
            text = text.replace('.h(30)', '.h(28)').replace('.gap(9)', '.gap(8)')
            text = text.replace('.pt(8)\n        .h(28)', '.pt(4)\n        .h(28)')
            text = text.replace('.h(41)\n          .pt(14)\n          .pb(5)', '.h(32)\n          .pt(4)\n          .pb(4)')
            text = replace(text, '.id(`ag-${a.address}`)\n        .px(8)\n        .h(28)', '.id(`ag-${a.address}`)\n        .px(8)\n        .h(full && more ? 44 : 36)')
            text = replace(text, '.when(Boolean(pic), el => el.child(div().id(`agent-fold-${a.address}`)', '.when(Boolean(pic), el => el.child(div().id(`agent-fold-${a.address}`).size(24).flex_none().rounded_full().bg(t.raised).flex().items_center().justify_center()')
            old = '.child(h_flex().flex_1().min_w(0).gap(5).items_center()\n          .child(div().flex_none().max_w(full && more ? 120 : 200).truncate().text_color(idle ? t.muted : t.foreground).child(name))\n          .when(full && Boolean(more), el => el.child(div().flex_1().min_w(0).truncate().text_color(t.dim).child(`\\u00b7 ${more}`))))'
            new = '.child(v_flex().flex_1().min_w(0).gap(1)\n          .child(div().min_w(0).truncate().text_size(12).text_color(t.foreground).tooltip(name).child(name))\n          .when(full && Boolean(more), el => el.child(div().min_w(0).truncate().text_size(10).text_color(t.muted).tooltip(more).child(more))))'
            text = replace(text, old, new)
            text = text.replace('.font_medium()', '.font_weight(400)')
            text = text.replace('.text_size(11).text_color(t.dim).child(duration', '.text_size(10).text_color(t.dim).child(duration')
        if part == 'tabs':
            text = replace(text, 'const line = (el) => el.border_b(1).border_color(t.border);', 'const line = (el) => el;')
            text = replace(text, '.h_full().min_w(140).max_w(260).flex_none().pl(12).pr(8).gap(8)', '.h(28).my(4).mx(2).min_w(120).max_w(240).flex_none().px(8).gap(6)')
            text = replace(text, '.border_r(1).border_color(t.border)', '.rounded(R)')
            text = replace(text, '.when(on, el => el.bg(t.background).text_color(t.foreground))', '.when(on, el => el.bg(t.selected).text_color(t.foreground))')
            text = text.replace('.h(28).px(10).gap(6)', '.h(24).px(8).gap(6)')
            text = replace(text, 'return h_flex().size_full()', 'return h_flex().size_full().border_b(1).border_color(t.border)')
            text = text.replace('.text_size(12).border(1).border_color(on ? t.selected : t.chrome).bg(on ? t.selected : t.chrome)', '.text_size(12).bg(on ? t.selected : t.chrome)')
        if part == 'pane':
            text = text.replace('.pl(10)', '.pl(8)').replace('.font_medium()', '.font_weight(400)')
            text = text.replace('.text_size(12)\n      .text_color(t.dim)', '.text_size(10)\n      .text_color(t.muted)')
        if part == 'status':
            text = text.replace('const ink = spaceInk(spaces().find((s) => s.active)?.id, t);', 'const ink = t.muted;')
            text = text.replace('.px(14).gap(14)', '.px(12).gap(12)').replace('.text_size(12).text_color(t.muted)', '.text_size(10).text_color(t.muted)')
        if part in ('files', 'changes'):
            text = text.replace('.h(28).flex_none().px(10).gap(8)', '.h(28).flex_none().px(8).gap(8)')
        path.write_text(text)
    chrome = HOME / 'mods/warp-chrome'
    for icon in ['terminal', 'folder']:
        shutil.copy2(assets / f'{icon}.svg', chrome / f'warp-{icon}.svg')

def apply_titles(home):
    for part in ('spaces', 'tabs'):
        path = home / 'mods' / f'warp-{part}' / 'main.js'
        text = path.read_text()
        indent = '    ' if part == 'spaces' else '  '
        needle = indent + 'const live = clean(lead?.title);'
        text = replace(text, needle, indent + 'if (lead?.program?.shell && !lead.program.agent) return lead.program.name || "shell";' + '\n' + needle)
        text = replace(text, 'const telling = live && live !== lead?.program?.name', 'const telling = live && live !== lead?.terminal && !/^t[0-9a-f]+$/i.test(live) && live !== lead?.program?.name')
        if part == 'spaces':
            first = '.text_color(t.foreground).tooltip(title || w.name).child(title || w.name)'
            second = '.text_color(t.muted).tooltip(w.name).child(w.name)'
            text = replace(text, first, '.text_color(t.foreground).tooltip(w.name).child(w.name)')
            text = replace(text, second, '.text_color(t.muted).tooltip(title || w.name).child(title || w.name)')
        path.write_text(text)
