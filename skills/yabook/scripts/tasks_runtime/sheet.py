"""Ficha de horas sugerida a partir das janelas de atividade e dos lançamentos manuais.

As horas configuradas do dia são divididas entre as tarefas que contam na
ficha, na proporção da atividade; o resto é extra, registrado fora do total.
Demanda (chamado) dispensa observação. Nas demais linhas a observação resume o
que foi feito no dia para colar no sistema de horas: `Desenvolvimento: item;
item.`, com o texto curto `ficha` de cada tarefa (ou o título), sem registro,
datas nem números de demanda ou issue.
"""
import datetime
import json
import math
import uuid
from pathlib import Path

from . import tree
from .precommit_hook import find_terms
from .store import now

WINDOW_HOURS = 0.25


def attribution(data, index=None):
    """(tipo, código) na ficha, ou None quando a tarefa é pessoal (extra).

    O código é o do próprio tipo da tarefa; sem ele, o do ancestral mais próximo
    na cadeia de `pai` (o do tipo dele, senão demanda ou projeto). Trabalho sem
    código entra como linha `trabalho` para a pessoa ajustar.
    """
    index = index or {data["id"]: data}
    if tree.personal(data, index):
        return None
    found = tree.nearest_code(data, index)
    if data.get("tipo") == "especificacao" and found:
        return "especificacao", found[1]
    return found or ("trabalho", "")


