"""`task capture`: grava em lote as tarefas levantadas de uma conversa.

O agente interpreta a conversa e envia itens estruturados; aqui ficam o que
não pode depender dele: casar cada item com a tarefa existente, recusar termos
da lista local indicando o campo, conferir revisões e gravar tudo sob uma trava,
com um único evento.

Lote (JSON):
  itens: [{chave?, id?, tipo, titulo, demanda?, projeto?, issue?, prazo?,
           proximo_passo?, refs?, estado? (papel ou coluna), registro?, complemento?}]
  perguntas: [{texto, sobre? (chave ou id)}]
  ativa: chave ou id
  horas: [{tarefa (chave ou id), data, horas, obs?}]
"""
import hashlib
import json
from pathlib import Path

from . import events, tree
from .commands import Tasks, _append_log, _plain, parse_date
from .precommit_hook import find_terms
from .store import PAPEIS, TIPOS, Conflict, atomic_write, check_tree, infer_level, now

FIELDS = ("titulo", "demanda", "projeto", "issue", "prazo", "proximo_passo", "refs", "nivel", "pessoal", "ficha")
CODED = ("demanda", "projeto", "especificacao")
ITEM_KEYS = FIELDS + ("chave", "id", "tipo", "estado", "registro", "complemento", "pai")


def _list(value):
    if value in (None, ""):
        return []
    return [value] if isinstance(value, str) else list(value)


def _text(value):
    return str(value).strip() if value not in (None, "") else None


