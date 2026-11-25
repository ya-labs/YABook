#!/usr/bin/env python3
"""CLI de `$yabook diff`: sessões capturadas pelo hook, arquivos alterados e `.patch`."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diff_runtime import compare, store  # noqa: E402


def config():
    path = Path(os.environ.get("YABOOK_CONFIG", str(Path.home() / ".config/yabook/config.json"))).expanduser()
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def project_root(path):
    result = subprocess.run(["git", "-C", str(path), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else str(Path(path).resolve())


def pick(base, root, wanted):
    """Sessão pedida por prefixo da chave; padrão é a atualizada mais recentemente."""
    found = store.sessions(base, root)
    if not found:
        raise ValueError("Nenhuma sessão de diff para " + root + "; a captura começa na próxima edição do agente.")
    if wanted in (None, "", "ultima"):
        return found[0]
    matches = [row for row in found if row[1]["sessao"].startswith(wanted)]
    if len(matches) != 1:
        raise ValueError("Sessão não encontrada ou ambígua: " + wanted)
    return matches[0]


def summary(folder, data, files):
    return dict(sessao=data["sessao"], pasta=str(folder), manifesto=str(Path(folder) / "manifest.json"),
                projeto=data["projeto"], agente=data.get("agente", ""), criada=data["criada"],
                atualizada=data["atualizada"], arquivos=files)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projeto", default=os.getcwd(), help="Diretório do projeto; padrão: atual")
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("sessions", help="Lista as sessões de diff do projeto")
    listing.add_argument("--json", action="store_true")
    show = sub.add_parser("show", help="Arquivos alterados na sessão")
    show.add_argument("--sessao")
    show.add_argument("--json", action="store_true")
    patch = sub.add_parser("patch", help="Grava o .patch da sessão")
    patch.add_argument("--sessao")
    patch.add_argument("--saida")
    args = parser.parse_args(argv)

    base, root = store.settings(config())["base"], project_root(args.projeto)
    if args.command == "sessions":
        rows = [dict(sessao=d["sessao"], atualizada=d["atualizada"], agente=d.get("agente", ""),
                     arquivos=len(d["arquivos"]), pasta=str(f)) for f, d in store.sessions(base, root)]
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        for row in [] if args.json else rows:
            print(f"{row['sessao']}  {row['atualizada']}  {row['agente'] or '-'}  {row['arquivos']} arquivo(s)")
        return 0
    folder, data = pick(base, root, args.sessao)
    if args.command == "show":
        files = compare.changes(folder, data)
        if args.json:
            print(json.dumps(summary(folder, data, files), ensure_ascii=False, indent=2))
            return 0
        print(f"Sessão {data['sessao']} ({data['atualizada']}): {len(files)} arquivo(s) alterado(s)")
        for item in files:
            print(f"  {item['estado']:<9} +{item['adicionadas']} -{item['removidas']}  {item['caminho']}")
        return 0
    print(compare.patch(folder, data, args.saida))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as error:
        print("yabook diff: " + str(error), file=sys.stderr)
        sys.exit(1)
