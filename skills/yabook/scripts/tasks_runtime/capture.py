"""Captura do YABook Tasks pelos hooks do plugin (Claude Code e Codex).

- SessionStart: pull rápido, tarefa ativa sugerida, perguntas, prazos e eventos.
- UserPromptSubmit: marca a janela de 15 minutos da tarefa ativa, só local.
- Stop: commit local idempotente; push em lote, em segundo plano.

Nada aqui pode bloquear o prompt: o despachante captura qualquer erro.
"""
import datetime
import json
import os
import re
import subprocess
import unicodedata
import sys
import time
from pathlib import Path

from . import events
from .store import TaskStore, atomic_write, now

WINDOW_MINUTES = 15
PUSH_INTERVAL = 30 * 60
MAX_EVENTS = 10
REASK_AFTER = 8
RULES = ("Mantenha as tarefas sem pedido, conforme a política: etapa concluída vira registro e próximo passo "
         "(task edit --append), dúvida que depende da pessoa vira task ask, prazo citado vai para a tarefa e mudança "
         "de fase move a coluna. Conversa anterior sem registro: task capture.")
SIGNAL = re.compile(r"#\d+|\b(prazo|entrega|amanha|segunda|terca|quarta|quinta|sexta|\d{1,2}/\d{1,2}"
                    r"|(chamado|projeto|demanda|issue|pr) ?#?\d{2,}"
                    r"|termin\w*|conclu\w*|finaliz\w*|resolv\w*|pendente|pendencia|bloquead\w*|aguardando)\b")
COMMIT_MESSAGE = "chore: registra atividade do YABook Tasks"
_GIT_ENV = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_ASKPASS="true")


def _git(root, *args, timeout=8):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=timeout, env=_GIT_ENV)


