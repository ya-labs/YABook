"""Recuperação progressiva: assuntos -> conhecimento -> experiências -> evidências."""
from .core import digest
from .search import search
from .sources import all_entries
from .views import bounded, key, overview, references


LEVELS = ("index", "knowledge", "evidence")


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
        levels.setdefault(item["key"] + "@" + str(item.get("revision")), set()).add("index")
    for item in result.get("knowledge", []) + result.get("experiences", []) + result.get("profile", []) + result.get("preferences", []):
        levels.setdefault(delivery_key(item), set()).add("evidence" if evidence else "knowledge")
    return levels


def retrieve(vault, query, includes=(), budget=6000, experiences=False, evidence=False, model=None, delivered=None):
    if not 512 <= budget <= 100000: raise ValueError("Orçamento inválido")
    if evidence and not experiences: raise ValueError("Evidências exigem nível de experiência")
    entries = all_entries(vault, includes)
    by_key = {key(e): e for e in entries}
    topics = search(vault, query, includes, budget=budget, level="index", model=model, expand=False)
    knowledge = search(vault, query, includes, budget=budget, level="knowledge", model=model, expand=False)
    selected = {key(e) for e in topics["results"] + knowledge["results"]}
    for entry in entries:
        namespace = entry.get("source", "own") + ":"
        if entry["collection"] == "groups" and any(namespace + member in selected for member in entry.get("members", [])):
            selected.add(key(entry))
    # A consulta lexical/vetorial também alcança um registro sem grupo, evitando
    # que uma classificação incompleta torne o conhecimento invisível.
    frontier = [(i, 0) for i in selected]
    while frontier:
        identifier, depth = frontier.pop()
        entry = by_key.get(identifier)
        if not entry: continue
        namespace = entry.get("source", "own") + ":"
        parent = entry.get("parent")
        if parent and namespace + parent in by_key: selected.add(namespace + parent)
        if depth >= 3: continue
        neighbors = [i for i in references(entry) if i != parent]
        if entry["collection"] == "groups":
            neighbors += [e["id"] for e in entries if e.get("source", "own") == entry.get("source", "own") and e.get("parent") == entry["id"]]
        for reference in neighbors:
            target = namespace + reference
            related = by_key.get(target)
            if related and target not in selected and (related["collection"] != "episodes" or experiences):
                selected.add(target); frontier.append((target, depth + 1))
    if experiences:
        for entry in entries:
            if entry["collection"] == "episodes" and any(entry.get("source", "own") + ":" + r in selected for r in entry.get("learnings", [])):
                selected.add(key(entry))
    items = [by_key[i] for i in selected if i in by_key]
    # Priorização determinística e sem promoção de hipóteses ou conteúdo externo.
    ranked = {key(e): i for i, e in enumerate(topics["results"] + knowledge["results"])}
    items.sort(key=lambda e: (ranked.get(key(e), 999), e["title"].casefold(), key(e)))
    def content(entry):
        fields = ("id", "revision", "source", "source_revision", "title", "scope", "kind", "state", "origin",
                  "content", "application", "conditions", "summary_stale", "authority", "activation", "triggers")
        if entry["collection"] == "episodes":
            fields += ("objective", "context", "actions", "outcome", "validation", "learnings")
        value = {k: entry[k] for k in fields if k in entry}
        if evidence and entry.get("evidence"): value["evidence"] = entry["evidence"]
        return value
    delivered = delivered or {}
    level = "evidence" if evidence else "knowledge"
    fresh = [e for e in items if not covered(delivered, e, "index" if e["collection"] == "groups" else level)]
    return bounded(dict(revision=digest(vault.snapshot()), query=query,
                        degraded=topics["degraded"] or knowledge["degraded"],
                        already_delivered=len(items) - len(fresh),
                        topics=overview(e for e in fresh if e["collection"] == "groups"),
                        knowledge=[content(e) for e in fresh if e["collection"] in ("records", "entities")],
                        experiences=[content(e) for e in fresh if e["collection"] == "episodes" and experiences]), budget)