class Capture:
    def __init__(self, store, cfg=None):
        self.store, self.cfg = store, cfg or {}
        self.tasks = Tasks(store, self.cfg)

    # Plano -------------------------------------------------------------------
    def plan(self, batch):
        if not isinstance(batch, dict):
            raise ValueError("Lote precisa ser um objeto JSON")
        unknown = set(batch) - {"itens", "perguntas", "ativa", "horas"}
        if unknown:
            raise ValueError("Chaves desconhecidas no lote: " + ", ".join(sorted(unknown)))
        items, questions = batch.get("itens") or [], batch.get("perguntas") or []
        if not items and not questions:
            raise ValueError("Lote vazio: informe itens ou perguntas")
        self._check_terms(batch)
        existing = [t for t in self.store.list() if t["data"].get("tipo") != "pergunta"]
        roles = self.tasks.roles()
        existing = [t for t in existing if roles.get(t["data"].get("coluna")) != "arquivado"]
        reserved, keys, matched, ops, orders = set(), {}, {}, [], {}
        for index, item in enumerate(items):
            ops.append(self._plan_item(index, item, existing, roles, reserved, keys, matched, orders))
        ops = self._plan_tree(items, ops, keys)
        plan_questions = []
        for index, question in enumerate(questions):
            text = _text((question or {}).get("texto"))
            if not text:
                raise ValueError("perguntas[%d]: pergunta sem texto" % index)
            about = self._resolve(question.get("sobre"), keys, "perguntas[%d].sobre" % index) if question.get("sobre") else None
            duplicate = next((t["data"]["id"] for t in self.store.list() if t["data"].get("tipo") == "pergunta"
                              and not t["data"].get("resposta") and _plain(t["data"]["titulo"]) == _plain(text)), None)
            plan_questions.append(dict(texto=text, sobre=about, existente=duplicate,
                                       id=duplicate or self._new_id("pergunta", None, text, reserved)))
        active = self._resolve(batch["ativa"], keys, "ativa") if batch.get("ativa") else None
        if active:
            op = next((o for o in ops if o["id"] == active), None)
            column = op["coluna"] if op else self.store.get(active)["data"].get("coluna")
            if roles.get(column) in ("concluido", "arquivado") or (not op and self.store.get(active)["data"].get("tipo") == "pergunta"):
                raise ValueError("ativa: tarefa fechada ou pergunta não pode ser a ativa: " + active)
        hours = []
        for index, entry in enumerate(batch.get("horas") or []):
            where = "horas[%d]" % index
            target = self._resolve(entry.get("tarefa"), keys, where + ".tarefa")
            value = float(str(entry.get("horas", "")).replace(",", ".").rstrip("hH") or 0)
            if not 0 < value <= 24:
                raise ValueError(where + ": horas fora do intervalo do dia")
            if not entry.get("data"):
                raise ValueError(where + ": informe o dia; horas passadas exigem data explícita")
            hours.append(dict(tarefa=target, data=parse_date(entry["data"]), horas=value, obs=_text(entry.get("obs"))))
        if any(o.get("complemento") for o in ops) and not self.cfg.get("confidential"):
            raise ValueError("Complemento sem base confidencial nesta máquina; omita `complemento` ou configure a base")
        result = dict(operacoes=ops, perguntas=plan_questions, ativa=active, horas=hours)
        result["approval_hash"] = self._hash(batch, ops)
        return result

    def _plan_tree(self, items, ops, keys):
        """Resolve `pai` pelas chaves do lote, valida a árvore final e ordena pais antes dos filhos."""
        index = {t["data"]["id"]: dict(t["data"]) for t in self.store.list()}
        current = {k: dict(v) for k, v in index.items()}
        for position, (item, op) in enumerate(zip(items, ops)):
            if item.get("pai"):
                self._set(op, "pai", self._resolve(item["pai"], keys, "itens[%d].pai" % position), current)
        for op in ops:
            if op["acao"] == "criar":
                index[op["id"]] = dict(op["dados"])
            else:
                index[op["id"]].update(op["mudancas"])
        for _ in range(3):  # épico novo > história > tarefa no mesmo lote
            for op in ops:
                infer_level(index[op["id"]], index)
        for op in ops:
            if index[op["id"]].get("nivel") and (op.get("dados") or current.get(op["id"], {})).get("nivel") != index[op["id"]]["nivel"]:
                self._set(op, "nivel", index[op["id"]]["nivel"], current)
        ids = [op["id"] for op in ops]
        try:
            check_tree(index, ids + [i for i, d in index.items() if d.get("pai") in ids and i not in ids])
        except ValueError as error:
            raise ValueError("Hierarquia: %s" % error)
        return sorted(ops, key=lambda op: len(tree.chain(index[op["id"]], index)))

    def _set(self, op, key, value, current):
        if op["acao"] == "criar":
            op["dados"][key] = value
            op["campos"] = sorted(set(op["campos"]) | {key})
        elif value != current[op["id"]].get(key):
            op["mudancas"][key] = value
            op["campos"] = sorted(set(op["campos"]) | {key})
            op["acao"] = "atualizar"

    def _plan_item(self, index, item, existing, roles, reserved, keys, matched, orders):
        where = "itens[%d]" % index
        if not isinstance(item, dict):
            raise ValueError(where + ": item precisa ser objeto")
        unknown = set(item) - set(ITEM_KEYS)
        if unknown:
            raise ValueError("%s: campos desconhecidos %s" % (where, ", ".join(sorted(unknown))))
        tipo = item.get("tipo")
        if tipo not in TIPOS or tipo == "pergunta":
            raise ValueError(where + ": tipo inválido %r; perguntas vão em `perguntas`" % (tipo,))
        fields = {k: item[k] for k in FIELDS if item.get(k) not in (None, "", [])}
        for key in ("demanda", "projeto"):
            if key in fields:
                fields[key] = str(fields[key])
        for key in ("issue", "refs"):
            if key in fields:
                fields[key] = _list(fields[key])
        if "prazo" in fields:
            fields["prazo"] = parse_date(fields["prazo"])
        if "pessoal" in fields and not isinstance(fields["pessoal"], bool):
            raise ValueError(where + ".pessoal: use true ou false")
        column = self._column(item.get("estado"), where) if item.get("estado") else None
        task = self._match(item, tipo, fields, existing, where)
        if task:
            identifier = task["data"]["id"]
            if identifier in matched:
                raise ValueError("%s: mesma tarefa de %s (%s); junte os dois itens" % (where, matched[identifier], identifier))
            matched[identifier] = where
            current = task["data"]
            changes = {}
            for key, value in fields.items():
                if key in ("issue", "refs"):
                    value = list(dict.fromkeys(_list(current.get(key)) + value))
                if value != current.get(key):
                    changes[key] = value
            if column and roles.get(column) != roles.get(current.get("coluna")):
                changes["coluna"] = column
            note = _text(item.get("registro"))
            if note and ("— " + note) in task["body"]:
                note = None  # repetir o mesmo lote não duplica o registro
            op = dict(acao="atualizar" if changes or note else "sem-alteracao", id=identifier,
                      tipo=current["tipo"], titulo=changes.get("titulo", current["titulo"]),
                      coluna=changes.get("coluna", current["coluna"]), campos=sorted(changes),
                      revision=task["revision"], mudancas=changes)
        else:
            if not _text(fields.get("titulo")):
                raise ValueError(where + ": item novo sem título")
            code = (fields.get("demanda") if tipo == "demanda" else fields.get("projeto") if tipo == "projeto"
                    else fields.get("demanda") or fields.get("projeto") if tipo == "especificacao" else None)
            marker = "%s:%s" % (tipo, code if code else _plain(fields["titulo"]))
            if marker in matched:
                raise ValueError("%s: repete o item %s; junte os dois itens" % (where, matched[marker]))
            matched[marker] = where
            identifier = self._new_id(tipo, code, fields["titulo"], reserved)
            column = column or self.tasks.first_column("entrada")
            orders.setdefault(column, self.tasks.next_order(column))
            data = dict(fields, id=identifier, tipo=tipo, coluna=column, ordem=orders[column])
            orders[column] += 1
            op = dict(acao="criar", id=identifier, tipo=tipo, titulo=fields["titulo"], coluna=column,
                      campos=sorted(fields), dados=data)
        if task is None and item.get("registro"):
            op["registro"] = _text(item["registro"])
        elif task is not None and note:
            op["registro"] = note
        if item.get("complemento"):
            op["complemento"] = _text(item["complemento"])
        if item.get("chave") is not None:
            key = str(item["chave"])
            if key in keys:
                raise ValueError(where + ": chave repetida " + key)
            keys[key] = identifier
        return op

    def _match(self, item, tipo, fields, existing, where):
        if item.get("id"):
            found = next((t for t in existing if t["data"]["id"] == item["id"]), None)
            if found is None:
                raise ValueError("%s: tarefa inexistente ou arquivada: %s" % (where, item["id"]))
            return found
        issues = set(fields.get("issue", []))
        if issues:
            found = [t for t in existing if issues & set(_list(t["data"].get("issue")))]
            if len(found) > 1:
                raise ValueError("%s: issue em mais de uma tarefa (%s); informe `id`"
                                 % (where, ", ".join(t["data"]["id"] for t in found)))
            if found:
                return found[0]
        if tipo in CODED:
            key = "projeto" if tipo == "projeto" else "demanda" if tipo == "demanda" else None
            codes = [fields.get(key)] if key else [fields.get("demanda") or fields.get("projeto")]
            for task in existing:
                data = task["data"]
                if data.get("tipo") != tipo or not codes[0]:
                    continue
                current = data.get(key) if key else data.get("demanda") or data.get("projeto")
                if current == codes[0]:
                    return task
        title = _plain(fields.get("titulo", ""))
        return next((t for t in existing if t["data"].get("tipo") == tipo and title and _plain(t["data"]["titulo"]) == title), None)

    def _column(self, value, where):
        ids = self.store.column_ids()
        if value in ids:
            return value
        if value in PAPEIS:
            return self.tasks.first_column(value)
        raise ValueError("%s.estado: use papel (%s) ou coluna do quadro (%s)" % (where, ", ".join(PAPEIS), ", ".join(ids)))

    def _resolve(self, ref, keys, where):
        ref = str(ref)
        if ref in keys:
            return keys[ref]
        if self.store.exists(ref):
            return ref
        raise ValueError("%s: referência desconhecida %r; use a chave de um item ou o id de uma tarefa" % (where, ref))

    def _new_id(self, tipo, code, title, reserved):
        base = self.store.new_id(tipo, code, title)
        candidate, counter = base, 2
        while candidate in reserved:
            candidate, counter = "%s-%d" % (base, counter), counter + 1
        reserved.add(candidate)
        return candidate

    def _check_terms(self, batch):
        """Recusa o lote inteiro e diz em que campo versionado o termo apareceu."""
        hits = []
        for index, item in enumerate(batch.get("itens") or []):
            for key in FIELDS + ("registro", "pai"):
                value = (item or {}).get(key)
                for text in _list(value) if key in ("issue", "refs") else [value]:
                    found = find_terms(str(text), self.store.terms) if text not in (None, "") else []
                    if found:
                        hits.append("itens[%d].%s: %s" % (index, key, ", ".join(found)))
        for index, question in enumerate(batch.get("perguntas") or []):
            found = find_terms(str((question or {}).get("texto", "")), self.store.terms)
            if found:
                hits.append("perguntas[%d].texto: %s" % (index, ", ".join(found)))
        for index, entry in enumerate(batch.get("horas") or []):
            found = find_terms(str((entry or {}).get("obs", "") or ""), self.store.terms)
            if found:
                hits.append("horas[%d].obs: %s" % (index, ", ".join(found)))
        if hits:
            raise ValueError("Lote recusado, termo confidencial em campo versionado (%s); mova o texto para "
                             "`complemento`" % "; ".join(hits))

    def _hash(self, batch, ops):
        state = [(o["id"], o.get("revision")) for o in ops]
        payload = json.dumps(dict(lote=batch, estado=state, maquina=self.cfg.get("machine")),
                             ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # Aplicação ---------------------------------------------------------------
    def apply(self, batch, approval_hash=None):
        with self.store.lock():
            plan = self.plan(batch)
            if approval_hash and approval_hash != plan["approval_hash"]:
                raise Conflict("Tarefas ou lote mudaram desde o plano; gere a prévia de novo")
            created, updated = [], []
            for op in plan["operacoes"]:
                if op["acao"] == "criar":
                    body = _append_log("", op["registro"]) if op.get("registro") else ""
                    self.store.save(op["dados"], body)
                    created.append(op["id"])
                elif op["acao"] == "atualizar":
                    task = self.store.get(op["id"])
                    if task["revision"] != op["revision"]:
                        raise Conflict("Tarefa mudou depois da leitura; recarregue antes de gravar: " + op["id"])
                    data = dict(task["data"], **op["mudancas"])
                    if "coluna" in op["mudancas"]:
                        data["ordem"] = self.tasks.next_order(op["mudancas"]["coluna"])
                    body = _append_log(task["body"], op["registro"]) if op.get("registro") else task["body"]
                    self.store.save(data, body, task["revision"])
                    updated.append(op["id"])
                if op.get("complemento"):
                    self._write_complement(op["id"], op["complemento"])
            asked = []
            for question in plan["perguntas"]:
                if question["existente"]:
                    continue
                column = self.tasks.first_column("entrada")
                data = dict(id=question["id"], tipo="pergunta", titulo=question["texto"], coluna=column,
                            ordem=self.tasks.next_order(column), sobre=question["sobre"])
                self.store.save(data)
                asked.append(question["id"])
            for entry in plan["horas"]:
                self._write_hours(entry)
            if plan["ativa"]:
                self._set_active(plan["ativa"])
            events.record(self.store.root, self.cfg.get("machine"), "agente", "capturar", criadas=created,
                          atualizadas=updated, perguntas=asked, ativa=plan["ativa"])
            return dict(criadas=created, atualizadas=updated, perguntas=asked, ativa=plan["ativa"],
                        horas=len(plan["horas"]))

    def _write_complement(self, identifier, text):
        path = Path(self.cfg["confidential"]) / "tarefas" / (identifier + ".md")
        current = path.read_text(encoding="utf-8") if path.is_file() else ""
        if ("— " + text) not in current:
            atomic_write(path, _append_log(current, text))

    def _write_hours(self, entry):
        machine = events._machine(self.cfg.get("machine"))
        line = dict(tipo="manual", data=entry["data"], tarefa=entry["tarefa"], horas=entry["horas"], ts=now())
        if entry.get("obs"):
            line["obs"] = entry["obs"]
        path = self.store.root / "horas" / ("%s-%s.jsonl" % (entry["data"][:7], machine))
        path.parent.mkdir(exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(line, ensure_ascii=False, separators=(",", ":")) + "\n")

    def _set_active(self, identifier):
        roles = self.tasks.roles()
        task = self.store.get(identifier)
        if roles.get(task["data"].get("coluna")) in ("entrada", "pronto"):
            data = dict(task["data"], coluna=self.tasks.first_column("ativo"))
            data["ordem"] = self.tasks.next_order(data["coluna"])
            self.store.save(data, task["body"], task["revision"])
        state = self.store.root / "local" / "ativa.json"
        atomic_write(state, json.dumps(dict(id=identifier, desde=now(), origem="capture"), ensure_ascii=False) + "\n")