def _read(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _session_file(store, session):
    return store.root / "local" / "sessoes" / (session + ".json")


def open_store(cfg):
    tasks = (cfg or {}).get("tasks") or {}
    if not tasks.get("root") or not Path(tasks["root"], "quadro.yml").is_file():
        return None, tasks
    return TaskStore(tasks["root"], tasks.get("terms")), tasks


def active(store, session):
    """Tarefa ativa da sessão; sem escolha na sessão, a última iniciada na máquina."""
    chosen = _read(_session_file(store, session), {}).get("ativa")
    return chosen or _read(store.root / "local" / "ativa.json", {}).get("id")


def recent(stamp, seconds=300):
    try:
        moment = datetime.datetime.fromisoformat(stamp)
    except (TypeError, ValueError):
        return False
    return abs((datetime.datetime.now().astimezone() - moment).total_seconds()) <= seconds


def set_active(store, session, identifier):
    store.get(identifier)
    path = _session_file(store, session)
    state = dict(_read(path, {}), ativa=identifier, desde=now())
    atomic_write(path, json.dumps(state, ensure_ascii=False) + "\n")
    return state


def suggest(store, session):
    roles = {c["id"]: c["papel"] for c in store.columns()}
    tasks = {t["data"]["id"]: t["data"] for t in store.list() if t["data"].get("tipo") != "pergunta"}
    current = active(store, session)
    if current in tasks and roles.get(tasks[current].get("coluna")) in ("ativo", "pronto", "validacao"):
        return tasks[current]
    for papel in ("ativo", "pronto"):
        candidates = sorted((t for t in tasks.values() if roles.get(t.get("coluna")) == papel),
                            key=lambda t: (t.get("ordem", 0), t["id"]))
        if candidates:
            return candidates[0]
    return None


def _label(task):
    codes = [task[k] for k in ("demanda", "projeto") if task.get(k)]
    return "%s — %s%s" % (task["id"], task["titulo"], (" [" + "/".join(codes) + "]") if codes else "")


def _event_line(entry):
    detail = entry.get("tarefa") or entry.get("coluna") or ""
    move = " %s→%s" % (entry["de"], entry["para"]) if entry.get("de") and entry.get("para") else ""
    return "%s %s %s%s" % (entry["id"], entry["acao"], detail, move)


def session_start(cfg, session, source="startup"):
    store, tasks_cfg = open_store(cfg)
    if store is None:
        return ""
    pulled = _pull(store)
    from .commands import Tasks
    review = Tasks(store, tasks_cfg).review()
    lines = ["YABook Tasks:"]
    current = suggest(store, session)
    if current:
        lines.append("Tarefa ativa sugerida: %s. Confirme com a pessoa uma vez nesta sessão; após a resposta, "
                     "rode task start com a escolhida." % _label(current))
    else:
        lines.append("Sem tarefa ativa; pergunte uma vez se a sessão pertence a alguma tarefa (task start ou task add).")
    lines.append(RULES)
    if review["perguntas"]:
        lines.append("Perguntas abertas para a pessoa: " + "; ".join(_label(t) for t in review["perguntas"][:5]))
    due = review["atrasadas"] + review["proximas"]
    if due:
        lines.append("Prazos: " + "; ".join("%s (%s)" % (_label(t), t["prazo"]) for t in due[:5]))
    waiting = events.pending(store.root, months=2)
    if waiting:
        shown = waiting[:MAX_EVENTS]
        lines.append("Ações do quadro não analisadas: " + "; ".join(_event_line(e) for e in shown)
                     + (" (+%d)" % (len(waiting) - len(shown)) if len(waiting) > len(shown) else "")
                     + ". Analise no fim da resposta se não tiver relação com o pedido e registre com task analyze.")
    path = _session_file(store, session)
    state = _read(path, {})
    state["avisados"] = [e["id"] for e in waiting]
    atomic_write(path, json.dumps(state, ensure_ascii=False) + "\n")
    if not pulled:
        lines.append("Pull do repositório de tarefas não concluído; dados podem estar atrasados.")
    return "\n".join(lines)[:1500]


def _plain(text):
    return unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()


def prompt(cfg, session, when=None, text=""):
    store, tasks_cfg = open_store(cfg)
    if store is None:
        return ""
    when = when or datetime.datetime.now().astimezone()
    current = active(store, session)
    if current and store.exists(current):
        mark(store, tasks_cfg.get("machine"), current, when)
    else:
        current = None
    path = _session_file(store, session)
    state = _read(path, {})
    changed, lines = False, []
    if current is None:
        # Sem escolha na sessão: pergunta de novo uma vez, depois de algumas mensagens.
        state["sem_ativa"] = state.get("sem_ativa", 0) + 1
        changed = True
        if state["sem_ativa"] == REASK_AFTER:
            lines.append("YABook Tasks: sessão ainda sem tarefa ativa e as horas não estão contando; pergunte de novo "
                         "a qual tarefa ela pertence (task start, task add ou task capture).")
    if text and SIGNAL.search(_plain(text)):
        start = window(when)[1]
        if state.get("lembrete") != start:
            state["lembrete"], changed = start, True
            lines.append("YABook Tasks: a mensagem cita prazo, código ou conclusão; ao responder, atualize a tarefa "
                         "correspondente (task edit, add ou ask) conforme a política.")
    seen = set(state.get("avisados", []))
    fresh = [e for e in events.pending(store.root, months=1) if e["id"] not in seen]
    if fresh:
        state["avisados"], changed = sorted(seen | {e["id"] for e in fresh}), True
        lines.append("YABook Tasks: %d nova(s) ação(ões) do quadro não analisada(s): %s." % (
            len(fresh), "; ".join(_event_line(e) for e in fresh[:3])))
    if changed:
        atomic_write(path, json.dumps(state, ensure_ascii=False) + "\n")
    return "\n".join(lines)


def window(when):
    minute = when.minute - when.minute % WINDOW_MINUTES
    return when.strftime("%Y-%m-%d"), "%02d:%02d" % (when.hour, minute)


def mark(store, machine, identifier, when):
    """Marca a janela uma vez por tarefa; repetir o hook não duplica a marca."""
    day, start = window(when)
    cache = store.root / "local" / "janelas.json"
    with store.lock():
        seen = _read(cache, {})
        if seen.get("data") != day:
            seen = dict(data=day, marcas=[])
        key = start + " " + identifier
        if key in seen["marcas"]:
            return False
        machine = events._machine(machine)
        path = store.root / "horas" / ("%s-%s.jsonl" % (day[:7], machine))
        path.parent.mkdir(exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(dict(tipo="janela", data=day, janela=start, tarefa=identifier),
                                    ensure_ascii=False, separators=(",", ":")) + "\n")
        seen["marcas"].append(key)
        atomic_write(cache, json.dumps(seen, ensure_ascii=False) + "\n")
        return True


def stop(cfg, config_path=None, spawn=True):
    store, _ = open_store(cfg)
    if store is None:
        return dict(commit=None, push=False)
    commit = None
    with store.lock():
        if _git(store.root, "rev-parse", "--is-inside-work-tree").returncode:
            return dict(commit=None, push=False)
        if _git(store.root, "status", "--porcelain").stdout.strip():
            _git(store.root, "add", "-A")
            if _git(store.root, "diff", "--cached", "--quiet").returncode:
                result = _git(store.root, "commit", "-q", "-m", COMMIT_MESSAGE)
                if not result.returncode:
                    commit = _git(store.root, "rev-parse", "--short", "HEAD").stdout.strip()
    marker = store.root / "local" / "ultimo-push"
    last = _read(marker, {}).get("ts", 0)
    due = time.time() - last >= PUSH_INTERVAL and _git(store.root, "rev-list", "--count", "@{upstream}..HEAD").stdout.strip() not in ("", "0")
    if due and spawn:
        atomic_write(marker, json.dumps(dict(ts=time.time())) + "\n")
        script = Path(__file__).resolve().parents[1] / "yabook_tasks.py"
        command = [sys.executable, str(script)] + (["--config", str(config_path)] if config_path else []) + ["sync"]
        subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True, env=_GIT_ENV)
    return dict(commit=commit, push=bool(due and spawn))


def _pull(store):
    """Pull curto; falha de rede ou conflito não bloqueia a sessão."""
    try:
        with store.lock():
            if _git(store.root, "rev-parse", "--abbrev-ref", "@{upstream}", timeout=3).returncode:
                return True
            result = _git(store.root, "-c", "rebase.autoStash=true", "pull", "--rebase", "-q", timeout=4)
            if result.returncode:
                _git(store.root, "rebase", "--abort", timeout=3)
                return False
            return True
    except (subprocess.TimeoutExpired, OSError):
        return False
