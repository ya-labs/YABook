"""Leitura da hierarquia épico > história > tarefa: herança de código e trabalho pessoal."""


def index_of(tasks):
    return {t["data"]["id"]: t["data"] for t in tasks}


def chain(data, index):
    """A própria tarefa seguida dos ancestrais, do pai ao épico."""
    result, seen, current = [], set(), data
    while current and current.get("id") not in seen:
        result.append(current)
        seen.add(current.get("id"))
        current = index.get(current.get("pai")) if current.get("pai") else None
    return result


def inherited(data, index, key):
    return next((d[key] for d in chain(data, index) if d.get(key)), None)


def personal(data, index):
    """`pessoal` marcado prevalece; sem marca, é pessoal o que não tem demanda nem projeto na cadeia."""
    if isinstance(data.get("pessoal"), bool):
        return data["pessoal"]
    if data.get("tipo") == "especificacao":
        return False
    return not any(d.get("demanda") or d.get("projeto") for d in chain(data, index))


def code(data, index):
    """Código exibido: demanda ou projeto da cadeia; sem eles, a issue (projeto pessoal não usa a numeração da empresa)."""
    value = inherited(data, index, "demanda") or inherited(data, index, "projeto")
    if value:
        return value
    issues = inherited(data, index, "issue")
    return issues[0] if issues else None
