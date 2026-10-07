"""FTS5 + embeddings Ollama opcionais + expansão de relações com orçamento."""
import json
import math
import re
import sqlite3
import urllib.request
from urllib.parse import urlparse
from .core import digest, read_json, write_json
from .sources import all_entries

PIPELINE = "yabook-text-v1"


def text(entry):
    return "\n".join(str(entry.get(k, "")) for k in ("title", "content", "application", "conditions", "summary",
                    "keywords", "aliases", "triggers", "objective", "context", "actions", "outcome", "validation"))


def uid(entry):
    return entry.get("source", "own") + ":" + entry["id"]


def vector_key(entry, model):
    return digest(dict(id=uid(entry), revision=entry.get("revision"), content_hash=digest(text(entry)),
                       model=model, pipeline=PIPELINE))


def valid_vector(value):
    return isinstance(value, list) and bool(value) and all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in value) and any(value)


def embed(texts, model, endpoint):
    parsed = urlparse(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1") or parsed.username or parsed.password:
        raise ValueError("Esta versão usa embeddings locais Ollama, sem enviar conhecimento a serviços externos")
    request = urllib.request.Request(endpoint, data=json.dumps({"model": model, "input": texts}).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as response:
        values = json.load(response)["embeddings"]
    if len(values) != len(texts) or not all(valid_vector(v) for v in values) or len({len(v) for v in values}) != 1:
        raise ValueError("Embeddings inválidos/incompatíveis")
    return values


def cosine(a, b):
    if len(a) != len(b): return -1
    return sum(x*y for x,y in zip(a,b)) / math.sqrt(sum(x*x for x in a)*sum(y*y for y in b))


def search(vault, query, includes=(), excludes=(), limit=8, budget=6000, model=None,
           endpoint="http://127.0.0.1:11434/api/embed", expand=True, kinds=(), level="all"):
    if not 1 <= limit <= 50 or budget < 256 or budget > 100000:
        raise ValueError("Limite/orçamento inválido")
    entries = all_entries(vault, includes, excludes)
    from .views import kind, references
    levels = {"index": {"groups"}, "knowledge": {"records", "entities"}, "experience": {"episodes"},
              "all": {"records", "entities", "groups", "episodes"}}
    if level not in levels: raise ValueError("Nível de recuperação inválido")
    # Relacionamentos só expandem dentro dos filtros de origem, escopo, tipo e nível.
    entries = [e for e in entries if e["collection"] in levels[level] and (not kinds or kind(e) in kinds)]
    by_id = {uid(e): e for e in entries}
    vault.local.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(vault.local / "search.sqlite")
    try:
        connection.execute("DROP TABLE IF EXISTS memory")
        connection.execute("CREATE VIRTUAL TABLE memory USING fts5(id UNINDEXED, body)")
        connection.executemany("INSERT INTO memory VALUES (?,?)", [(uid(e), text(e)) for e in entries])
        connection.commit()
        terms = re.findall(r"[\w-]+", query, flags=re.UNICODE)[:32]
        fts_query = " OR ".join('"'+term+'"' for term in terms)
        lexical = [row[0] for row in connection.execute("SELECT id FROM memory WHERE memory MATCH ? ORDER BY bm25(memory) LIMIT 50", (fts_query,))] if terms else []
    finally:
        connection.close()
    rankings = [lexical]; mode = "textual"; degraded = None
    if model and entries:
        path = vault.local / "vectors.json"
        cache = read_json(path) if path.exists() else {}
        keys = {uid(e): vector_key(e, model) for e in entries}
        try:
            missing = [e for e in entries if not valid_vector(cache.get(keys[uid(e)], {}).get("vector"))]
            # Pequenos lotes evitam requests com corpus inteiro.
            for offset in range(0, len(missing), 16):
                batch = missing[offset:offset+16]
                for entry, vector in zip(batch, embed([text(e) for e in batch], model, endpoint)):
                    cache[keys[uid(entry)]] = dict(id=uid(entry), revision=entry.get("revision"),
                        content_hash=digest(text(entry)), model=model, pipeline=PIPELINE, vector=vector)
            # Excluídos/retirados não ficam em índice compartilhado da consulta.
            cache = {key: cache[key] for key in keys.values() if key in cache}
            write_json(path, cache)
            query_vector = embed([query], model, endpoint)[0]
            compatible = [(uid(e), cosine(query_vector, cache[keys[uid(e)]]["vector"])) for e in entries]
            rankings.append([k for k,s in sorted(compatible, key=lambda x:x[1], reverse=True) if s > 0])
            mode = "hybrid"
        except (OSError, ValueError, KeyError):
            degraded = "Embeddings indisponíveis; busca textual preservada"
    scores = {}
    for ranking in rankings:
        for rank, key in enumerate(ranking): scores[key] = scores.get(key, 0) + 1/(60+rank+1)
    if expand:
        for key in list(scores):
            entry = by_id[key]; namespace = entry.get("source", "own") + ":"
            neighbors = references(entry)
            for target in neighbors:
                neighbor = namespace + target
                if neighbor in by_id: scores[neighbor] = max(scores.get(neighbor, 0), scores[key]*0.5)
    result = []
    for key in sorted(scores, key=lambda k:scores[k], reverse=True)[:limit]:
        e = by_id[key]
        hit = {k:e[k] for k in ("id", "revision", "title", "scope", "state", "kind", "collection", "parent", "keywords", "aliases", "triggers", "content", "application", "conditions", "evidence", "source", "source_revision", "origin", "origin_updates", "summary", "summary_stale", "objective", "context", "actions", "outcome", "validation", "learnings", "episodes") if k in e}
        hit.update(score=round(scores[key], 6), reason="Termos/significado e relações explícitas" if mode == "hybrid" else "Termos e relações explícitas")
        if len(json.dumps(result+[hit], ensure_ascii=False)) > budget:
            remaining = budget-len(json.dumps(result, ensure_ascii=False))-len(json.dumps({k:v for k,v in hit.items() if k not in ("content","evidence","summary")},ensure_ascii=False))-80
            if remaining < 100: break
            hit["content"] = str(hit.get("content", hit.get("summary", "")))[:remaining]
            hit.pop("summary",None); hit.pop("evidence",None); hit["truncated"] = True
            low, high = 0, len(hit["content"])
            content = hit["content"]
            while low < high:
                middle = (low + high + 1) // 2
                hit["content"] = content[:middle]
                if len(json.dumps(result+[hit],ensure_ascii=False)) <= budget: low = middle
                else: high = middle - 1
            hit["content"] = content[:low]
            if len(json.dumps(result+[hit],ensure_ascii=False)) > budget: break
        result.append(hit)
    return dict(mode=mode, level=level, degraded=degraded, results=result, characters=len(json.dumps(result,ensure_ascii=False)))


def export_vectors(vault, destination):
    package = dict(schema_version=1, pipeline=PIPELINE, vectors=read_json(vault.local / "vectors.json"))
    write_json(destination, package)
    return dict(exported=len(package["vectors"]), destination=str(destination))


def import_vectors(vault, package):
    if package.get("schema_version") != 1 or package.get("pipeline") != PIPELINE:
        raise ValueError("Pacote vetorial incompatível")
    entries = all_entries(vault); valid = {}
    for key, value in package["vectors"].items():
        match = next((e for e in entries if uid(e) == value.get("id")), None)
        if match and vector_key(match, value.get("model")) == key and valid_vector(value.get("vector")):
            valid[key] = value
    write_json(vault.local / "vectors.json", valid)
    return dict(accepted=len(valid), rejected=len(package["vectors"])-len(valid))
