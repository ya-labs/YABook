"""Edição mecânica pelo site: um salvamento explícito, validado antes de gravar.

Cada salvamento confere revisões e termos de todas as mudanças antes de escrever;
se algo falhar, nada é gravado. Depois aplica pela mesma biblioteca do agente,
com eventos de origem `quadro` (pendentes de análise), faz um commit no
repositório de dados e devolve um resumo em Markdown para a pessoa copiar.

Corpo de POST /api/salvar:
  tarefas: [{id, revision, campos?: {...}, unset?: [...], registro?}]
  colunas: [{id, nome}]
  complementos: [{id, texto}]   # texto que vai para a base confidencial local
  ficha: {data, linhas, extras}
"""
import datetime
import json
import subprocess
from http import HTTPStatus
from pathlib import Path

from . import events, fmt, sheet
from .commands import Tasks, _append_log, parse_date
from .precommit_hook import find_terms
from .store import NIVEIS, Conflict, atomic_write, validate_quadro

EDITABLE = ("titulo", "coluna", "ordem", "prazo", "proximo_passo", "projeto", "demanda", "issue", "nivel", "pai", "pessoal", "ficha")
TEXT_FIELDS = ("titulo", "proximo_passo", "ficha", "projeto", "demanda", "issue")
COMMIT_MESSAGE = "chore: salva alterações do quadro"


class TermsFound(ValueError):
    def __init__(self, hits):
        super().__init__("Texto com termo confidencial; mova para o complemento confidencial ou reescreva")
        self.hits = hits


def handle(board, path, body):
    """Despachante de escrita registrado no servidor."""
    if path != "/api/salvar":
        return HTTPStatus.NOT_FOUND, dict(error="Rota de escrita desconhecida")
    try:
        return HTTPStatus.OK, save(board.store, board.cfg, body)
    except Conflict as error:
        return HTTPStatus.CONFLICT, dict(error=str(error), conflitos=getattr(error, "ids", []))
    except TermsFound as error:
        return HTTPStatus.UNPROCESSABLE_ENTITY, dict(error=str(error), termos=error.hits,
                                                      base_confidencial=bool(board.base()))


def save(store, cfg, body):
    if not isinstance(body, dict):
        raise ValueError("Salvamento precisa ser um objeto JSON")
    changes = body.get("tarefas") or []
    columns = body.get("colunas") or []
    complements = body.get("complementos") or []
    day_sheet = body.get("ficha")
    if not (changes or columns or complements or day_sheet):
        raise ValueError("Nada para salvar")
    tasks = Tasks(store, cfg, origem="quadro")
    with store.lock():
        plan = _validate(store, cfg, tasks, changes, columns, complements, day_sheet)
        applied, seen = [], {e["id"] for e in events.read_all(store.root, months=1)}
        for entry in plan["complementos"]:
            _write_complement(cfg, entry["id"], entry["texto"])
            applied.append(dict(acao="complemento", id=entry["id"], titulo=entry["titulo"]))
        for item in plan["tarefas"]:
            before = store.get(item["id"])["data"]
            result = tasks.edit(item["id"], item["campos"], item["unset"], item.get("registro"), item["revision"])
            applied.append(dict(acao="tarefa", id=item["id"], titulo=item["campos"].get("titulo", before["titulo"]),
                                de=before.get("coluna"), para=result["coluna"],
                                campos=sorted(set(item["campos"]) | set(item["unset"]) - {"coluna", "ordem"}),
                                registro=bool(item.get("registro"))))
        if plan["colunas"]:
            quadro = fmt.loads((store.root / "quadro.yml").read_text(encoding="utf-8"))
            for column in quadro["colunas"]:
                if column["id"] in plan["colunas"]:
                    old, column["nome"] = column["nome"], plan["colunas"][column["id"]]
                    applied.append(dict(acao="coluna", id=column["id"], de=old, para=column["nome"]))
                    tasks._event("renomear-coluna", coluna=column["id"], de=old, para=column["nome"])
            validate_quadro(quadro)
            atomic_write(store.root / "quadro.yml", fmt.dumps(quadro, ["formato", "colunas"]))
        if plan["ficha"]:
            entry = sheet.confirm(store, plan["ficha"]["data"], plan["ficha"]["linhas"], plan["ficha"]["extras"])
            tasks._event("confirmar-ficha", data=entry["data"], total=sum(r["total"] for r in entry["linhas"]))
            applied.append(dict(acao="ficha", data=entry["data"], linhas=entry["linhas"], extras=entry["extras"]))
        event_ids = [e["id"] for e in events.read_all(store.root, months=1)
                     if e["id"] not in seen and e.get("origem") == "quadro"]
        commit, warning = _commit(store.root)
    result = dict(aplicadas=applied, commit=commit, eventos=event_ids)
    if warning:
        result["aviso"] = warning
    result["resumo"] = summary(store, applied, commit, event_ids)
    return result


