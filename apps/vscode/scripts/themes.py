#!/usr/bin/env python3
"""Gera os temas YA LABS (claro e escuro) a partir da paleta do site do YABook Tasks.

As cores de base, borda, texto, ação e rótulos vêm dos tokens de `tasks_runtime/site/app.css`;
o amarelo é o da estrela do ícone do YABook. Rode depois de mudar a paleta:

    python3 apps/vscode/scripts/themes.py [--check]

`--check` só confere o contraste do texto contra o fundo do editor (mínimo 4,5:1).
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
        editor="#202226", panel="#232529", deep="#17191c", raised="#292c31", subtle="#25282d", hover="#363b43",
        border="#41464e", border_strong="#7d8796", text="#eef1f5", text2="#b6beca", muted="#8e97a5",
        accent="#a7c2ee", accent_text="#111b2b", selection="#3a4a66", star="#f2bf3e",
        blue="#96c3ff", green="#78e0b3", yellow="#f1ca71", orange="#f4b77b", red="#ff9daf",
        pink="#f1b5de", purple="#c6b3ff", gray="#bfcee4",
        inserted="#78e0b31f", inserted_line="#78e0b314", removed="#ff9daf24", removed_line="#ff9daf14"),
    "claro": dict(
        ui="vs", label="YA LABS Claro",
        editor="#ffffff", panel="#f4f5f7", deep="#e6e9ed", raised="#ffffff", subtle="#eff1f4", hover="#e2e7ef",
        border="#d9dee5", border_strong="#778294", text="#26303c", text2="#515c6c", muted="#5f6b7c",
        accent="#294f9d", accent_text="#ffffff", selection="#d4dceb", star="#f2bf3e",
        blue="#1d52c2", green="#116844", yellow="#8b5500", orange="#a4410e", red="#b42c47",
        pink="#992c77", purple="#6545b3", gray="#43536d",
        inserted="#1168441f", inserted_line="#11684412", removed="#b42c471f", removed_line="#b42c4712"),
}

# Papel de sintaxe -> (cor da paleta, estilo, escopos TextMate)
SYNTAX = [
    ("muted", "italic", ["comment", "punctuation.definition.comment"]),
    ("purple", "", ["keyword", "storage", "keyword.control", "storage.modifier"]),
    ("green", "", ["string", "string.quoted", "markup.inline.raw"]),
    ("orange", "", ["constant.numeric", "constant.language", "constant.character", "support.constant"]),
    ("blue", "", ["entity.name.function", "support.function", "meta.function-call"]),
    ("yellow", "", ["entity.name.type", "entity.name.class", "support.type", "support.class", "storage.type"]),
    ("red", "", ["entity.name.tag", "markup.deleted", "invalid"]),
    ("yellow", "", ["entity.other.attribute-name"]),
    ("text", "", ["variable", "variable.other", "meta.definition.variable"]),
    ("text2", "", ["keyword.operator", "punctuation"]),
    ("accent", "bold", ["markup.heading", "entity.name.section"]),
    ("text", "bold", ["markup.bold"]),
    ("text", "italic", ["markup.italic"]),
    ("blue", "underline", ["markup.underline.link", "string.other.link"]),
    ("green", "", ["markup.inserted"]),
    ("pink", "", ["constant.other", "variable.language", "support.variable"]),
]


def theme(name):
    p = PALETTES[name]
    colors = {
        "focusBorder": p["accent"], "foreground": p["text"], "descriptionForeground": p["text2"],
        "widget.border": p["border"], "selection.background": p["selection"], "icon.foreground": p["text2"],
        "textLink.foreground": p["accent"], "textLink.activeForeground": p["accent"],
        "button.background": p["accent"], "button.foreground": p["accent_text"], "button.hoverBackground": p["blue"],
        "badge.background": p["star"], "badge.foreground": "#111b2b",
        "input.background": p["subtle"], "input.border": p["border"], "input.foreground": p["text"],
        "dropdown.background": p["raised"], "dropdown.border": p["border"],
        "editor.background": p["editor"], "editor.foreground": p["text"],
        "editorLineNumber.foreground": p["muted"], "editorLineNumber.activeForeground": p["text"],
        "editor.lineHighlightBackground": p["subtle"], "editor.selectionBackground": p["selection"],
        "editor.inactiveSelectionBackground": p["hover"], "editorCursor.foreground": p["accent"],
        "editorIndentGuide.background1": p["border"], "editorWhitespace.foreground": p["border"],
        "editorWidget.background": p["raised"], "editorWidget.border": p["border"],
        "editorGroupHeader.tabsBackground": p["deep"], "editorGroup.border": p["border"],
        "tab.activeBackground": p["editor"], "tab.inactiveBackground": p["deep"], "tab.border": p["border"],
        "tab.activeForeground": p["text"], "tab.inactiveForeground": p["text2"], "tab.activeBorderTop": p["star"],
        "activityBar.background": p["deep"], "activityBar.foreground": p["text"],
        "activityBar.inactiveForeground": p["muted"], "activityBar.activeBorder": p["star"],
        "activityBarBadge.background": p["star"], "activityBarBadge.foreground": "#111b2b",
        "sideBar.background": p["panel"], "sideBar.foreground": p["text"], "sideBar.border": p["border"],
        "sideBarSectionHeader.background": p["panel"], "sideBarSectionHeader.border": p["border"],
        "list.activeSelectionBackground": p["selection"], "list.activeSelectionForeground": p["text"],
        "list.inactiveSelectionBackground": p["hover"], "list.hoverBackground": p["hover"],
        "list.focusOutline": p["accent"], "list.highlightForeground": p["accent"],
        "titleBar.activeBackground": p["deep"], "titleBar.activeForeground": p["text"],
        "titleBar.inactiveBackground": p["deep"], "titleBar.inactiveForeground": p["muted"],
        "statusBar.background": p["panel"], "statusBar.foreground": p["text2"], "statusBar.border": p["border"],
        "statusBar.noFolderBackground": p["panel"], "statusBarItem.remoteBackground": p["accent"],
        "statusBarItem.remoteForeground": p["accent_text"],
        "panel.background": p["editor"], "panel.border": p["border"], "panelTitle.activeBorder": p["star"],
        "terminal.background": p["editor"], "terminal.foreground": p["text"],
        "terminal.ansiBlue": p["blue"], "terminal.ansiGreen": p["green"], "terminal.ansiYellow": p["yellow"],
        "terminal.ansiRed": p["red"], "terminal.ansiMagenta": p["purple"], "terminal.ansiCyan": p["accent"],
        "diffEditor.insertedTextBackground": p["inserted"], "diffEditor.insertedLineBackground": p["inserted_line"],
        "diffEditor.removedTextBackground": p["removed"], "diffEditor.removedLineBackground": p["removed_line"],
        "gitDecoration.addedResourceForeground": p["green"], "gitDecoration.modifiedResourceForeground": p["blue"],
        "gitDecoration.deletedResourceForeground": p["red"], "gitDecoration.untrackedResourceForeground": p["green"],
        "editorError.foreground": p["red"], "editorWarning.foreground": p["yellow"], "editorInfo.foreground": p["blue"],
        "peekViewEditor.background": p["subtle"], "peekViewResult.background": p["panel"],
        "scrollbarSlider.background": p["border"] + "99", "scrollbarSlider.hoverBackground": p["border_strong"] + "99",
    }
    tokens = [{"scope": scopes, "settings": dict({"foreground": p[role]}, **({"fontStyle": style} if style else {}))}
              for role, style, scopes in SYNTAX]
    return {"name": p["label"], "type": "dark" if p["ui"] == "vs-dark" else "light", "colors": colors,
            "tokenColors": tokens, "semanticHighlighting": True}


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
        for role in sorted({role for role, _, _ in SYNTAX} | {"text2"}):
            ratio = contrast(p[role], p["editor"])
            print(f"{name:7} {role:7} {p[role]} {ratio:5.2f}")
            if ratio < 4.5:
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
