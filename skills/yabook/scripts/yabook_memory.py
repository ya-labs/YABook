#!/usr/bin/env python3
"""CLI de serviços; o agente YABook prepara avaliações e obtém a aprovação."""
import argparse
import json
import sys

from memory_runtime.core import Vault, read_json
from memory_runtime.gitstore import apply_and_publish, init_plan, init_apply, inventory, publish
from memory_runtime.sources import source_add, refresh, sync, all_entries
from memory_runtime.search import search, export_vectors, import_vectors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Base local da memória")
    sub = parser.add_subparsers(dest="command", required=True)
    bootstrap = sub.add_parser("bootstrap")
    bootstrap.add_argument("--owner", required=True)
    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("id")
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--input", required=True)
    prepare.add_argument("--actor", required=True)
    pending = sub.add_parser("pending")
    pending.add_argument("id", nargs="?")
    apply = sub.add_parser("apply")
    apply.add_argument("id")
    apply.add_argument("--approval-hash", required=True)
    sub.add_parser("review")
    sub.add_parser("recover")
    inv = sub.add_parser("inventory")
    inv.add_argument("--agent", choices=["codex", "claude"], required=True)
    inv.add_argument("--source", required=True)
    ini = sub.add_parser("init-plan")
    ini.add_argument("--agent", choices=["codex", "claude"], required=True)
    ini.add_argument("--source", required=True)
    ini.add_argument("--curated")
    ini.add_argument("--output", required=True)
    ai = sub.add_parser("init-apply")
    ai.add_argument("--plan", required=True)
    ai.add_argument("--curated", required=True)
    ai.add_argument("--approval-hash", required=True)
    ai.add_argument("--config", required=True)
    sub.add_parser("publish")
    source = sub.add_parser("source-add")
    source.add_argument("--input", required=True)
    sub.add_parser("sync")
    lookup = sub.add_parser("search")
    lookup.add_argument("query")
    lookup.add_argument("--scope", action="append", default=[], help="Componentes separados por /")
    lookup.add_argument("--limit", type=int, default=8)
    lookup.add_argument("--budget", type=int, default=6000)
    lookup.add_argument("--model")
    lookup.add_argument("--embedding-url", default="http://127.0.0.1:11434/api/embed")
    ve = sub.add_parser("vectors-export"); ve.add_argument("--output", required=True)
    vi = sub.add_parser("vectors-import"); vi.add_argument("--input", required=True)
    args = parser.parse_args()
    vault = Vault(args.root)
    if args.command == "search":
        result = search(vault, args.query, includes=[s.split("/") for s in args.scope], limit=args.limit,
                        budget=args.budget, model=args.model, endpoint=args.embedding_url)
    elif args.command == "vectors-export":
        result = export_vectors(vault, args.output)
    elif args.command == "vectors-import":
        result = import_vectors(vault, read_json(args.input))
    elif args.command == "source-add":
        result = source_add(vault, read_json(args.input))
    elif args.command == "sync":
        result = sync(vault)
    elif args.command == "inventory":
        result = inventory(args.agent, args.source)
    elif args.command == "init-plan":
        from memory_runtime.core import write_json
        result = init_plan(args.root, args.agent, args.source, read_json(args.curated) if args.curated else None)
        write_json(args.output, result)
    elif args.command == "init-apply":
        result = init_apply(read_json(args.plan), args.approval_hash, read_json(args.curated), args.config)
    elif args.command == "publish":
        result = publish(vault)
    elif args.command == "bootstrap":
        result = vault.bootstrap(args.owner)
    elif args.command == "prepare":
        payload = read_json(args.input)
        result = vault.prepare(payload["changes"], payload["assessment"], args.actor)
    elif args.command == "pending":
        result = vault.proposal(args.id)
    elif args.command == "apply":
        result = apply_and_publish(vault, args.id, args.approval_hash)
    elif args.command == "recover":
        result = vault.recover()
    elif args.command == "review":
        result = vault.review()
    else:
        entries = list(vault.entries(include_archived=True)) if args.command == "show" else all_entries(vault)
        result = next((x for x in entries if x["id"] == args.id), None) if args.command == "show" else entries
        if result is None:
            raise ValueError("Registro não encontrado")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