def _validate(store, cfg, tasks, changes, columns, complements, day_sheet):
    conflicts, hits, plan_tasks = [], [], []
    known_columns = {c["id"]: c for c in store.columns()}
    for index, change in enumerate(changes):
        identifier = change.get("id")
        try:
            current = store.get(identifier)
        except KeyError:
            conflicts.append(identifier)
            continue
        if change.get("revision") != current["revision"]:
            conflicts.append(identifier)
            continue
        fields = dict(change.get("campos") or {})
        unknown = set(fields) - set(EDITABLE)
        if unknown:
            raise ValueError("%s: campos não editáveis %s" % (identifier, ", ".join(sorted(unknown))))
        unset = [k for k, v in fields.items() if v in (None, "", [])] + list(change.get("unset") or [])
        fields = {k: v for k, v in fields.items() if v not in (None, "", [])}
        if set(unset) - set(EDITABLE):
            raise ValueError("%s: campos não removíveis" % identifier)
        if "titulo" in unset:
            raise ValueError("%s: título obrigatório" % identifier)
        if "coluna" in fields and fields["coluna"] not in known_columns:
            raise ValueError("%s: coluna inexistente %s" % (identifier, fields["coluna"]))
        if "ordem" in fields:
            fields["ordem"] = int(fields["ordem"])
        if "prazo" in fields:
            fields["prazo"] = parse_date(fields["prazo"])
        if "issue" in fields and isinstance(fields["issue"], str):
            fields["issue"] = [i.strip() for i in fields["issue"].split(",") if i.strip()]
        if "nivel" in fields and fields["nivel"] not in NIVEIS:
            raise ValueError("%s: nível inválido" % identifier)
        if "pessoal" in fields and not isinstance(fields["pessoal"], bool):
            raise ValueError("%s: pessoal precisa ser verdadeiro ou falso" % identifier)
        for key in TEXT_FIELDS:
            value = fields.get(key)
            for text in (value if isinstance(value, list) else [value]):
                found = find_terms(str(text), store.terms) if text not in (None, "") else []
                if found:
                    hits.append(dict(id=identifier, campo=key, termos=found, texto=str(text)))
        note = (change.get("registro") or "").strip()
        if note:
            found = find_terms(note, store.terms)
            if found:
                hits.append(dict(id=identifier, campo="registro", termos=found, texto=note))
        plan_tasks.append(dict(id=identifier, revision=current["revision"], campos=fields, unset=sorted(set(unset)),
                               registro=note or None))
    if conflicts:
        error = Conflict("Tarefas mudaram depois da leitura; a tela será recarregada: " + ", ".join(conflicts))
        error.ids = conflicts
        raise error
    renames = {}
    for column in columns:
        if column.get("id") not in known_columns:
            raise ValueError("Coluna inexistente: %s" % column.get("id"))
        name = (column.get("nome") or "").strip()
        if not name:
            raise ValueError("Nome de coluna vazio")
        found = find_terms(name, store.terms)
        if found:
            hits.append(dict(id=column["id"], campo="coluna", termos=found, texto=name))
        renames[column["id"]] = name
    if hits:
        raise TermsFound(hits)
    plan_complements = []
    for entry in complements:
        if not cfg.get("confidential") or not Path(cfg["confidential"]).expanduser().is_dir():
            raise ValueError("Base confidencial ausente nesta máquina; reescreva o texto sem o termo")
        task = store.get(entry["id"])
        plan_complements.append(dict(id=entry["id"], texto=str(entry["texto"]).strip(), titulo=task["data"]["titulo"]))
    plan_sheet = None
    if day_sheet:
        plan_sheet = dict(data=parse_date(day_sheet["data"]), linhas=day_sheet.get("linhas"), extras=day_sheet.get("extras"))
    _simulate_tree(store, plan_tasks)
    return dict(tarefas=plan_tasks, colunas=renames, complementos=plan_complements, ficha=plan_sheet)


