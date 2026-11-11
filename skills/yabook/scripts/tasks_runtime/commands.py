"""Comandos `task`: consulta e escrita sobre o `TaskStore`.

O agente interpreta o texto livre da pessoa e chama estes serviços com campos
estruturados; datas relativas são resolvidas aqui para não depender do modelo.
"""
import datetime
import json
import re
import unicodedata
from pathlib import Path

from . import events, remote, tree
from .precommit_hook import find_terms
from .store import TIPOS, atomic_write, now

WEEKDAYS = ("segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo")
CLOSED = ("concluido", "arquivado")
OPEN_WORK = ("pronto", "ativo", "validacao")


def _plain(text):
    return " ".join(unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().casefold().split())


def today():
    return datetime.datetime.now().astimezone().date()


def parse_date(text, base=None):
    """Aceita AAAA-MM-DD, DD/MM[/AAAA], hoje, amanhã, +Nd e dia da semana."""
    base = base or today()
    value = _plain(str(text)).replace("-feira", "").replace(" feira", "")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return datetime.date.fromisoformat(value).isoformat()
    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", value)
    if match:
        day, month, year = int(match[1]), int(match[2]), match[3]
        if year:
            year = int(year) + (2000 if len(year) == 2 else 0)
            return datetime.date(year, month, day).isoformat()
        candidate = datetime.date(base.year, month, day)
        return (candidate if candidate >= base else datetime.date(base.year + 1, month, day)).isoformat()
    if value == "hoje":
        return base.isoformat()
    if value in ("amanha",):
        return (base + datetime.timedelta(days=1)).isoformat()
    match = re.fullmatch(r"\+(\d+)d", value)
    if match:
        return (base + datetime.timedelta(days=int(match[1]))).isoformat()
    for prefix in ("proxima ", "proximo ", "na ", "no "):
        if value.startswith(prefix):
            value = value[len(prefix):]
    if value in WEEKDAYS:
        delta = (WEEKDAYS.index(value) - base.weekday()) % 7 or 7
        return (base + datetime.timedelta(days=delta)).isoformat()
    raise ValueError("Prazo não reconhecido: %r; use AAAA-MM-DD, DD/MM, hoje, amanhã, +Nd ou dia da semana" % text)


