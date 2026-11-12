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
    return not any(d.get("demanda") or d.get("projeto") for d in chain(data, index))


def own_code(data):
    """(tipo, código) do próprio nó: o do tipo dele; nos demais tipos, demanda e depois projeto."""
    if data.get("tipo") == "projeto" and data.get("projeto"):
        return "projeto", data["projeto"]
    if data.get("tipo") == "demanda" and data.get("demanda"):
        return "demanda", data["demanda"]
    if data.get("demanda"):
        return "demanda", data["demanda"]
    if data.get("projeto"):
        return "projeto", data["projeto"]
    return None


def mixed_code_warning(data):
    """Aviso (sem recusar) quando o tipo traz o código do outro tipo junto."""
    tipo, other = data.get("tipo"), {"projeto": "demanda", "demanda": "projeto"}.get(data.get("tipo"))
    if other and data.get(tipo) and data.get(other):
        return "%s: tipo %s com %s %s; o código exibido e da ficha será o %s %s" % (
            data.get("id") or data.get("titulo"), tipo, other, data[other], tipo, data[tipo])
    return None


def nearest_code(data, index):
    """(tipo, código) do nó mais próximo da cadeia que tem código: a própria tarefa, depois os ancestrais."""
    return next((c for c in (own_code(d) for d in chain(data, index)) if c), None)


def code(data, index):
    """Código exibido: o do próprio tipo, senão o do ancestral mais próximo; sem eles, a issue
    (projeto pessoal não usa a numeração da empresa)."""
    found = nearest_code(data, index)
    if found:
        return found[1]
    issues = inherited(data, index, "issue")
    return issues[0] if issues else None
