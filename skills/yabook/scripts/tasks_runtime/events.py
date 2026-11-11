"""Histórico de ações em `eventos/AAAA-MM-<maquina>.jsonl`, somente acréscimo.

Ações do agente nascem analisadas. Ações do quadro ficam pendentes até uma
linha `analise` citá-las, em qualquer máquina, o que se apura após o pull.
"""
import datetime
import json
import os
import re
from pathlib import Path

_SAFE = re.compile(r"[^a-z0-9-]+")


def _machine(value):
    return _SAFE.sub("-", (value or "local").lower()).strip("-") or "local"


def _path(root, machine, when):
    return Path(root) / "eventos" / ("%s-%s.jsonl" % (when.strftime("%Y-%m"), _machine(machine)))


def _append(path, entry):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def _new_id(prefix, path, when, machine):
    count = 1
    if path.exists():
        with path.open(encoding="utf-8") as stream:
            count = sum(1 for _ in stream) + 1
    return "%s-%s-%s-%d" % (prefix, when.strftime("%Y%m%d-%H%M%S"), _machine(machine), count)


def record(root, machine, origem, acao, analisado=None, **fields):
    when = datetime.datetime.now().astimezone()
    path = _path(root, machine, when)
    entry = dict(id=_new_id("ev", path, when, machine), ts=when.isoformat(timespec="seconds"), origem=origem, acao=acao)
    entry.update({k: v for k, v in fields.items() if v is not None})
    if analisado if analisado is not None else origem == "agente":
        entry["analisado"] = True
    _append(path, entry)
    return entry


def analyze(root, machine, ids, resultado, actor="agente"):
    if not ids:
        raise ValueError("Informe os eventos analisados")
    known = {e["id"] for e in read_all(root)}
    missing = [i for i in ids if i not in known]
    if missing:
        raise ValueError("Eventos inexistentes: " + ", ".join(missing))
    when = datetime.datetime.now().astimezone()
    path = _path(root, machine, when)
    entry = dict(id=_new_id("an", path, when, machine), ts=when.isoformat(timespec="seconds"), origem=actor,
                 acao="analise", eventos=list(dict.fromkeys(ids)), resultado=resultado)
    _append(path, entry)
    return entry


def read_all(root, months=None):
    """Eventos de todas as máquinas; `months` limita aos arquivos mais recentes."""
    files = sorted(Path(root, "eventos").glob("*.jsonl"))
    if months:
        keep = sorted({f.name[:7] for f in files})[-months:]
        files = [f for f in files if f.name[:7] in keep]
    entries = []
    for path in files:
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except ValueError:
                    continue  # linha parcial de outra máquina não derruba a leitura
    entries.sort(key=lambda e: (e.get("ts", ""), e.get("id", "")))
    return entries


def pending(root, months=None):
    entries = read_all(root, months)
    analyzed = {i for e in entries if e.get("acao") == "analise" for i in e.get("eventos", [])}
    return [e for e in entries if e.get("acao") != "analise" and not e.get("analisado") and e["id"] not in analyzed]
