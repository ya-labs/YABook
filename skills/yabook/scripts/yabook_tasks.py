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
    sub.add_parser("summary", help="Resumo: ativas, prazos, perguntas e colunas")
    show = sub.add_parser("show")
    show.add_argument("id")
    search = sub.add_parser("search")
    search.add_argument("query", nargs="?", default="")
    search.add_argument("--tipo")
    search.add_argument("--coluna")
    search.add_argument("--projeto", help="Inclui as tarefas que herdam o projeto pelo pai")
    search.add_argument("--nivel", choices=["epico", "historia", "tarefa"])
    search.add_argument("--pai")
    search.add_argument("--limit", type=int, default=20)
    recent = sub.add_parser("recent")
    recent.add_argument("--limit", type=int, default=10)
    sub.add_parser("review", help="Perguntas abertas, prazos, tarefas sem prazo e paradas")
    add = sub.add_parser("add", help="Cria tarefa com campos já interpretados pelo agente")
    add.add_argument("--tipo", required=True)
    add.add_argument("--titulo", required=True)
    edit = sub.add_parser("edit")
    edit.add_argument("id")
    edit.add_argument("--titulo")
    edit.add_argument("--tipo")
    edit.add_argument("--unset", action="append", default=[], help="Remove o campo")
    edit.add_argument("--append", help="Acrescenta linha ao registro da tarefa")
    edit.add_argument("--revision", help="Revisão lida; recusa se a tarefa mudou")
    for command in (add, edit):
        command.add_argument("--coluna")
        command.add_argument("--prazo", help="AAAA-MM-DD, DD/MM, hoje, amanhã, +Nd ou dia da semana")
        command.add_argument("--projeto")
        command.add_argument("--demanda")
        command.add_argument("--issue", action="append", help="dono/repo#n, repetível")
        command.add_argument("--ref", action="append", help="confidencial:|yabook:|github:, repetível")
        command.add_argument("--proximo-passo")
        command.add_argument("--sobre")
        command.add_argument("--ordem", type=int)
        command.add_argument("--nivel", choices=["epico", "historia", "tarefa"])
        command.add_argument("--pai", help="Id do épico ou da história acima")
        command.add_argument("--pessoal", choices=["sim", "nao"], help="Sem a opção, vem calculado; --unset pessoal volta ao cálculo")
    add.add_argument("--body", default="")
    forget = sub.add_parser("forget", help="Arquiva sem apagar")
    forget.add_argument("id")
    forget.add_argument("--motivo")
    start = sub.add_parser("start", help="Define a tarefa ativa")
    start.add_argument("id")
    ask = sub.add_parser("ask", help="Registra pergunta pendente do agente")
    ask.add_argument("pergunta")
    ask.add_argument("--sobre")
    answer = sub.add_parser("answer")
    answer.add_argument("id")
    answer.add_argument("resposta")
    log = sub.add_parser("log", help="Lança horas manuais")
    log.add_argument("id")
    log.add_argument("horas")
    log.add_argument("obs", nargs="?")
    log.add_argument("--data")
    sub.add_parser("sync", help="Commit local, pull com rebase e push")
    clean = sub.add_parser("clean", help="Faxina: concluídas antigas e duplicatas")
    clean.add_argument("--days", type=int, default=30)
    clean.add_argument("--apply", action="store_true")
    sheet = sub.add_parser("sheet", help="Ficha de horas sugerida do dia ou da semana")
    sheet.add_argument("--data", help="Dia de referência; padrão hoje")
    sheet.add_argument("--semana", action="store_true")
    sheet.add_argument("--confirm", action="store_true", help="Grava os totais do dia")
    sheet.add_argument("--input", help="JSON com linhas e extras ajustados para --confirm")
    history = sub.add_parser("events", help="Histórico de ações")
    history.add_argument("--pending", action="store_true", help="Só ações do quadro não analisadas")
    history.add_argument("--limit", type=int, default=30)
    analyze = sub.add_parser("analyze", help="Registra a análise de ações do quadro")
    analyze.add_argument("--id", action="append", required=True)
    analyze.add_argument("--resultado", required=True)
    capture = sub.add_parser("capture", help="Cria ou atualiza em lote as tarefas levantadas de uma conversa")
    capture.add_argument("--input", required=True, help="JSON com itens, perguntas, ativa e horas")
    capture.add_argument("--apply", action="store_true", help="Grava; na política manual exige --approval-hash")
    capture.add_argument("--approval-hash", help="Hash da prévia apresentada")
    board = sub.add_parser("board", help="Site local: --serve inicia o servidor; --output gera cópia estática")
    board.add_argument("--serve", action="store_true", help="Serve em 127.0.0.1 até Ctrl+C")
    board.add_argument("--port", type=int, help="Porta; padrão `tasks.port` ou 8765")
    board.add_argument("--output", help="Arquivo ou pasta da cópia estática somente leitura")
    policy = sub.add_parser("policy")
    policy.add_argument("mode", choices=["automatic", "manual"])
    return parser