def _simulate_tree(store, plan_tasks):
    """Recusa antes de gravar a combinação de mudanças que quebraria a árvore."""
    if not any({"nivel", "pai"} & (set(t["campos"]) | set(t["unset"])) for t in plan_tasks):
        return
    from .store import check_tree, infer_level
    index = {t["data"]["id"]: dict(t["data"]) for t in store.list()}
    for item in plan_tasks:
        data = index[item["id"]]
        data.update(item["campos"])
        for key in item["unset"]:
            data.pop(key, None)
    for _ in range(3):
        for item in plan_tasks:
            infer_level(index[item["id"]], index)
    ids = [t["id"] for t in plan_tasks]
    check_tree(index, ids + [i for i, d in index.items() if d.get("pai") in ids])


def _write_complement(cfg, identifier, text):
    path = Path(cfg["confidential"]).expanduser() / "tarefas" / (identifier + ".md")
    current = path.read_text(encoding="utf-8") if path.is_file() else ""
    if ("— " + text) not in current:
        atomic_write(path, _append_log(current, text))


def _commit(root):
    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=20)
    if git("rev-parse", "--is-inside-work-tree").returncode:
        return None, None
    git("add", "-A")
    if not git("diff", "--cached", "--quiet").returncode:
        return None, None
    result = git("commit", "-q", "-m", COMMIT_MESSAGE)
    if result.returncode:
        return None, "Arquivos gravados, mas o commit falhou: " + (result.stderr or result.stdout).strip()[:300]
    return git("rev-parse", "--short", "HEAD").stdout.strip(), None


def summary(store, applied, commit, event_ids):
    names = {c["id"]: c["nome"] for c in store.columns()}
    stamp = datetime.datetime.now().astimezone().strftime("%d/%m %H:%M")
    lines = ["## Salvamento do quadro — %s" % stamp, ""]
    for item in applied:
        if item["acao"] == "tarefa":
            parts = []
            if item["de"] != item["para"]:
                parts.append("%s → %s" % (names.get(item["de"], item["de"]), names.get(item["para"], item["para"])))
            if item["campos"]:
                parts.append("campos: " + ", ".join(item["campos"]))
            if item["registro"]:
                parts.append("registro acrescentado")
            lines.append("- `%s` %s: %s" % (item["id"], item["titulo"], "; ".join(parts) or "ordem ajustada"))
        elif item["acao"] == "coluna":
            lines.append("- Coluna `%s` renomeada: %s → %s" % (item["id"], item["de"], item["para"]))
        elif item["acao"] == "complemento":
            lines.append("- `%s` %s: texto movido para o complemento confidencial local" % (item["id"], item["titulo"]))
        elif item["acao"] == "ficha":
            totals = ", ".join("%s %s %sh" % (r["tipo"], r["codigo"] or "sem código", ("%g" % r["total"]).replace(".", ","))
                               for r in item["linhas"])
            lines.append("- Ficha de %s confirmada: %s" % (item["data"], totals or "sem linhas"))
    lines += ["", "Commit: %s" % (commit or "sem commit"),
              "Ações para o agente analisar: %s" % (", ".join(event_ids) or "nenhuma"),
              "", "Peça ao agente: `task review` para analisar as ações do quadro."]
    return "\n".join(lines) + "\n"