def window_records(root, day):
    """Janelas deduplicadas e correções ordenadas, inclusive entre máquinas."""
    windows, corrections, manual, notes = set(), {}, {}, {}
    for path in sorted(Path(root, "horas").glob(day[:7] + "-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("data") != day or not entry.get("tarefa"):
                continue
            kind = entry.get("tipo")
            if kind == "janela" and entry.get("janela"):
                windows.add((entry["janela"], entry["tarefa"]))
            elif kind == "correcao" and entry.get("janela") and isinstance(entry.get("ignorar"), bool):
                key = (entry["janela"], entry["tarefa"])
                order = (entry.get("ts", ""), entry.get("id", ""))
                if key not in corrections or order > corrections[key][0]:
                    corrections[key] = (order, entry["ignorar"])
            elif kind == "manual":
                manual[entry["tarefa"]] = manual.get(entry["tarefa"], 0) + float(entry.get("horas", 0))
                if entry.get("obs"):
                    notes.setdefault(entry["tarefa"], []).append(entry["obs"])
    rows = [dict(janela=start, tarefa=task, ignorar=corrections.get((start, task), (None, False))[1])
            for start, task in sorted(windows)]
    return rows, manual, notes


def activity(root, day):
    """Horas estimadas por tarefa, respeitando correções sem apagar o histórico."""
    windows, manual, notes = window_records(root, day)
    hours = dict(manual)
    for entry in windows:
        if not entry["ignorar"]:
            task = entry["tarefa"]
            hours[task] = hours.get(task, 0) + WINDOW_HOURS
    return hours, notes


def correct_windows(store, machine, day, corrections):
    """Acrescenta correções reversíveis; a chave representa a janela entre máquinas."""
    from .events import _machine
    with store.lock():
        available = {(r["janela"], r["tarefa"]) for r in window_records(store.root, day)[0]}
        seen = set()
        for item in corrections:
            key = (item.get("janela"), item.get("tarefa"))
            if key not in available or key in seen or not isinstance(item.get("ignorar"), bool):
                raise ValueError("Correção de janela inválida ou desatualizada")
            seen.add(key)
        path = Path(store.root, "horas", "%s-%s.jsonl" % (day[:7], _machine(machine)))
        path.parent.mkdir(exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            for item in corrections:
                entry = dict(tipo="correcao", data=day, janela=item["janela"], tarefa=item["tarefa"],
                             ignorar=item["ignorar"], ts=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="microseconds"),
                             id=uuid.uuid4().hex)
                stream.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")



def distribute(weights, total, step):
    """Divide `total` em múltiplos de `step` proporcionalmente, somando exatamente `total`."""
    units = int(round(total / step))
    whole = sum(weights.values())
    if not weights or whole <= 0 or units <= 0:
        return {}
    exact = {k: units * v / whole for k, v in weights.items()}
    result = {k: math.floor(v) for k, v in exact.items()}
    for key in sorted(exact, key=lambda k: (-(exact[k] - result[k]), -weights[k], k))[:units - sum(result.values())]:
        result[key] += 1
    return {k: round(v * step, 2) for k, v in result.items() if v}


def _item_text(data):
    text = (data.get("ficha") or data.get("titulo") or "").strip().rstrip(".")
    if len(text) > 1 and text[0].isupper() and not text[1].isupper():
        text = text[0].lower() + text[1:]
    return text


def observation(items, notes):
    """`Atividade: item; item.` — Especificação só quando todos os itens são especificações."""
    verb = "Especificação" if items and all(d.get("tipo") == "especificacao" for d in items) else "Desenvolvimento"
    parts = list(dict.fromkeys(p for p in [_item_text(d) for d in items] + [n.strip().rstrip(".") for n in notes] if p))
    return "%s: %s." % (verb, "; ".join(parts)) if parts else verb + "."


def _round_step(value, step):
    return round(max(step, round(value / step) * step), 2) if value > 0 else 0


TOUCH_ACTIONS = ("criar", "mover", "editar", "reordenar", "horas", "iniciar")


def touches(root, day, index):
    """Quantos toques cada tarefa recebeu no dia: eventos dela e alteração do arquivo na data."""
    from . import events
    count = {}
    for entry in events.read_all(root, months=2):
        if (entry.get("ts") or "")[:10] == day and entry.get("acao") in TOUCH_ACTIONS and entry.get("tarefa") in index:
            count[entry["tarefa"]] = count.get(entry["tarefa"], 0) + 1
    for data in index.values():
        if (data.get("atualizada") or "")[:10] == day:
            count[data["id"]] = max(count.get(data["id"], 0), 1)
    return count


def spread_epic_hours(hours, index, day_touches):
    """Horas marcadas num épico vão para as descendentes com demanda tocadas no dia, na proporção dos toques.

    Devolve o novo mapa de horas e, por épico, as tarefas que receberam a divisão.
    """
    result, spread = dict(hours), {}
    for identifier, value in hours.items():
        data = index.get(identifier)
        if not data or data.get("nivel") != "epico" or tree.personal(data, index):
            continue
        kids = [d["id"] for d in index.values() if d["id"] != identifier and identifier in {a["id"] for a in tree.chain(d, index)[1:]}
                and day_touches.get(d["id"]) and (tree.own_code(d) or (None,))[0] == "demanda" and not tree.personal(d, index)]
        if not kids:
            continue
        total = sum(day_touches[k] for k in kids)
        del result[identifier]
        for kid in kids:
            result[kid] = result.get(kid, 0) + value * day_touches[kid] / total
        spread[identifier] = sorted(kids)
    return result, spread


def day_sheet(store, day, complement=None):
    cfg = store.config()
    ficha = cfg.get("ficha", {})
    labels = cfg.get("rotulos", {})
    per_day, step = float(ficha.get("horas_dia", 8)), float(ficha.get("arredondamento", 1))
    windows, _, _ = window_records(store.root, day)
    hours, notes = activity(store.root, day)
    tasks = {t["data"]["id"]: t for t in store.list()}
    index = {k: t["data"] for k, t in tasks.items()}
    for entry in windows:
        entry["titulo"] = index.get(entry["tarefa"], {}).get("titulo", entry["tarefa"])
    hours, spread = spread_epic_hours(hours, index, touches(store.root, day, index))
    groups, extras = {}, []
    touched = [d for d in index.values() if (d.get("atualizada") or "")[:10] == day and d.get("tipo") != "pergunta"
               and d["id"] not in hours]
    for identifier, value in sorted(hours.items()):
        task = tasks.get(identifier)
        key = attribution(task["data"], index) if task else None
        if key is None:
            extras.append(dict(tarefa=identifier, titulo=task["data"]["titulo"] if task else identifier,
                               horas=_round_step(value, step)))
            continue
        group = groups.setdefault(key, dict(peso=0.0, tarefas=[]))
        group["peso"] += value
        group["tarefas"].append(identifier)
    for data in touched:  # alterada no dia sem horas marcadas: entra na observação, não no peso
        key = attribution(data, index)
        if key in groups:
            groups[key].setdefault("tocadas", []).append(data["id"])
    totals = distribute({k: g["peso"] for k, g in groups.items()}, per_day, step)
    rows = []
    for key, group in groups.items():
        if key not in totals:
            continue
        observacao = ""
        if key[0] != "demanda":  # chamado dispensa observação
            worked = group["tarefas"] + group.get("tocadas", [])
            covered = set().union(*(set(d["id"] for d in tree.chain(index[i], index)[1:]) for i in worked))
            items = [index[i] for i in worked if i not in covered]  # épico cede lugar às histórias do dia
            items.sort(key=lambda d: (d.get("nivel") != "historia", d.get("ordem", 0), d["titulo"]))
            observacao = observation(items, [n for i in group["tarefas"] for n in notes.get(i, [])])
        label = labels.get(key[0], "Sem código" if key[0] == "trabalho" else key[0])
        row = dict(tipo=key[0], rotulo=label, codigo=key[1], inicio=None, fim=None,
                   total=totals[key], estimado=round(group["peso"], 2), tarefas=group["tarefas"],
                   observacao=observacao)
        if complement:
            extra = [c for c in (complement(i) for i in group["tarefas"]) if c]
            if extra:
                row["complemento"] = "\n".join(extra)
        rows.append(row)
    rows.sort(key=lambda r: (-r["total"], r["tipo"], str(r["codigo"])))
    confirmed = confirmed_day(store.root, day)
    if confirmed:  # observação ajustada na confirmação prevalece
        chosen = {(r["tipo"], str(r["codigo"])): r.get("observacao") for r in confirmed.get("linhas", [])}
        for row in rows:
            if chosen.get((row["tipo"], str(row["codigo"]))):
                row["observacao_sugerida"], row["observacao"] = row["observacao"], chosen[(row["tipo"], str(row["codigo"]))]
    return dict(data=day, horas_dia=per_day, total=round(sum(r["total"] for r in rows), 2), linhas=rows, divididas=spread,
                extras=extras, confirmada=confirmed, janelas=windows)


def week_sheet(store, day, complement=None):
    date = datetime.date.fromisoformat(day)
    monday = date - datetime.timedelta(days=date.weekday())
    days = [day_sheet(store, (monday + datetime.timedelta(days=i)).isoformat(), complement) for i in range(7)]
    days = [d for d in days if d["linhas"] or d["extras"] or d["confirmada"]]
    summary = {}
    for sheet in days:
        source = sheet["confirmada"]["linhas"] if sheet["confirmada"] else sheet["linhas"]
        for row in source:
            key = (row["tipo"], str(row["codigo"]))
            summary[key] = round(summary.get(key, 0) + row["total"], 2)
    return dict(inicio=monday.isoformat(), dias=days,
                totais=[dict(tipo=k[0], codigo=k[1], total=v) for k, v in sorted(summary.items(), key=lambda i: -i[1])])


def confirmed_day(root, day):
    path = Path(root, "fichas", day[:7] + ".jsonl")
    if not path.exists():
        return None
    latest = None
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("data") == day:
            latest = entry
    return latest


def confirm(store, day, rows=None, extras=None):
    """Grava os totais confirmados do dia; a confirmação mais recente prevalece."""
    sheet = day_sheet(store, day)
    rows = rows if rows is not None else [dict(tipo=r["tipo"], codigo=r["codigo"], total=r["total"], observacao=r["observacao"])
                                          for r in sheet["linhas"]]
    extras = extras if extras is not None else [dict(tarefa=e["tarefa"], horas=e["horas"]) for e in sheet["extras"]]
    clean_rows = []
    for row in rows:
        coded = row.get("tipo") in ("demanda", "projeto", "especificacao") and str(row.get("codigo", "")).strip()
        if not coded and row.get("tipo") != "trabalho":
            raise ValueError("Linha da ficha precisa de tipo demanda, projeto ou especificacao e código, "
                             "ou tipo trabalho para horas sem código")
        total = float(row["total"])
        if not 0 <= total <= 24:
            raise ValueError("Total fora do intervalo do dia")
        clean = dict(tipo=row["tipo"], codigo=str(row["codigo"]), total=total)
        if str(row.get("observacao") or "").strip():
            clean["observacao"] = str(row["observacao"]).strip()
            hits = find_terms(clean["observacao"], store.terms)
            if hits:
                raise ValueError("Observação com termo confidencial (%s); reescreva sem o termo" % ", ".join(hits))
        clean_rows.append(clean)
    clean_extras = [dict(tarefa=e["tarefa"], horas=float(e["horas"])) for e in extras]
    entry = dict(data=day, linhas=clean_rows, extras=clean_extras, ts=now())
    path = store.root / "fichas" / (day[:7] + ".jsonl")
    with store.lock():
        path.parent.mkdir(exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
    return entry
