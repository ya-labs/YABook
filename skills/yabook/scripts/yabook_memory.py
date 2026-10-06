#!/usr/bin/env python3
"""CLI de serviços; o agente YABook prepara avaliações e obtém a aprovação."""
import argparse
import json
import sys

from memory_runtime.core import Vault, read_json


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
    args = parser.parse_args()
    vault = Vault(args.root)
    if args.command == "bootstrap":
        result = vault.bootstrap(args.owner)
    elif args.command == "prepare":
        payload = read_json(args.input)
        result = vault.prepare(payload["changes"], payload["assessment"], args.actor)
    elif args.command == "pending":
        result = vault.proposal(args.id)
    elif args.command == "apply":
        result = vault.apply(args.id, args.approval_hash)
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