FIELDS = ("coluna", "prazo", "projeto", "demanda", "sobre", "ordem", "nivel", "pai")


def fields(args, existing=None):
    result = {k: getattr(args, k) for k in FIELDS if getattr(args, k, None) is not None}
    if getattr(args, "pessoal", None) is not None:
        result["pessoal"] = args.pessoal == "sim"
    if getattr(args, "proximo_passo", None) is not None:
        result["proximo_passo"] = args.proximo_passo
    for key, flag in (("issue", "issue"), ("refs", "ref")):
        values = getattr(args, flag, None)
        if values:
            result[key] = list(dict.fromkeys((existing or {}).get(key, []) + values))
    return result


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
    if args.command == "policy":
        from tasks_runtime.commands import set_policy
        return set_policy(args.config, args.mode)
    from tasks_runtime.commands import Tasks, sync
    store, cfg = open_store(args.config)
    tasks = Tasks(store, cfg)
    state = store.root / "local" / "ativa.json"
    if args.command == "summary":
        return tasks.summary(json.loads(state.read_text(encoding="utf-8")) if state.exists() else None)
    if args.command == "show":
        return tasks.show(args.id)
    if args.command == "search":
        return tasks.search(args.query, args.tipo, args.coluna, args.projeto, args.limit, args.nivel, args.pai)
    if args.command == "recent":
        return tasks.recent(args.limit)
    if args.command == "review":
        from tasks_runtime import events
        return dict(tasks.review(), eventos_pendentes=events.pending(store.root))
    if args.command == "add":
        return tasks.add(args.tipo, args.titulo, body=args.body, **fields(args))
    if args.command == "edit":
        current = store.get(args.id)["data"]
        changes = fields(args, current)
        for key in ("titulo", "tipo"):
            if getattr(args, key):
                changes[key] = getattr(args, key)
        return tasks.edit(args.id, changes, args.unset, args.append, args.revision)
    if args.command == "forget":
        return tasks.forget(args.id, args.motivo)
    if args.command == "start":
        return tasks.start(args.id, state)
    if args.command == "ask":
        return tasks.ask(args.pergunta, args.sobre)
    if args.command == "answer":
        return tasks.answer(args.id, args.resposta)
    if args.command == "log":
        return tasks.log(args.id, args.horas, args.obs, args.data)
    if args.command == "sync":
        return sync(store.root)
    if args.command == "sheet":
        from tasks_runtime import sheet
        from tasks_runtime.commands import parse_date, today
        day = parse_date(args.data) if args.data else today().isoformat()
        if args.confirm:
            if args.semana:
                raise ValueError("Confirme um dia por vez")
            adjusted = json.loads(Path(args.input).read_text(encoding="utf-8")) if args.input else {}
            entry = sheet.confirm(store, day, adjusted.get("linhas"), adjusted.get("extras"))
            tasks._event("confirmar-ficha", data=day, total=sum(r["total"] for r in entry["linhas"]))
            return entry
        build = sheet.week_sheet if args.semana else sheet.day_sheet
        return build(store, day, tasks.complement)
    if args.command == "events":
        from tasks_runtime import events
        entries = events.pending(store.root) if args.pending else events.read_all(store.root)
        return dict(total=len(entries), eventos=entries[-args.limit:])
    if args.command == "analyze":
        from tasks_runtime import events
        if tasks.find_terms_in(args.resultado):
            raise ValueError("Resultado com termo confidencial")
        return events.analyze(store.root, cfg.get("machine"), args.id, args.resultado)
    if args.command == "board":
        from tasks_runtime import server
        if args.output:
            return server.Board(store, cfg).export(args.output)
        if not args.serve:
            raise ValueError("Use --serve para iniciar o site ou --output para a cópia estática")
        return server.serve(store, cfg, args.port, writer=getattr(server, "WRITER", None))
    if args.command == "capture":
        from tasks_runtime.batch import Capture
        batch = json.loads(Path(args.input).read_text(encoding="utf-8"))
        capture = Capture(store, cfg)
        if not args.apply:
            return dict(capture.plan(batch), politica=cfg.get("policy", "automatic"))
        if cfg.get("policy") == "manual" and not args.approval_hash:
            raise ValueError("Política manual: apresente a prévia e aplique com --approval-hash após do task capture")
        return capture.apply(batch, args.approval_hash)
    if args.command == "clean":
        return tasks.clean(args.days, args.apply)
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
