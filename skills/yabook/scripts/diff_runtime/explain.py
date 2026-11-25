"""Blocos do diff para o agente explicar e gravação das explicações em `explain.json`.

O modelo recebe blocos compactos com id e escreve só o texto de cada um; posições, assinatura do
arquivo e exibição ficam com o script e a extensão do VS Code.
"""
from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

from . import compare, store

MERGE_GAP = 1  # linhas iguais entre mudanças que ainda formam um só bloco
MAX_LINES = 30
MAX_WIDTH = 200


def _lines(path):
    return compare.read_text(path).splitlines()


def _clip(lines):
    lines = [line if len(line) <= MAX_WIDTH else line[:MAX_WIDTH] + "…" for line in lines]
    if len(lines) <= MAX_LINES:
        return lines
    head, tail = lines[:20], lines[-8:]
    return head + [f"… ({len(lines) - 28} linhas omitidas)"] + tail


def digest(path):
    return hashlib.sha1(Path(path).read_bytes()).hexdigest() if path and Path(path).exists() else None


def _groups(old, new):
    """Trechos alterados como (i1, i2, j1, j2), unindo mudanças separadas por até MERGE_GAP linhas."""
    groups = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if groups and i1 - groups[-1][1] <= MERGE_GAP and j1 - groups[-1][3] <= MERGE_GAP:
            groups[-1] = (groups[-1][0], i2, groups[-1][2], j2)
        else:
            groups.append((i1, i2, j1, j2))
    return groups


def blocks(folder, data, only=None):
    """Blocos numerados da sessão; linhas em base 1, contagem zero indica inserção ou remoção pura."""
    found, number = [], 0
    for change in compare.changes(folder, data):
        if only and change["caminho"] != only:
            continue
        old, new = _lines(change["antes"]), _lines(change["depois"] if change["estado"] != "removido" else None)
        for i1, i2, j1, j2 in _groups(old, new):
            number += 1
            found.append(dict(id=f"b{number}", arquivo=change["caminho"], estado=change["estado"],
                              antes=[i1 + 1, i2 - i1], depois=[j1 + 1, j2 - j1],
                              removidas=_clip(old[i1:i2]), adicionadas=_clip(new[j1:j2])))
    return found


def parse(text):
    """Aceita {"blocos": [{"id", "texto"}]} ou {"b1": "texto"}."""
    payload = json.loads(text)
    if isinstance(payload, dict) and isinstance(payload.get("blocos"), list):
        pairs = [(row.get("id"), row.get("texto")) for row in payload["blocos"] if isinstance(row, dict)]
    elif isinstance(payload, dict):
        pairs = list(payload.items())
    else:
        raise ValueError("Formato inválido: use {\"blocos\": [{\"id\": \"b1\", \"texto\": \"...\"}]}")
    texts = {}
    for key, value in pairs:
        if not isinstance(key, str) or not isinstance(value, str) or not value.strip():
            raise ValueError("Cada bloco precisa de id e texto não vazio")
        texts[key] = value.strip()
    return texts


def save(folder, data, texts, only=None):
    """Grava `explain.json` com posição, assinatura do arquivo atual e texto de cada bloco."""
    current = {block["id"]: block for block in blocks(folder, data, only)}
    unknown = sorted(set(texts) - set(current))
    if unknown:
        raise ValueError("Blocos inexistentes na sessão atual: " + ", ".join(unknown))
    rows = []
    for key, block in current.items():
        if key not in texts:
            continue
        after = store.target(data["projeto"], block["arquivo"])
        rows.append(dict(id=key, arquivo=block["arquivo"], estado=block["estado"], antes=block["antes"],
                         depois=block["depois"], texto=texts[key], assinatura=digest(after)))
    payload = dict(versao=1, sessao=data["sessao"], gerada=store.now_iso(), blocos=rows,
                   pendentes=[key for key in current if key not in texts])
    target = Path(folder) / "explain.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target, payload
