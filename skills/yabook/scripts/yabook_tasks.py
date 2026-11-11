#!/usr/bin/env python3
"""CLI do YABook Tasks; o agente interpreta o pedido e chama os serviços."""
import argparse
import json
import os
import sys
from pathlib import Path

from tasks_runtime import init as task_init
from tasks_runtime.store import TaskStore

CONFIG = os.environ.get("YABOOK_CONFIG", str(Path.home() / ".config/yabook/config.json"))


def machine_config(config_path):
    cfg = task_init.read_config(config_path).get("tasks")
    if not cfg or not cfg.get("root"):
        raise ValueError("YABook Tasks não configurado nesta máquina; rode task init")
    return cfg


def open_store(config_path):
    cfg = machine_config(config_path)
    return TaskStore(cfg["root"], cfg.get("terms")), cfg


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=CONFIG)
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("init-plan", help="Prévia do task init, sem alterar nada")
    plan.add_argument("--repository", help="proprietário/nome; padrão YABook-task-<login>")
    plan.add_argument("--root", help="Pasta local do repositório de dados")
    plan.add_argument("--machine", help="Nome desta máquina nos arquivos por máquina")
    plan.add_argument("--confidential", help="Pasta da base confidencial local")
    plan.add_argument("--terms", help="Arquivo local de termos proibidos")
    plan.add_argument("--output", required=True)
    apply = sub.add_parser("init-apply", help="Aplica o plano aprovado (do task init)")
    apply.add_argument("--plan", required=True)
    apply.add_argument("--approval-hash", required=True)
    sub.add_parser("validate", help="Valida quadro, configuração e todas as tarefas")
    return parser


def run(args):
    if args.command == "init-plan":
        result = task_init.init_plan(args.config, args.repository, args.root, args.machine, args.confidential, args.terms)
        task_init.write_config(args.output, result)
        return dict(result, output=str(Path(args.output).expanduser().resolve()))
    if args.command == "init-apply":
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        return task_init.init_apply(plan, args.approval_hash, args.config)
    if args.command == "validate":
        store, _ = open_store(args.config)
        store.config()
        errors = []
        tasks = store.list()
        for task in tasks:
            try:
                store.validate(store.normalize(task["data"]))
            except ValueError as exc:
                errors.append(dict(id=task["data"].get("id"), error=str(exc)))
        return dict(ok=not errors, tasks=len(tasks), errors=errors)
    raise ValueError("Comando desconhecido: " + args.command)


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        result = run(args)
    except (ValueError, KeyError) as exc:
        print(json.dumps(dict(error=str(exc).strip("'\"")), ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
