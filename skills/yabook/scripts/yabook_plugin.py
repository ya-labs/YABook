#!/usr/bin/env python3
"""Empacotamento reproduzível; instalação local sem sobrescrever configuração."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from memory_runtime.core import read_json, write_json


def fingerprint(root):
    files = [root / "plugin.json"]
    for directory in ("assets", "hooks", ".claude-plugin", "skills/yabook"):
        files += [p for p in (root / directory).rglob("*") if p.is_file()
                  and "__pycache__" not in p.parts and "tests" not in p.relative_to(root).parts and p.suffix != ".pyc"]
    result = hashlib.sha256()
    for path in sorted(files):
        result.update(str(path.relative_to(root)).encode()); result.update(b"\0"); result.update(path.read_bytes())
    return result.hexdigest()[:16]


def register_codex(*args, **kwargs):
    """Alias compatível para o adaptador Codex."""
    from host_codex import register_codex as register
    return register(*args, **kwargs)


def build(destination, source=None):
    root = Path(source).resolve() if source else Path(__file__).resolve().parents[3]
    from plugin_sync import validate_package
    validate_package(root)
    destination = Path(destination).expanduser().resolve()
    if destination == root or root in destination.parents:
        raise ValueError("Construa fora do checkout para não copiar a saída recursivamente")
    if destination.exists():
        raise ValueError("Destino já existe; escolha uma nova pasta para preservar instalação")
    destination.mkdir(parents=True)
    for filename in ("plugin.json",): shutil.copy2(root / filename, destination / filename)
    for directory in ("assets", "hooks", ".claude-plugin", "skills/yabook"):
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
    for name in ("install-codex", "uninstall-codex"):
        c = sub.add_parser(name); c.add_argument("--home", default=str(Path.home()))
    s = sub.add_parser("sync", help="Compara ou atualiza o plugin pelo adaptador do host")
    s.add_argument("--source", required=True)
    s.add_argument("--installed", required=True)
    s.add_argument("--home", default=str(Path.home()))
    s.add_argument("--apply", action="store_true")
    s.add_argument("--adapter", choices=["auto", "codex", "directory"], default="auto")
    i = sub.add_parser("install", help="Instalação portátil em diretório gerenciado")
    i.add_argument("--source", required=True); i.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "sync":
        from plugin_sync import sync_plugin
        result = sync_plugin(args.source, args.installed, args.home, apply=args.apply, adapter=args.adapter)
    elif args.command == "install":
        from host_directory import sync_directory
        result = sync_directory(args.source, args.output, apply=True)
    elif args.command in ("install-codex", "uninstall-codex"):
        result = register_codex(args.home, remove=args.command == "uninstall-codex")
    else:
        result = str(build(args.output)) if args.command == "build" else migrate_guardrails(args.agents, args.receipt)
    print(json.dumps({"result": result}, ensure_ascii=False))


if __name__ == "__main__": main()
