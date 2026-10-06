#!/usr/bin/env python3
"""CLI de serviços; o agente YABook prepara avaliações e obtém a aprovação."""
import argparse
import json
import sys

from memory_runtime.core import Vault, read_json
from memory_runtime.gitstore import apply_and_publish, init_plan, init_apply, inventory, publish


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
    args = parser.parse_args()
    vault = Vault(args.root)
    if args.command == "inventory":
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
        entries = list(vault.entries(include_archived=args.command == "show"))
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
