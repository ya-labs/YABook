"""Sumários e índices derivados; contexto compacto antes do conhecimento completo."""
import json
import os
import tempfile
from pathlib import Path

from .core import digest, snapshot_entries

KINDS = {"profile": "Perfil", "preference": "Preferências", "procedure": "Procedimentos",
         "knowledge": "Conhecimento", "project": "Projeto", "topic": "Assunto",
         "collection": "Grupo", "episodes": "Experiência", "entities": "Entidade"}
PERSONAL = ("profile", "preference")


def key(entry):
    return entry.get("source", "own") + ":" + entry["id"]


def kind(entry):
    return entry.get("kind", "knowledge") if entry["collection"] == "records" else entry.get("kind", entry["collection"])


def references(entry):
    result = entry.get("members", []) + entry.get("entities", []) + entry.get("episodes", []) + entry.get("learnings", [])
    result += [r["target"] for r in entry.get("relations", []) if not r.get("suggested")]
    if entry.get("parent"): result.append(entry["parent"])
    return list(dict.fromkeys(result))


def ordered(entries):
    return sorted(entries, key=lambda e: (e.get("state") != "confirmed", -int(e.get("priority", 0)),
                                         e["title"].casefold(), key(e)))


def overview(entries):
    """Índice filtrado antes de compor qualquer resumo; sem duplicar conteúdo."""
    index = []
    for entry in ordered(entries):
        item = {k: entry[k] for k in ("id", "title", "scope", "revision", "source", "state",
                "parent", "summary_stale", "keywords", "aliases", "triggers") if k in entry}
        item.update(kind=kind(entry), key=key(entry), references=references(entry))
        if entry.get("summary"): item["summary"] = entry["summary"]
        index.append(item)
    return index


def compact(entries, summary=0):
    """Uma linha por item: identidade e revisão para aprofundar, sem listas de membros/termos."""
    index = []
    for entry in ordered(entries):
        item = {"id": entry["id"], "revision": entry.get("revision"), "title": entry["title"], "kind": kind(entry)}
        if entry.get("source", "own") != "own": item["source"] = entry["source"]
        if entry.get("state", "confirmed") != "confirmed": item["state"] = entry["state"]
        if entry.get("summary_stale"): item["summary_stale"] = True
        if summary and entry.get("summary"):
            text = entry["summary"]
            item["summary"] = text if len(text) <= summary else text[:summary].rsplit(" ", 1)[0] + "…"
        index.append(item)
    return index


def bounded(value, budget):
    """JSON válido sob orçamento; descarta itens completos em vez de cortar bytes."""
    result = {k: ([] if isinstance(v, list) else v) for k, v in value.items()}
    result["truncated"] = False
    if len(json.dumps(result, ensure_ascii=False)) > budget:
        raise ValueError("Orçamento insuficiente para metadados")
    for field, items in value.items():
        if not isinstance(items, list): continue
        for item in items:
            candidate = dict(result, **{field: result[field] + [item]})
            if len(json.dumps(candidate, ensure_ascii=False)) <= budget:
                result = candidate
            else: result["truncated"] = True
    return result


def session_context(vault, scope=(), budget=4500):
    from .sources import all_entries
    scopes = [["Pessoa"]] + ([list(scope)] if scope else [])
    entries = all_entries(vault, scopes)
    active = [e for e in ordered(entries) if e["collection"] == "records" and e.get("source") == "own"
              and e.get("state") == "confirmed" and (kind(e) == "profile" or
              kind(e) == "preference" and e.get("authority") == "explicit" and e.get("activation") == "always")]
    brief = lambda e: {k: e[k] for k in ("id", "revision", "source", "title", "kind", "content", "application", "conditions") if k in e}
    # Tópicos do projeto configurado antes dos pessoais; índice compacto para caber no orçamento.
    own = lambda e: bool(scope) and e["scope"][:len(scope)] == list(scope)
    groups = [e for e in entries if e["collection"] == "groups"]
    topics = compact([e for e in groups if own(e)], summary=160) + compact([e for e in groups if not own(e)])
    conditional = [e for e in entries if kind(e) in ("preference", "procedure") and e not in active]
    return bounded(dict(revision=digest(vault.snapshot()), scope=list(scope),
                        profile=[brief(e) for e in active if kind(e) == "profile"],
                        preferences=[brief(e) for e in active if kind(e) == "preference"],
                        topics=topics, conditional=compact(conditional),
                        index=compact([e for e in entries if e["collection"] != "groups" and e not in active and e not in conditional])), budget)


