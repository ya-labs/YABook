#!/usr/bin/env python3
"""CLI de serviços; o agente YABook prepara avaliações e obtém a aprovação."""
import argparse
import json
import os
import sys
from pathlib import Path

from memory_runtime.core import Vault, read_json
from memory_runtime.gitstore import apply_and_publish, init_plan, init_apply, inventory, publish
from memory_runtime.sources import source_add, refresh, sync, all_entries
from memory_runtime.search import search, export_vectors, import_vectors
from memory_runtime.map import export_map, serve


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
    learning = sub.add_parser("learn", help="Aplica um lote curado pela política de aprendizado")
    learning.add_argument("--input", required=True)
    learning.add_argument("--actor", required=True)
    learning.add_argument("--workspace", default=os.getcwd())
    learning.add_argument("--config", default=os.environ.get("YABOOK_CONFIG", str(Path.home() / ".config/yabook/config.json")))
    policy = sub.add_parser("learning-policy")
    policy.add_argument("--mode", required=True, choices=["automatic", "manual"])
    policy.add_argument("--config", default=os.environ.get("YABOOK_CONFIG", str(Path.home() / ".config/yabook/config.json")))
    recent = sub.add_parser("recent")
    recent.add_argument("--limit", type=int, default=10)
    pending = sub.add_parser("pending")
    pending.add_argument("id", nargs="?")
    apply = sub.add_parser("apply")
    apply.add_argument("id")
    apply.add_argument("--approval-hash", required=True)
    sub.add_parser("review")
    sub.add_parser("recover")
    inv = sub.add_parser("inventory")
    inv.add_argument("--agent", required=True, help="Nome do agente de origem, sem lista fechada")
    inv.add_argument("--source", required=True)
    ini = sub.add_parser("init-plan")
    ini.add_argument("--agent", required=True, help="Nome do agente de origem")
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
    lookup.add_argument("--kind", action="append", default=[])
    lookup.add_argument("--level", choices=["all", "index", "knowledge", "experience"], default="all")
    lookup.add_argument("--embedding-url", default="http://127.0.0.1:11434/api/embed")
    index = sub.add_parser("index", help="Índice por tipo, projeto e assunto")
    index.add_argument("--scope", action="append", default=[])
    context = sub.add_parser("context", help="Perfil, preferências explícitas e índice inicial")
    context.add_argument("--scope", default="")
    context.add_argument("--budget", type=int, default=4500)
    retrieve = sub.add_parser("retrieve", help="Recuperação em camadas")
    retrieve.add_argument("query"); retrieve.add_argument("--scope", action="append", default=[])
    retrieve.add_argument("--budget", type=int, default=6000)
    retrieve.add_argument("--experiences", action="store_true")
    retrieve.add_argument("--evidence", action="store_true")
    retrieve.add_argument("--model")
    ve = sub.add_parser("vectors-export"); ve.add_argument("--output", required=True)
    vi = sub.add_parser("vectors-import"); vi.add_argument("--input", required=True)
    visual = sub.add_parser("map")
    visual.add_argument("--output")
    visual.add_argument("--serve", action="store_true")
    visual.add_argument("--port", type=int, default=8765)
    visual.add_argument("--scope", action="append", default=[])
    args = parser.parse_args()
    vault = Vault(args.root)
    if args.command == "index":
        from memory_runtime.views import overview
        result = overview(all_entries(vault, [s.split("/") for s in args.scope]))
    elif args.command == "context":
        from memory_runtime.views import session_context
        result = session_context(vault, args.scope.split("/") if args.scope else [], args.budget)
    elif args.command == "retrieve":
        from memory_runtime.retrieval import retrieve
        result = retrieve(vault, args.query, [s.split("/") for s in args.scope], args.budget,
                          args.experiences, args.evidence, args.model)
    elif args.command == "map":
        scopes=[s.split("/") for s in args.scope]
        if args.serve:
            serve(vault,args.port,scopes); return
        if not args.output: raise ValueError("Informe --output ou --serve")
        result=export_map(vault,args.output,scopes)
    elif args.command == "search":
        result = search(vault, args.query, includes=[s.split("/") for s in args.scope], limit=args.limit,
                        budget=args.budget, model=args.model, endpoint=args.embedding_url,
                        kinds=args.kind, level=args.level)
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
    elif args.command == "learn":
        from memory_runtime.learning import learn
        result = learn(vault, read_json(args.input), args.actor, args.config, args.workspace)
    elif args.command == "learning-policy":
        from memory_runtime.learning import set_policy
        result = set_policy(args.config, vault.root, args.mode)
    elif args.command == "recent":
        from memory_runtime.learning import recent
        result = recent(vault, args.limit)
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