class Tasks:
    def __init__(self, store, cfg=None, origem="agente"):
        self.store, self.cfg, self.origem = store, cfg or {}, origem

    def _event(self, acao, **fields):
        """Ação do agente entra analisada; a do quadro fica pendente até `analyze`."""
        return events.record(self.store.root, self.cfg.get("machine"), self.origem, acao, **fields)

    # Apoio ----------------------------------------------------------------
    def roles(self):
        return {c["id"]: c["papel"] for c in self.store.columns()}

    def first_column(self, papel):
        ids = self.store.column_ids(papel)
        if not ids:
            raise ValueError("Quadro sem coluna com papel " + papel)
        return ids[0]

    def next_order(self, column, tasks=None):
        orders = [t["data"].get("ordem", 0) for t in (tasks or self.store.list()) if t["data"].get("coluna") == column]
        return max(orders, default=0) + 1

    def brief(self, task, index=None):
        data = task["data"]
        keys = ("id", "tipo", "nivel", "titulo", "coluna", "pai", "projeto", "demanda", "issue", "prazo", "proximo_passo")
        result = {k: data[k] for k in keys if k in data}
        if data.get("tipo") != "pergunta":
            index = index if index is not None else {data["id"]: data}
            result["codigo"] = tree.code(data, index)
            if tree.personal(data, index):
                result["pessoal"] = True  # sem numeração da empresa: o código exibido é a issue
        return result

    def epics(self, tasks, index=None):
        """Épicos abertos com o progresso das histórias."""
        index, roles = index or tree.index_of(tasks), self.roles()
        result = []
        for task in tasks:
            data = task["data"]
            if data.get("nivel") != "epico" or roles.get(data.get("coluna")) == "arquivado":
                continue
            stories = [t["data"] for t in tasks if t["data"].get("pai") == data["id"]
                       and roles.get(t["data"].get("coluna")) != "arquivado"]
            done = sum(1 for d in stories if roles.get(d.get("coluna")) == "concluido")
            result.append(dict(self.brief(task, index), historias=len(stories), concluidas=done))
        return result

    def complement(self, identifier):
        base = self.cfg.get("confidential")
        path = Path(base) / "tarefas" / (identifier + ".md") if base else None
        return path.read_text(encoding="utf-8") if path and path.is_file() else None

    def find_terms_in(self, *texts):
        return find_terms("\n".join(t for t in texts if t), self.store.terms)

    def _check_text(self, *texts):
        hits = find_terms("\n".join(t for t in texts if t), self.store.terms)
        if hits:
            raise ValueError("Texto com termo confidencial (%s); mova para o complemento confidencial" % ", ".join(hits))

    # Consulta ---------------------------------------------------------------
    def summary(self, active=None):
        tasks, roles, day = self.store.list(), self.roles(), today()
        columns = {}
        for column in self.store.columns():
            columns[column["id"]] = dict(nome=column["nome"], papel=column["papel"], total=0)
        for task in tasks:
            if task["data"].get("coluna") in columns:
                columns[task["data"]["coluna"]]["total"] += 1
        review, index = self.review(tasks), tree.index_of(tasks)
        current = [self.brief(t, index) for t in tasks if roles.get(t["data"].get("coluna")) == "ativo"]
        result = dict(hoje=day.isoformat(), ativas=current, epicos=self.epics(tasks, index),
                      prazos=review["atrasadas"] + review["proximas"], perguntas=review["perguntas"], colunas=columns)
        if active:
            result["tarefa_ativa"] = active
        return result

    def show(self, identifier):
        task = self.store.get(identifier)
        result = dict(task, complemento=self.complement(identifier))
        if result["complemento"] is None:
            result.pop("complemento")
        return result

    def search(self, query="", tipo=None, coluna=None, projeto=None, limit=20, nivel=None, pai=None):
        needle = _plain(query)
        found, tasks = [], self.store.list()
        index = tree.index_of(tasks)
        for task in tasks:
            data = task["data"]
            if tipo and data.get("tipo") != tipo or coluna and data.get("coluna") != coluna:
                continue
            if projeto and tree.inherited(data, index, "projeto") != str(projeto):
                continue
            if nivel and data.get("nivel") != nivel or pai and data.get("pai") != pai:
                continue
            haystack = _plain(" ".join(str(v) for v in data.values()) + " " + task["body"])
            if needle in haystack:
                found.append(self.brief(task, index))
        return dict(total=len(found), tarefas=found[:limit])

    def recent(self, limit=10):
        tasks = sorted(self.store.list(), key=lambda t: t["data"].get("atualizada", ""), reverse=True)
        index = tree.index_of(tasks)
        return [dict(self.brief(t, index), atualizada=t["data"].get("atualizada")) for t in tasks[:limit]]

    def review(self, tasks=None, stale_days=7, soon_days=2):
        tasks, roles, day = tasks or self.store.list(), self.roles(), today()
        index = tree.index_of(tasks)
        result = dict(perguntas=[], atrasadas=[], proximas=[], sem_prazo=[], paradas=[])
        for task in tasks:
            data, role = task["data"], roles.get(task["data"].get("coluna"))
            if data.get("tipo") == "pergunta":
                if not data.get("resposta") and role not in CLOSED:
                    result["perguntas"].append(self.brief(task, index))
                continue
            if role in CLOSED:
                continue
            if data.get("prazo"):
                due = datetime.date.fromisoformat(data["prazo"])
                if due < day:
                    result["atrasadas"].append(self.brief(task, index))
                elif (due - day).days <= soon_days:
                    result["proximas"].append(self.brief(task, index))
            else:
                result["sem_prazo"].append(self.brief(task, index))
            updated = data.get("atualizada")
            if role in OPEN_WORK and updated:
                age = day - datetime.datetime.fromisoformat(updated).date()
                if age.days > stale_days:
                    result["paradas"].append(dict(self.brief(task, index), dias=age.days))
        for key in ("atrasadas", "proximas"):
            result[key].sort(key=lambda t: t["prazo"])
        return result

    # Escrita ----------------------------------------------------------------
    def add(self, tipo, titulo, coluna=None, prazo=None, body="", **fields):
        if tipo not in TIPOS:
            raise ValueError("Tipo inválido: %r" % (tipo,))
        code = (fields.get("demanda") if tipo == "demanda" else fields.get("projeto") if tipo == "projeto"
                else fields.get("demanda") or fields.get("projeto") if tipo == "especificacao" else None)
        identifier = fields.pop("id", None) or self.store.new_id(tipo, code, titulo)
        column = coluna or self.first_column("entrada")
        data = dict(fields, id=identifier, tipo=tipo, titulo=titulo, coluna=column, ordem=self.next_order(column))
        if prazo:
            data["prazo"] = parse_date(prazo)
        revision = self.store.save(data, body)
        self._event("criar", tarefa=identifier, tipo=tipo, coluna=column)
        return dict(id=identifier, revision=revision, coluna=column)

    def edit(self, identifier, changes=None, unset=(), append=None, expected_revision=None):
        with self.store.lock():
            task = self.store.get(identifier)
            if expected_revision and expected_revision != task["revision"]:
                from .store import Conflict
                raise Conflict("Tarefa mudou depois da leitura; recarregue antes de gravar: " + identifier)
            data = dict(task["data"])
            for key, value in (changes or {}).items():
                if key in ("id", "criada", "atualizada"):
                    raise ValueError("Campo não editável: " + key)
                data[key] = parse_date(value) if key == "prazo" and value else value
            if changes and "coluna" in changes and "ordem" not in changes and changes["coluna"] != task["data"].get("coluna"):
                data["ordem"] = self.next_order(changes["coluna"])
            for key in unset:
                data.pop(key, None)
            body = task["body"]
            if append:
                self._check_text(append)
                body = _append_log(body, append)
            revision = self.store.save(data, body, task["revision"])
            before = task["data"].get("coluna")
            if before != data["coluna"]:
                self._event("mover", tarefa=identifier, de=before, para=data["coluna"])
            elif data.get("ordem") != task["data"].get("ordem"):
                self._event("reordenar", tarefa=identifier, coluna=data["coluna"], ordem=data.get("ordem"))
            changed = sorted(k for k in set(data) | set(task["data"])
                             if k not in ("coluna", "ordem", "atualizada", "criada") and data.get(k) != task["data"].get(k))
            if changed or append:
                self._event("editar", tarefa=identifier, campos=changed + (["registro"] if append else []))
            return dict(id=identifier, revision=revision, coluna=data["coluna"])

    def move(self, identifier, papel, note=None):
        return self.edit(identifier, dict(coluna=self.first_column(papel)), append=note)

    def forget(self, identifier, reason=None):
        """Arquiva sem apagar o arquivo nem o histórico."""
        return self.move(identifier, "arquivado", note=("Arquivada: " + reason) if reason else "Arquivada.")

    def start(self, identifier, state_path):
        task = self.store.get(identifier)
        if task["data"].get("tipo") == "pergunta":
            raise ValueError("Pergunta não pode ser tarefa ativa")
        role = self.roles().get(task["data"].get("coluna"))
        moved = None
        if role in ("entrada", "pronto"):
            moved = self.move(identifier, "ativo")["coluna"]
        elif role in CLOSED:
            raise ValueError("Tarefa fechada não pode ser ativa; reabra movendo de coluna")
        atomic_write(state_path, json.dumps(dict(id=identifier, desde=now()), ensure_ascii=False) + "\n")
        self._event("iniciar", tarefa=identifier)
        return dict(id=identifier, movida_para=moved)

    def ask(self, question, about=None):
        if about:
            self.store.get(about)
        fields = dict(sobre=about) if about else {}
        return self.add("pergunta", question, **fields)

    def answer(self, identifier, text):
        task = self.store.get(identifier)
        if task["data"].get("tipo") != "pergunta":
            raise ValueError("Somente perguntas recebem resposta")
        return self.edit(identifier, dict(resposta=text))

    def log(self, identifier, hours, note=None, day=None, machine=None):
        self.store.get(identifier)
        hours = float(str(hours).replace(",", ".").rstrip("hH"))
        if not 0 < hours <= 24:
            raise ValueError("Horas fora do intervalo do dia")
        self._check_text(note)
        date = parse_date(day) if day else today().isoformat()
        machine = machine or self.cfg.get("machine") or "local"
        entry = dict(tipo="manual", data=date, tarefa=identifier, horas=hours, ts=now())
        if note:
            entry["obs"] = note
        path = self.store.root / "horas" / ("%s-%s.jsonl" % (date[:7], machine))
        with self.store.lock():
            path.parent.mkdir(exist_ok=True)
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self._event("horas", tarefa=identifier, horas=hours)
        return entry

    def clean(self, days=30, apply=False):
        roles, day, tasks = self.roles(), today(), self.store.list()
        old = []
        for task in tasks:
            data = task["data"]
            if roles.get(data.get("coluna")) == "concluido" and data.get("atualizada"):
                if (day - datetime.datetime.fromisoformat(data["atualizada"]).date()).days > days:
                    old.append(data["id"])
        groups = {}
        for task in tasks:
            data = task["data"]
            if roles.get(data.get("coluna")) == "arquivado":
                continue
            code = data.get("demanda") or (data.get("projeto") if data.get("tipo") == "projeto" else None)
            key = (data["tipo"], code) if code else ("titulo", _plain(data["titulo"]))
            groups.setdefault(key, []).append(data["id"])
        duplicates = [ids for ids in groups.values() if len(ids) > 1]
        archived = [self.move(i, "arquivado", note="Arquivada na faxina.")["id"] for i in old] if apply else []
        return dict(concluidas_antigas=old, duplicatas=duplicates, arquivadas=archived)


