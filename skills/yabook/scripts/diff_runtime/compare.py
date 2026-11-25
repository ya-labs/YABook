"""Comparação da versão anterior guardada com o arquivo atual."""
from __future__ import annotations

import difflib
from pathlib import Path

from . import store


def read_text(path):
    """Texto do arquivo: UTF-8 quando válido, senão Latin-1 (fontes ABL em ISO-8859-1)."""
    if path is None or not Path(path).exists():
        return ""
    data = Path(path).read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def changes(folder, data, view="sessao"):
    """Arquivos da visão com estado e contagem de linhas; omite os que voltaram ao original."""
    found = []
    for item in store.view_items(data, view)[1]:
        before = Path(folder) / item["antes"] if item.get("antes") else None
        later = "depois" in item  # rodada antiga: o "depois" é o "antes" da rodada seguinte (None = apagado)
        after = (Path(folder) / item["depois"] if item["depois"] else Path(folder) / "_ausente") if later \
            else store.target(data["projeto"], item["caminho"])
        old, new = read_text(before), read_text(after)
        if old == new and (before is not None) == after.exists():
            continue
        state = "novo" if before is None else "removido" if not after.exists() else "alterado"
        lines = list(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0))
        added = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
        found.append(dict(caminho=item["caminho"], estado=state, antes=str(before) if before else None,
                          depois=str(after), adicionadas=added, removidas=removed))
    return found


def unified(change, context=3):
    old, new = read_text(change["antes"]), read_text(change["depois"])
    label = change["caminho"]
    lines = difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                 "a/" + label if change["antes"] else "/dev/null",
                                 "b/" + label if change["estado"] != "removido" else "/dev/null", n=context)
    text = "".join(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n" for line in lines)
    return text


def patch(folder, data, output=None):
    """Grava o `.patch` da sessão (UTF-8) e devolve o caminho."""
    target = Path(output) if output else Path(folder) / "alteracoes.patch"
    target.write_text("".join(unified(change) for change in changes(folder, data)), encoding="utf-8")
    return target
