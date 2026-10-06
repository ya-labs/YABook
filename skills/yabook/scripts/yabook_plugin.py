#!/usr/bin/env python3
"""Empacotamento reproduzível; instalação local sem sobrescrever configuração."""
import argparse
import json
import shutil
from pathlib import Path


def build(destination):
    root = Path(__file__).resolve().parents[3]
    destination = Path(destination).expanduser().resolve()
    if destination == root or root in destination.parents:
        raise ValueError("Construa fora do checkout para não copiar a saída recursivamente")
    if destination.exists():
        raise ValueError("Destino já existe; escolha uma nova pasta para preservar instalação")
    destination.mkdir(parents=True)
    for filename in ("plugin.json",): shutil.copy2(root / filename, destination / filename)
    for directory in ("hooks", ".claude-plugin", "skills/yabook"):
        shutil.copytree(root / directory, destination / directory,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tests"))
    return destination


def migrate_guardrails(agents, receipt):
    from memory_runtime.core import read_json
    proof = read_json(receipt)
    if not proof.get("startup_seen") or not proof.get("pretool_seen"):
        raise ValueError("Uma sessão real deve ter observado SessionStart e PreToolUse")
    path = Path(agents)
    text = path.read_text(encoding="utf-8")
    start, end = "<!-- YABOOK-GUARDRAILS:START -->", "<!-- YABOOK-GUARDRAILS:END -->"
    if text.count(start) != 1 or text.count(end) != 1 or text.index(end) < text.index(start):
        raise ValueError("Bloco ausente, duplicado ou incompleto")
    canonical = (Path(__file__).resolve().parents[1] / "references/guardrails.md").read_text(encoding="utf-8")
    a, b = text.index(start), text.index(end) + len(end)
    if text[a:b] not in canonical:
        raise ValueError("Bloco divergente: revisão manual necessária")
    backup = path.with_name(path.name + ".before-yabook-plugin")
    if backup.exists(): raise ValueError("Backup já existe; não sobrescrever")
    shutil.copy2(path, backup)
    path.write_text(text[:a] + text[b:], encoding="utf-8")
    return str(backup)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build"); b.add_argument("--output", required=True)
    m = sub.add_parser("migrate-guardrails"); m.add_argument("--agents", required=True); m.add_argument("--receipt", required=True)
    args = parser.parse_args()
    result = str(build(args.output)) if args.command == "build" else migrate_guardrails(args.agents, args.receipt)
    print(json.dumps({"result": result}, ensure_ascii=False))


if __name__ == "__main__": main()
