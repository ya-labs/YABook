#!/usr/bin/env python3
"""Gera os temas YA LABS (escuro e claro) com as cores da marca e a estrutura do Night Owl, sem itálico.

Cores da marca: as da paleta "ya-labs" do site do YABook Tasks (`tasks_runtime/site/app.css`) — azul
escuro nas superfícies, laranja nos destaques e branco no texto da interface. A distribuição segue o
Night Owl (no italics): editor e barra lateral no mesmo fundo, bordas discretas, laranja onde o Night
Owl usa o roxo de destaque, e realce de sintaxe com o mesmo mapeamento de papéis. Rode depois de
mudar a paleta:

    python3 apps/vscode/scripts/themes.py [--check]

`--check` confere o contraste de cada cor contra o fundo do editor, com o mínimo de cada papel (MINIMUM).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PALETTES = {
    "escuro": dict(
        ui="vs-dark", label="YA LABS Escuro",
        editor="#0b1221", deep="#060b16", nav="#050a17", raised="#141d30", card="#1e283e", hover="#1d3b53",
        line="#101929", border="#1a2a40", border_strong="#33425c", text="#d6deeb", ui_text="#d6deeb",
        text2="#89a4bb", muted="#5f7e97", line_number="#4b6479", line_number_active="#c5e4fd",
        accent="#f78c6c", accent_text="#0b1221", amber="#ecc48d", selection="#1d3b53", word="#1d3b53",
        cursor="#80a4c2", subtle_mark="#5f7e97",
        syntax=dict(comment="#637777", keyword="#c792ea", operator="#c792ea", string="#ecc48d",
                    number="#f78c6c", constant="#ff5874", function="#82aaff", type="#ffcb8b",
                    variable="#d6deeb", constant_variable="#9ad1ff", parameter="#7fdbca", property="#baebe2", tag="#caece6",
                    attribute="#addb67", support="#c5e478", object="#c5e478", accessed="#faf39f",
                    punctuation="#d9f5dd", heading="#82b1ff", link="#ff869a"),
        inserted="#99b76d23", inserted_line="#99b76d14", removed="#ef535033", removed_line="#ef535014",
        ansi=dict(blue="#82aaff", green="#22da6e", yellow="#addb67", red="#ef5350", magenta="#c792ea", cyan="#21c7a8")),
    "claro": dict(
        ui="vs", label="YA LABS Claro",
        editor="#fbfbfb", deep="#f0f0f0", nav="#f0f0f0", raised="#ffffff", card="#ffffff", hover="#e0e7ea",
        line="#f0f0f0", border="#d9d9d9", border_strong="#93a1a1", text="#403f53", ui_text="#403f53",
        text2="#5f6b7c", muted="#90a7b2", line_number="#90a7b2", line_number_active="#403f53",
        accent="#b8663e", accent_text="#ffffff", amber="#c96765", selection="#e0e0e0", word="#e0e7ea",
        cursor="#90a7b2", subtle_mark="#90a7b2",
        syntax=dict(comment="#989fb1", keyword="#994cc3", operator="#994cc3", string="#c96765",
                    number="#aa0982", constant="#bc5454", function="#4876d6", type="#111111",
                    variable="#403f53", constant_variable="#2f86b8", parameter="#0c969b", property="#0c969b", tag="#994cc3",
                    attribute="#4876d6", support="#4f7b25", object="#4f7b25", accessed="#8b5500",
                    punctuation="#403f53", heading="#4876d6", link="#c96765"),
        inserted="#08916a1f", inserted_line="#08916a12", removed="#de3d3b1f", removed_line="#de3d3b12",
        ansi=dict(blue="#288ed7", green="#08916a", yellow="#daaa01", red="#de3d3b", magenta="#d6438a", cyan="#2aa298")),
}

# Contraste mínimo contra o fundo, como no Night Owl: código legível sem estourar; comentário e
# texto secundário mais apagados de propósito.
MINIMUM = dict(
    escuro=dict(default=4.5, comment=3.0, muted=2.5, line_number=2.0, text2=4.0),
    claro=dict(default=3.4, comment=2.5, muted=2.4, line_number=2.0, text2=4.0),  # nível do Light Owl
)

# Papel de sintaxe -> escopos TextMate (mapeamento do Night Owl). Nenhum papel usa itálico.
SYNTAX = [
    ("comment", "", ["comment", "punctuation.definition.comment"]),
    ("keyword", "", ["keyword", "keyword.control", "storage", "storage.type", "storage.modifier"]),
    ("operator", "", ["keyword.operator", "keyword.operator.new"]),
    ("punctuation", "", ["punctuation", "meta.brace", "punctuation.accessor"]),
    ("string", "", ["string", "string.quoted", "markup.inline.raw"]),
    ("number", "", ["constant.numeric"]),
    ("constant", "", ["constant.language", "constant.character.escape", "support.constant"]),
    ("function", "", ["entity.name.function", "support.function", "meta.function-call", "meta.method-call",
                      "variable.function"]),
    ("type", "", ["entity.name.type", "entity.name.class", "support.type", "support.class", "entity.other.inherited-class"]),
    # Como no Night Owl, só gramática (sem realce semântico): `let`/`var` e usos em branco; `const` declarado em
    # azul-claro; objeto antes do ponto em verde; propriedade acessada depois do ponto em amarelo.
    ("variable", "", ["variable", "variable.other", "variable.other.readwrite", "meta.definition.variable"]),
    ("constant_variable", "", ["variable.other.constant", "meta.definition.variable variable.other.constant"]),
    ("support", "", ["support.variable"]),
    # `constructor` é storage.type dentro da declaração de método: cor de nome de função; get/set seguem palavra-chave.
    ("function", "", ["meta.method.declaration storage.type"]),
    ("keyword", "", ["meta.method.declaration storage.type.property"]),
    ("parameter", "", ["variable.parameter", "variable.language.this", "variable.language"]),
    ("object", "", ["variable.other.object", "support.variable.object"]),
    ("accessed", "", ["variable.other.property", "variable.other.object.property", "support.variable.property"]),
    ("property", "", ["meta.object-literal.key", "meta.property-name", "meta.definition.property variable.object.property"]),
    ("tag", "", ["entity.name.tag", "meta.tag"]),
    ("attribute", "", ["entity.other.attribute-name"]),
    ("heading", "bold", ["markup.heading", "entity.name.section"]),
    ("attribute", "bold", ["markup.bold"]),
    ("text", "", ["markup.italic"]),
    ("link", "underline", ["markup.underline.link", "string.other.link"]),
    ("attribute", "", ["markup.inserted"]),
    ("constant", "", ["markup.deleted", "invalid"]),
]


def theme(name):
    p = PALETTES[name]
    colors = {
        "focusBorder": p["border_strong"], "foreground": p["ui_text"], "descriptionForeground": p["text2"],
        "widget.border": p["border"], "selection.background": p["selection"], "icon.foreground": p["text2"],
        "textLink.foreground": p["syntax"]["link"], "textLink.activeForeground": p["syntax"]["link"],
        "button.background": p["accent"], "button.foreground": p["accent_text"], "button.hoverBackground": p["accent"] + "cc",
        "badge.background": p["accent"], "badge.foreground": p["accent_text"],
        "progressBar.background": p["accent"],
        "input.background": p["line"], "input.border": p["border"], "input.foreground": p["ui_text"],
        "input.placeholderForeground": p["muted"], "inputOption.activeBorder": p["subtle_mark"],
        "dropdown.background": p["raised"], "dropdown.border": p["border"],
        "editor.background": p["editor"], "editor.foreground": p["text"],
        "editorLineNumber.foreground": p["line_number"], "editorLineNumber.activeForeground": p["line_number_active"],
        "editor.lineHighlightBackground": p["line"], "editor.lineHighlightBorder": p["line"],
        "editor.selectionBackground": p["selection"], "editor.inactiveSelectionBackground": p["line"],
        "editor.wordHighlightBackground": p["word"] + "88", "editor.findMatchBackground": p["subtle_mark"] + "79",
        "editor.findMatchHighlightBackground": p["subtle_mark"] + "40", "editorCursor.foreground": p["cursor"],
        "editorBracketMatch.border": p["subtle_mark"] + "99", "editorBracketMatch.background": p["editor"],
        "editorIndentGuide.background1": p["border"], "editorIndentGuide.activeBackground1": p["border_strong"],
        "editorWhitespace.foreground": p["border"], "editorRuler.foreground": p["border"],
        "editorWidget.background": p["raised"], "editorWidget.border": p["border"],
        "editorSuggestWidget.background": p["raised"], "editorSuggestWidget.selectedBackground": p["hover"],
        "editorHoverWidget.background": p["raised"], "editorHoverWidget.border": p["border"],
        "editorGroupHeader.tabsBackground": p["deep"], "editorGroup.border": p["border"],
        "tab.activeBackground": p["editor"], "tab.inactiveBackground": p["deep"], "tab.border": p["deep"],
        "tab.activeForeground": p["ui_text"], "tab.inactiveForeground": p["muted"], "tab.activeBorderTop": p["accent"],
        "tab.unfocusedActiveBorderTop": p["border_strong"],
        "activityBar.background": p["editor"], "activityBar.foreground": p["ui_text"],
        "activityBar.inactiveForeground": p["muted"], "activityBar.activeBorder": p["accent"],
        "activityBar.border": p["border"], "activityBarBadge.background": p["accent"],
        "activityBarBadge.foreground": p["accent_text"],
        "sideBar.background": p["editor"], "sideBar.foreground": p["text2"], "sideBar.border": p["border"],
        "sideBarTitle.foreground": p["ui_text"], "sideBarSectionHeader.background": p["editor"],
        "sideBarSectionHeader.foreground": p["ui_text"], "sideBarSectionHeader.border": p["border"],
        "list.activeSelectionBackground": p["hover"], "list.activeSelectionForeground": p["ui_text"],
        "list.inactiveSelectionBackground": p["line"], "list.hoverBackground": p["line"],
        "list.focusOutline": p["border_strong"], "list.highlightForeground": p["syntax"]["function"],
        "titleBar.activeBackground": p["nav"], "titleBar.activeForeground": p["ui_text"],
        "titleBar.inactiveBackground": p["nav"], "titleBar.inactiveForeground": p["muted"],
        "titleBar.border": p["border"],
        "statusBar.background": p["nav"], "statusBar.foreground": p["text2"], "statusBar.border": p["border"],
        "statusBar.noFolderBackground": p["nav"], "statusBar.debuggingBackground": p["accent"],
        "statusBar.debuggingForeground": p["accent_text"], "statusBarItem.remoteBackground": p["nav"],
        "statusBarItem.remoteForeground": p["text2"],
        "panel.background": p["editor"], "panel.border": p["border"], "panelTitle.activeBorder": p["accent"],
        "panelTitle.activeForeground": p["ui_text"], "panelTitle.inactiveForeground": p["muted"],
        "terminal.background": p["editor"], "terminal.foreground": p["text"], "terminalCursor.foreground": p["cursor"],
        "terminal.ansiBlue": p["ansi"]["blue"], "terminal.ansiGreen": p["ansi"]["green"],
        "terminal.ansiYellow": p["ansi"]["yellow"], "terminal.ansiRed": p["ansi"]["red"],
        "terminal.ansiMagenta": p["ansi"]["magenta"], "terminal.ansiCyan": p["ansi"]["cyan"],
        "diffEditor.insertedTextBackground": p["inserted"], "diffEditor.insertedLineBackground": p["inserted_line"],
        "diffEditor.removedTextBackground": p["removed"], "diffEditor.removedLineBackground": p["removed_line"],
        "gitDecoration.addedResourceForeground": p["syntax"]["attribute"],
        "gitDecoration.modifiedResourceForeground": p["syntax"]["string"],
        "gitDecoration.deletedResourceForeground": p["syntax"]["constant"],
        "gitDecoration.untrackedResourceForeground": p["syntax"]["attribute"],
        "editorError.foreground": p["syntax"]["constant"], "editorWarning.foreground": p["amber"],
        "editorInfo.foreground": p["syntax"]["function"],
        "peekViewEditor.background": p["line"], "peekViewResult.background": p["raised"],
        "peekViewTitle.background": p["raised"], "peekView.border": p["border_strong"],
        "scrollbarSlider.background": p["border_strong"] + "66", "scrollbarSlider.hoverBackground": p["border_strong"] + "aa",
        "scrollbarSlider.activeBackground": p["subtle_mark"] + "aa",
    }
    tokens = [{"scope": scopes, "settings": dict({"foreground": (p["syntax"].get(role) or p[role])}, fontStyle=style)}
              for role, style, scopes in SYNTAX]
    # Sem realce semântico, como o Night Owl: ele trata módulos do `require` como namespace (cor de tipo) e
    # apagaria a distinção entre objeto e propriedade acessada que a gramática faz.
    return {"name": p["label"], "type": "dark" if p["ui"] == "vs-dark" else "light", "colors": colors,
            "tokenColors": tokens, "semanticHighlighting": False}


def luminance(hex_color):
    def channel(value):
        value /= 255
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def check():
    failures = []
    for name, p in PALETTES.items():
        roles = dict(p["syntax"], text=p["text"], text2=p["text2"], muted=p["muted"], line_number=p["line_number"])
        for role, color in sorted(roles.items()):
            ratio = contrast(color, p["editor"])
            minimum = MINIMUM[name].get(role, MINIMUM[name]["default"])
            print(f"{name:7} {role:12} {color} {ratio:5.2f} (mín. {minimum})")
            if ratio < minimum:
                failures.append((name, role, round(ratio, 2)))
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = check()
    if failures:
        print("Contraste abaixo de 4,5:1:", failures)
        return 1
    if not args.check:
        for name in PALETTES:
            target = ROOT / "themes" / f"ya-labs-{name}.json"
            target.parent.mkdir(exist_ok=True)
            target.write_text(json.dumps(theme(name), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
