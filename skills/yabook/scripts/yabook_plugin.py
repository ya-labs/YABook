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


def register_codex(home, remove=False):
    home = Path(home).expanduser().resolve()
    registry = home / ".agents/plugins/marketplace.json"
    data = read_json(registry) if registry.exists() else dict(name="yabook-local",interface=dict(displayName="YABook local"),plugins=[])
    if not isinstance(data.get("plugins"), list) or not isinstance(data.get("name"), str):
        raise ValueError("Marketplace existente tem formato incompatível")
    existing = next((p for p in data["plugins"] if p.get("name") == "yabook"), None)
    if existing and not (existing.get("source", {}).get("source") == "local" and
                         existing["source"].get("path", "").startswith("./.local/share/yabook/plugins/")):
        raise ValueError("Entrada yabook existente não pertence a este instalador")
    if remove:
        if existing:
            data["plugins"].remove(existing); write_json(registry, data)
        return dict(status="unregistered",preserved="pacotes, configuração do host e memória")
    root = Path(__file__).resolve().parents[3]
    relative = ".local/share/yabook/plugins/" + fingerprint(root)
    destination = home / relative
    if destination.exists():
        if fingerprint(destination) != fingerprint(root): raise ValueError("Pacote instalado foi alterado")
    else: build(destination)
    entry = dict(name="yabook",source=dict(source="local",path="./"+relative),
                 policy=dict(installation="AVAILABLE",authentication="ON_INSTALL"),category="Productivity")
    if existing: data["plugins"][data["plugins"].index(existing)] = entry
    else: data["plugins"].append(entry)
    write_json(registry, data)
    return dict(status="registered",path=str(destination),marketplace=data["name"],
                enable=f'[plugins."yabook@{data["name"]}"]\nenabled = true')


def build(destination):
    root = Path(__file__).resolve().parents[3]
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
    args = parser.parse_args()
    if args.command in ("install-codex", "uninstall-codex"):
        result = register_codex(args.home, remove=args.command == "uninstall-codex")
    else:
        result = str(build(args.output)) if args.command == "build" else migrate_guardrails(args.agents, args.receipt)
    print(json.dumps({"result": result}, ensure_ascii=False))


if __name__ == "__main__": main()
