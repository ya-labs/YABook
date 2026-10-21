"""Recuperação progressiva: assuntos -> conhecimento -> experiências -> evidências."""
from .core import digest
from .search import search
from .sources import all_entries
from .views import PERSONAL, bounded, clip, compact, key, kind, on_this_machine, ordered


LEVELS = ("index", "knowledge", "evidence")
ENTITY_RECORDS = 2
TOPICS = 3
TOPIC_MEMBERS = 3
FOREIGN_AFTER = 3
SEARCH_BUDGET = 60000
QUERY_CHARS = 200
STRONG_SHARE = 0.75  # parcela dos termos da consulta exigida fora do projeto


def delivery_key(entry):
    return key(entry) + "@" + str(entry.get("revision"))


def covered(delivered, entry, level):
    """Nível entregue cobre os anteriores; índice não equivale a conhecimento."""
    levels = delivered.get(delivery_key(entry), ())
    return any(LEVELS.index(l) >= LEVELS.index(level) for l in levels if l in LEVELS)


def delivered_levels(result, evidence=False):
    """Níveis entregues por item, para o hook não reinjetar o mesmo conteúdo na sessão."""
    levels = {}
    for item in result.get("topics", []) + result.get("index", []) + result.get("conditional", []):
        levels.setdefault(delivery_key(item), set()).add("index")
    for item in result.get("knowledge", []) + result.get("experiences", []) + result.get("profile", []) + result.get("preferences", []):
        levels.setdefault(delivery_key(item), set()).add("evidence" if evidence else "knowledge")
    return levels


def strong_match(entry, query):
    """Fora do projeto exige mais termos da consulta no registro que dentro dele."""
    import math, re
    from .search import STOPWORDS, fold, text
    wanted = {fold(t) for t in re.findall(r"[\w-]+", query) if t.casefold() not in STOPWORDS}
    if len(wanted) < 2:
        return False
    found = sum(1 for t in wanted if re.search(r"\b" + re.escape(t) + r"\b", fold(text(entry))))
    return found >= min(4, max(2, math.ceil(len(wanted) * STRONG_SHARE)))


def other_projects(vault, query, includes, limit, model=None):
    """Registros próprios fora dos escopos da sessão que casam fortemente com a consulta."""
    from .core import scoped
    found = search(vault, query, (), limit=12, budget=SEARCH_BUDGET, level="knowledge", model=model, expand=False)["results"]
    result = []
    for entry in found:
        if entry["collection"] != "records" or entry.get("source", "own") != "own" or scoped(entry["scope"], includes):
            continue
        if kind(entry) in PERSONAL or not on_this_machine(entry) or not strong_match(entry, query):
            continue
        result.append(entry)
        if len(result) == limit: break
    return result


