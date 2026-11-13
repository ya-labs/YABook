"""Estimativa × tempo real: `size` das tarefas concluídas comparado às horas registradas.

Horas de uma tarefa = janelas de atividade e horas manuais dela e das tarefas abaixo
dela (a história soma as suas tarefas). Épicos ficam fora: o tamanho deles vem das
histórias. A faixa por `size` segue a escala de entrega com agentes; as horas medem
só o tempo de trabalho registrado, não a espera por validação externa.
"""
import json
import statistics
from pathlib import Path

from . import tree
from .sheet import activity

# Limite superior de horas de cada size; acima de 30 h a tarefa é size 5.
FAIXAS = {1: 1.5, 2: 4.0, 3: 10.0, 4: 30.0, 5: None}


def size_for(hours):
    return next((size for size, limit in FAIXAS.items() if limit is None or hours <= limit), 5)


def hours_by_task(root):
    days = set()
    for path in Path(root, "horas").glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                day = json.loads(line).get("data")
            except ValueError:
                continue
            if day:
                days.add(day)
    total = {}
    for day in sorted(days):
        for task, value in activity(root, day)[0].items():
            total[task] = total.get(task, 0) + value
    return total


def compare(store):
    roles = {c["id"]: c["papel"] for c in store.columns()}
    tasks = [t["data"] for t in store.list() if t["data"].get("tipo") != "pergunta"]
    index = tree.index_of(store.list())
    own = hours_by_task(store.root)
    children = {}
    for data in tasks:
        if data.get("pai"):
            children.setdefault(data["pai"], []).append(data["id"])

    def total(identifier, seen=()):
        if identifier in seen:
            return 0
        return own.get(identifier, 0) + sum(total(c, seen + (identifier,)) for c in children.get(identifier, []))

    rows = []
    for data in tasks:
        if roles.get(data.get("coluna")) != "concluido" or not data.get("size") or data.get("nivel") == "epico":
            continue
        hours = round(total(data["id"]), 2)
        if not hours:
            continue
        rows.append(dict(id=data["id"], numero=data.get("numero"), titulo=data["titulo"], codigo=tree.code(data, index),
                         size=data["size"], horas=hours, size_pelas_horas=size_for(hours)))
    groups = []
    for size in FAIXAS:
        values = [r["horas"] for r in rows if r["size"] == size]
        previous = FAIXAS.get(size - 1) or 0
        groups.append(dict(size=size, faixa=[previous, FAIXAS[size]], quantidade=len(values),
                           mediana=round(statistics.median(values), 2) if values else None,
                           minimo=min(values, default=None), maximo=max(values, default=None)))
    outside = sorted((r for r in rows if r["size_pelas_horas"] != r["size"]),
                     key=lambda r: -abs(r["size_pelas_horas"] - r["size"]))
    return dict(por_size=groups, fora_da_faixa=outside, tarefas=len(rows))
