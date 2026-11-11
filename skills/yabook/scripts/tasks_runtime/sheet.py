"""Ficha de horas sugerida a partir das janelas de atividade e dos lançamentos manuais.

As horas configuradas do dia são divididas entre as tarefas que contam na
ficha, na proporção da atividade; o resto é extra, registrado fora do total.
A observação é montada com texto genérico e, onde existir, o complemento
confidencial local; ela nunca é versionada.
"""
import datetime
import json
import math
import re
from pathlib import Path

from .store import now

WINDOW_HOURS = 0.25
_LOG_LINE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) \d{2}:\d{2} — (.+)$", re.MULTILINE)


def attribution(data):
    """(tipo, código) na ficha, ou None quando a tarefa é extra."""
    if data.get("tipo") == "especificacao":
        return "especificacao", data.get("demanda") or data.get("projeto") or data["id"]
    if data.get("demanda"):
        return "demanda", data["demanda"]
    if data.get("projeto"):
        return "projeto", data["projeto"]
    return None


def activity(root, day):
    """Horas estimadas por tarefa no dia: janelas únicas entre máquinas e lançamentos manuais."""
    windows, manual, notes = set(), {}, {}
    for path in sorted(Path(root, "horas").glob(day[:7] + "-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("data") != day or not entry.get("tarefa"):
                continue
            if entry.get("tipo") == "janela":
                windows.add((entry["janela"], entry["tarefa"]))
            elif entry.get("tipo") == "manual":
                manual[entry["tarefa"]] = manual.get(entry["tarefa"], 0) + float(entry.get("horas", 0))
                if entry.get("obs"):
                    notes.setdefault(entry["tarefa"], []).append(entry["obs"])
    hours = dict(manual)
    for _, task in windows:
        hours[task] = hours.get(task, 0) + WINDOW_HOURS
    return hours, notes


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


def _round_step(value, step):
    return round(max(step, round(value / step) * step), 2) if value > 0 else 0


def day_sheet(store, day, complement=None):
    cfg = store.config()
    ficha = cfg.get("ficha", {})
    labels = cfg.get("rotulos", {})
    per_day, step = float(ficha.get("horas_dia", 8)), float(ficha.get("arredondamento", 1))
    hours, notes = activity(store.root, day)
    tasks = {t["data"]["id"]: t for t in store.list()}
    groups, extras = {}, []
    for identifier, value in sorted(hours.items()):
        task = tasks.get(identifier)
        key = attribution(task["data"]) if task else None
        if key is None:
            extras.append(dict(tarefa=identifier, titulo=task["data"]["titulo"] if task else identifier,
                               horas=_round_step(value, step)))
            continue
        group = groups.setdefault(key, dict(peso=0.0, tarefas=[]))
        group["peso"] += value
        group["tarefas"].append(identifier)
    totals = distribute({k: g["peso"] for k, g in groups.items()}, per_day, step)
    rows = []
    for key, group in groups.items():
        if key not in totals:
            continue
        pieces = []
        for identifier in group["tarefas"]:
            task = tasks[identifier]
            pieces.append(task["data"]["titulo"])
            pieces += [text for date, text in _LOG_LINE.findall(task["body"]) if date == day]
            pieces += notes.get(identifier, [])
        row = dict(tipo=key[0], rotulo=labels.get(key[0], key[0]), codigo=key[1], inicio=None, fim=None,
                   total=totals[key], estimado=round(group["peso"], 2), tarefas=group["tarefas"],
                   observacao="; ".join(dict.fromkeys(p.strip() for p in pieces if p.strip())))
        if complement:
            extra = [c for c in (complement(i) for i in group["tarefas"]) if c]
            if extra:
                row["complemento"] = "\n".join(extra)
        rows.append(row)
    rows.sort(key=lambda r: (-r["total"], r["tipo"], str(r["codigo"])))
    confirmed = confirmed_day(store.root, day)
    return dict(data=day, horas_dia=per_day, total=round(sum(r["total"] for r in rows), 2), linhas=rows,
                extras=extras, confirmada=confirmed)


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
    rows = rows if rows is not None else [dict(tipo=r["tipo"], codigo=r["codigo"], total=r["total"]) for r in sheet["linhas"]]
    extras = extras if extras is not None else [dict(tarefa=e["tarefa"], horas=e["horas"]) for e in sheet["extras"]]
    clean_rows = []
    for row in rows:
        if row.get("tipo") not in ("demanda", "projeto", "especificacao") or not str(row.get("codigo", "")).strip():
            raise ValueError("Linha da ficha precisa de tipo demanda, projeto ou especificacao e código")
        total = float(row["total"])
        if not 0 <= total <= 24:
            raise ValueError("Total fora do intervalo do dia")
        clean_rows.append(dict(tipo=row["tipo"], codigo=str(row["codigo"]), total=total))
    clean_extras = [dict(tarefa=e["tarefa"], horas=float(e["horas"])) for e in extras]
    entry = dict(data=day, linhas=clean_rows, extras=clean_extras, ts=now())
    path = store.root / "fichas" / (day[:7] + ".jsonl")
    with store.lock():
        path.parent.mkdir(exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
    return entry