def retrieve(vault, query, includes=(), budget=6000, experiences=False, evidence=False, model=None, delivered=None,
             excerpt=None, other=0):
    """excerpt limita content/application por item (pistas do hook); show/retrieve aprofundam.
    other: quantos registros de outros projetos podem entrar, marcados com a origem."""
    if not 512 <= budget <= 100000: raise ValueError("Orçamento inválido")
    if evidence and not experiences: raise ValueError("Evidências exigem nível de experiência")
    entries = [e for e in all_entries(vault, includes) if on_this_machine(e)]
    by_key = {key(e): e for e in entries}
    # A busca devolve resultados completos (com evidências); com o orçamento das pistas
    # caberia só o primeiro candidato. O corte final por orçamento é feito abaixo.
    topics = search(vault, query, includes, budget=SEARCH_BUDGET, level="index", model=model, expand=False)
    knowledge = search(vault, query, includes, budget=SEARCH_BUDGET, level="knowledge", model=model, expand=False)
    # Só o que casou com a consulta, na ordem da busca. Entidade não tem conteúdo:
    # vale pelos registros que a citam. Perfil já chega no início da sessão.
    order = []
    def add(identifier):
        entry = by_key.get(identifier)
        if entry and identifier not in order and kind(entry) != "profile":
            order.append(identifier)
    for entry in knowledge["results"]:
        if entry["collection"] == "entities":
            citing = [e for e in entries if e["collection"] == "records" and entry["id"] in e.get("entities", [])
                      and e.get("source", "own") == entry.get("source", "own")]
            for record in ordered(citing)[:ENTITY_RECORDS]: add(key(record))
        else:
            add(key(entry))
    # Assunto que casou (apelido, gatilho) vale pelos seus registros, em número limitado.
    for found in (e for e in topics["results"] if e["collection"] == "groups"):
        group = by_key.get(key(found), found)  # resultado da busca vem sem a lista de membros
        namespace = group.get("source", "own") + ":"
        members = [by_key.get(namespace + m) for m in group.get("members", [])]
        for member in [m for m in members if m and m["collection"] == "records"][:TOPIC_MEMBERS]:
            add(key(member))
    # Outros projetos depois dos três primeiros do escopo da sessão (para não perderem
    # espaço no orçamento), poucos e com a origem marcada.
    foreign = []
    if other and includes:
        for entry in other_projects(vault, query, includes, other, model):
            if key(entry) not in order:
                by_key[key(entry)] = entry; foreign.append(key(entry))
        order[FOREIGN_AFTER:FOREIGN_AFTER] = foreign
    # No máximo um vizinho direto por item, logo após a origem para sobreviver ao
    # orçamento: a relação explícita mais próxima. Preferência condicional relacionada
    # vale como vizinho; perfil não (já chega no início da sessão).
    chosen = []
    for identifier in order:
        chosen.append(identifier)
        entry = by_key[identifier]
        namespace = entry.get("source", "own") + ":"
        for target in (namespace + r["target"] for r in entry.get("relations", []) if not r.get("suggested")):
            related = by_key.get(target)
            if related and related["collection"] == "records" and kind(related) != "profile" \
                    and target not in order and target not in chosen:
                chosen.append(target); break
    groups = [key(e) for e in topics["results"] if e["collection"] == "groups"]
    for identifier in order:
        entry = by_key[identifier]
        parents = [g for g in entries if g["collection"] == "groups" and entry["id"] in g.get("members", [])]
        if entry.get("parent"): parents += [by_key.get(entry.get("source", "own") + ":" + entry["parent"])]
        groups += [key(g) for g in parents if g]
    selected = chosen + list(dict.fromkeys(groups))[:TOPICS]
    if experiences:
        for entry in entries:
            if entry["collection"] == "episodes" and any(entry.get("source", "own") + ":" + r in selected for r in entry.get("learnings", [])):
                selected.append(key(entry))
    items = [by_key[i] for i in dict.fromkeys(selected) if i in by_key]
    def content(entry):
        fields = ("id", "revision", "source", "source_revision", "title", "scope", "kind", "state", "origin",
                  "content", "application", "conditions", "summary_stale", "authority", "activation", "triggers")
        if entry["collection"] == "episodes":
            fields += ("objective", "context", "actions", "outcome", "validation", "learnings")
        value = {k: entry[k] for k in fields if k in entry}
        if excerpt:
            # Pista compacta: identidade, revisão e o que aplicar; metadados ficam para show/retrieve.
            value = {k: v for k, v in value.items() if k in ("id", "revision", "title", "state", "content",
                     "application", "conditions", "objective", "outcome", "learnings")
                     or (k == "source" and v != "own")}
            if value.get("state") == "confirmed": value.pop("state")
            for field in ("content", "application", "conditions"):
                if isinstance(value.get(field), str) and len(value[field]) > excerpt:
                    value[field] = value[field][:excerpt].rsplit(" ", 1)[0] + "…"
        if key(entry) in foreign:
            value["project"] = " / ".join(entry["scope"][:2])  # pista de outro projeto
        if evidence and entry.get("evidence"): value["evidence"] = entry["evidence"]
        return value
    delivered = delivered or {}
    level = "evidence" if evidence else "knowledge"
    fresh = [e for e in items if not covered(delivered, e, "index" if e["collection"] == "groups" else level)]
    # A consulta volta resumida: o prompt inteiro (ex.: texto colado) estourava o orçamento.
    return bounded(dict(revision=digest(vault.snapshot()), query=clip(query, QUERY_CHARS),
                        degraded=topics["degraded"] or knowledge["degraded"],
                        already_delivered=len(items) - len(fresh),
                        # Conhecimento ocupa o orçamento antes do índice de assuntos.
                        knowledge=[content(e) for e in fresh if e["collection"] in ("records", "entities")],
                        topics=compact((e for e in fresh if e["collection"] == "groups"), summary=200),
                        experiences=[content(e) for e in fresh if e["collection"] == "episodes" and experiences]), budget)