def _append_log(body, text):
    stamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    line = "- %s — %s" % (stamp, text.strip())
    if "## Registro" not in body:
        return (body.rstrip("\n") + "\n\n" if body.strip() else "") + "## Registro\n\n" + line + "\n"
    return body.rstrip("\n") + "\n" + line + "\n"


def sync(root, message="chore: atualiza tarefas"):
    """Commit local, pull com rebase e push; conflito aborta sem descartar nada."""
    from .store import TaskStore
    with TaskStore(root).lock():
        return _sync(root, message)


def _sync(root, message):
    git = lambda *a, check=True: remote.git(root, *a, check=check)
    git("add", "-A")
    committed = None
    if git("diff", "--cached", "--name-only").stdout.strip():
        git("commit", "-q", "-m", message)
        committed = git("rev-parse", "--short", "HEAD").stdout.strip()
    branch = git("branch", "--show-current").stdout.strip()
    upstream = git("rev-parse", "--abbrev-ref", "@{upstream}", check=False)
    if upstream.returncode:
        git("push", "-u", "origin", branch)
        return dict(commit=committed, pulled=False, pushed=True)
    pulled = git("pull", "--rebase", "-q", check=False)
    if pulled.returncode:
        git("rebase", "--abort", check=False)
        raise ValueError("Conflito ao integrar o remoto; nada foi descartado. Resolva no repositório de dados: " + str(root))
    ahead = git("rev-list", "--count", "@{upstream}..HEAD").stdout.strip()
    if ahead != "0":
        git("push", "-q")
    return dict(commit=committed, pulled=True, pushed=ahead != "0")


def set_policy(config_path, mode):
    from .init import read_config, write_config
    if mode not in ("automatic", "manual"):
        raise ValueError("Política deve ser automatic ou manual")
    full = read_config(config_path)
    if not full.get("tasks"):
        raise ValueError("YABook Tasks não configurado nesta máquina; rode task init")
    full["tasks"]["policy"] = mode
    write_config(config_path, full)
    return dict(policy=mode)
