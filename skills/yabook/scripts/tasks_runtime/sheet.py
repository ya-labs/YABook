"""Ficha de horas sugerida a partir das janelas de atividade e dos lançamentos manuais.

A captura deduplica janelas simultâneas. O rateio sugere margem de até 50%,
limitada a 1h por código e ao saldo da jornada, sem forçar seu preenchimento.
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



def captured_activity(windows):
    """Uma janela vale 15 min no dia, repartida entre tarefas simultâneas."""
    slots = {}
    for entry in windows:
        if not entry["ignorar"]:
            slots.setdefault(entry["janela"], set()).add(entry["tarefa"])
    result = {}
    for identifiers in slots.values():
        for identifier in identifiers:
            result[identifier] = result.get(identifier, 0) + WINDOW_HOURS / len(identifiers)
    return result


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


def bounded_rateio(bases, jornada):
    """Sugere margem limitada por código; nenhuma base é reduzida ou inventada."""
    bases = {k: max(0, v) for k, v in bases.items()}
    limits = {k: min(v * .5, 1.0) for k, v in bases.items()}
    available = max(0, jornada - sum(bases.values()))
    maximum = sum(limits.values())
    factor = min(1, available / maximum) if maximum else 0
    return {k: round(v + limits[k] * factor, 6) for k, v in bases.items()}


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



def day_sheet(store, day, complement=None):
    cfg = store.config()
    ficha = cfg.get("ficha", {})
    labels = cfg.get("rotulos", {})
    per_day, step = float(ficha.get("horas_dia", 8)), float(ficha.get("arredondamento", 1))
    windows, manual, notes = window_records(store.root, day)
    captured = captured_activity(windows)
    hours, _ = activity(store.root, day)
    tasks = {t["data"]["id"]: t for t in store.list()}
    index = {k: t["data"] for k, t in tasks.items()}
    for entry in windows:
        entry["titulo"] = index.get(entry["tarefa"], {}).get("titulo", entry["tarefa"])
    groups, extras = {}, []

    def group_for(key):
        return groups.setdefault(key, dict(tarefas=[], capturado=0.0, informado=0.0))

    for identifier in sorted(set(hours) | set(captured) | set(manual)):
        task = index.get(identifier)
        key = attribution(task, index) if task else None
        direct, informed = captured.get(identifier, 0), manual.get(identifier, 0)
        if key is None:
            extras.append(dict(tarefa=identifier, titulo=task["titulo"] if task else identifier,
                               horas=_round_step(hours.get(identifier, 0), step),
                               capturado=round(direct, 6), informado=round(informed, 6), registrado=round(direct + informed, 6)))
            continue
        group = group_for(key)
        group["capturado"] += direct
        group["informado"] += informed
        group["tarefas"].append(identifier)

    touched = [d for d in index.values() if (d.get("atualizada") or "")[:10] == day and d.get("tipo") != "pergunta"
               and d["id"] not in hours]
    for data in touched:
        key = attribution(data, index)
        if key not in groups and key and key[0] == "demanda" and any(
                ancestor["id"] in captured for ancestor in tree.chain(data, index)[1:]):
            group_for(key)
        if key in groups:
            groups[key].setdefault("tocadas", []).append(data["id"])
    bases = {k: g["capturado"] + g["informado"] for k, g in groups.items()}
    totals = bounded_rateio(bases, per_day)
    rows = []
    for key, group in groups.items():
        total = totals.get(key, 0)
        if not total and not group["capturado"] and not group["informado"] and not group.get("tocadas"):
            continue
        observacao = ""
        if key[0] != "demanda":
            worked = group["tarefas"] + group.get("tocadas", [])
            covered = set().union(*(set(d["id"] for d in tree.chain(index[i], index)[1:]) for i in worked)) if worked else set()
            items = [index[i] for i in worked if i not in covered]
            items.sort(key=lambda d: (d.get("nivel") != "historia", d.get("ordem", 0), d["titulo"]))
            observacao = observation(items, [n for i in group["tarefas"] for n in notes.get(i, [])])
        label = labels.get(key[0], "Sem código" if key[0] == "trabalho" else key[0])
        row = dict(tipo=key[0], rotulo=label, codigo=key[1], inicio=None, fim=None,
                   total=round(total, 6), estimado=round(bases[key], 6), tarefas=group["tarefas"] or group.get("tocadas", []),
                   capturado=round(group["capturado"], 6), informado=round(group["informado"], 6),
                   registrado=round(group["capturado"] + group["informado"], 6), observacao=observacao)
        if complement:
            extra = [c for c in (complement(i) for i in group["tarefas"]) if c]
            if extra:
                row["complemento"] = "\n".join(extra)
        rows.append(row)
    rows.sort(key=lambda r: (-r["total"], r["tipo"], str(r["codigo"])))
    capture_total = sum(captured.values())
    manual_total = sum(manual.values())
    registered = sum(r["registrado"] for r in rows)
    return dict(data=day, horas_dia=per_day, total=round(sum(r["total"] for r in rows), 6), linhas=rows, divididas={},
                acumulado_total=round(sum(hours.values()), 6),
                saldo_rateado=round(max(0, per_day - sum(r["total"] for r in rows)), 6),
                margem_percentual=50, margem_limite=1,
                capturado_total=round(capture_total, 6), informado_total=round(manual_total, 6),
                registrado_total=round(capture_total + manual_total, 6), registrado_ficha=round(registered, 6),
                extras_registrado=round(sum(e["registrado"] for e in extras), 6),
                falta=round(max(0, per_day - registered), 6), excedente=round(max(0, registered - per_day), 6),
                extras=extras, janelas=windows)


def week_sheet(store, day, complement=None):
    date = datetime.date.fromisoformat(day)
    monday = date - datetime.timedelta(days=date.weekday())
    days = [day_sheet(store, (monday + datetime.timedelta(days=i)).isoformat(), complement) for i in range(7)]
    days = [d for d in days if d["linhas"] or d["extras"]]
    summary = {}
    for sheet in days:
        for row in sheet["linhas"]:
            if row["total"] <= 0:
                continue
            key = (row["tipo"], str(row["codigo"]))
            summary[key] = round(summary.get(key, 0) + row["total"], 6)
    return dict(inicio=monday.isoformat(), dias=days,
                totais=[dict(tipo=k[0], codigo=k[1], total=v) for k, v in sorted(summary.items(), key=lambda i: -i[1])])