def render_views(snapshot):
    entries = [e for e in snapshot_entries(snapshot) if e.get("state") not in ("archived", "superseded")]
    revision = digest(snapshot)
    header = f"<!-- YABOOK-VIEW:generated revision={revision} -->\n"
    summary = [header, "# Sumário da memória YABook", "\nVisão gerada. Os JSON canônicos e suas evidências sustentam o conteúdo."]
    for label, record_kind in (("Perfil", "profile"), ("Preferências", "preference"), ("Procedimentos", "procedure")):
        summary.append("\n## " + label)
        for entry in ordered(e for e in entries if kind(e) == record_kind):
            body = entry["content"] if entry.get("state") == "confirmed" and (record_kind == "profile" or entry.get("activation") == "always" and entry.get("authority") == "explicit") else "Consultar quando aplicável"
            summary.append(f"- [{entry['title']}](../records/{entry['id']}.json): {body[:500]} · {entry.get('state', 'hypothesis')} · revisão {entry['revision']}")
    summary.append("\n## O que existe na memória\n\nConsulte [o índice](MEMORY.md) por projeto, assunto, tipo e termos de busca.")
    projects = [e for e in entries if e["collection"] == "groups" and kind(e) == "project"]
    for entry in ordered(projects): summary.append(f"- [{entry['title']}](topics/{entry['id']}.md)")
    index = [header, "# Índice da memória YABook"]
    rendered = {}
    by_id = {e["id"]: e for e in entries}
    for scope in sorted({tuple(e["scope"]) for e in entries}):
        index.append("\n## " + " / ".join(scope))
        for entry in ordered(e for e in entries if tuple(e["scope"]) == scope):
            terms = ", ".join(entry.get("keywords", []) + entry.get("aliases", []) + entry.get("triggers", []))
            target = f"topics/{entry['id']}.md" if entry["collection"] == "groups" else f"../{entry['collection']}/{entry['id']}.json"
            index.append(f"- [{entry['title']}]({target}) · {KINDS.get(kind(entry), kind(entry))} · {entry.get('state', 'confirmed')} · revisão {entry['revision']}" + (f" · termos: {terms}" if terms else ""))
    for group in (e for e in entries if e["collection"] == "groups"):
        lines = [header, "# " + group["title"], "\nEscopo: " + " / ".join(group["scope"])]
        lines.append("\n" + group.get("summary", "Resumo precisa ser revisto." if group.get("summary_stale") else "Grupo sem resumo aprovado."))
        related = [by_id[i] for i in group.get("members", []) if i in by_id]
        related += [e for e in entries if e.get("parent") == group["id"] and e not in related]
        for entry in ordered(related):
            target = f"{entry['id']}.md" if entry["collection"] == "groups" else f"../../{entry['collection']}/{entry['id']}.json"
            lines.append(f"- [{entry['title']}]({target}) · revisão {entry['revision']}")
        lines.append("\nRevisões do resumo: " + json.dumps(group.get("summary_sources", {}), ensure_ascii=False, sort_keys=True))
        lines[0] = f"<!-- YABOOK-VIEW:generated revision={digest(dict(group=group, members=related))} -->\n"
        rendered["views/topics/" + group["id"] + ".md"] = "\n".join(lines) + "\n"
    rendered["views/memory_summary.md"] = "\n".join(summary) + "\n"
    rendered["views/MEMORY.md"] = "\n".join(index) + "\n"
    return rendered


def write_views(vault, snapshot):
    rendered = render_views(snapshot)
    changed = []
    directory = vault.root / "views"
    if directory.is_symlink() or (directory / "topics").is_symlink():
        raise ValueError("Symlink em visões derivadas")
    for relative, content in rendered.items():
        path = vault.root / relative
        if path.is_symlink(): raise ValueError("Symlink em visão derivada")
        if path.exists() and not path.read_text(encoding="utf-8").startswith("<!-- YABOOK-VIEW:generated "):
            raise ValueError("Arquivo independente em visões derivadas")
        if path.exists() and path.read_text(encoding="utf-8") == content: continue
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".writing-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream: stream.write(content)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)
        changed.append(relative)
    for path in (directory / "topics").glob("*.md"):
        relative = path.relative_to(vault.root).as_posix()
        if relative not in rendered:
            if path.is_symlink() or not path.read_text(encoding="utf-8").startswith("<!-- YABOOK-VIEW:generated "):
                raise ValueError("Arquivo independente em visões derivadas")
            path.unlink(); changed.append(relative)
    return changed
